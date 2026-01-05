# Descripción y justificación de la configuración para el despliegue automático

El objetivo de este archivo es describir la configuración propuesta para automatizar el despliegue de la aplicación desde el repositorio de GitHub hacia la plataforma PaaS seleccionada (Fly). Incluirá el flujo CI que construye y publica la imagen, las variables y secretos necesarios, y las opciones para realizar el despliegue evitando la cola del builder remoto.

Resumen del flujo recomendado
-
1. GitHub Actions: al hacer `push` a `main` se ejecuta un pipeline que:
   - Ejecuta pruebas (unitarias y/o de integración básicas).
   - Construye la imagen Docker usando `docker buildx`.
   - Etiqueta la imagen con `ghcr.io/<owner>/<repo>:<tag>` y la publica en GHCR.
2. Despliegue: una vez publicada la imagen, el pipeline invoca `flyctl deploy --image <ghcr...>` para desplegar una imagen ya construida (evita usar el builder remoto de Fly y la cola asociada).
3. Verificación: tras el despliegue se ejecuta script de comprobación y se recogen evidencias (`scripts/collect_fly_evidence.sh`).

Secrets y variables necesarias
-
- `FLY_API_TOKEN`: token de la cuenta de Fly para autenticar `flyctl` desde CI (si se usa `flyctl` en CI).
- `FLY_APP_NAME`: nombre de la aplicación en Fly.
- `GITHUB_TOKEN`: token automático disponible en Actions, útil para operaciones con GHCR si la política del repositorio lo permite.

Ejemplo de workflow (GitHub Actions)
-
El siguiente ejemplo ilustra un workflow completo: construir → publicar imagen → desplegar → smoke tests. Ajusta los pasos según necesidades y secretos disponibles.

```yaml
name: CI / Build / Publish / Deploy

on:
  push:
    branches: [ main ]
  workflow_dispatch: {}

jobs:
  build-and-push:
    runs-on: ubuntu-latest
    outputs:
      image: ${{ steps.build.outputs.image }}
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Set up QEMU and docker buildx
        uses: docker/setup-buildx-action@v2

      - name: Log in to GHCR
        uses: docker/login-action@v2
        with:
          registry: ghcr.io
          username: ${{ github.actor }}
          password: ${{ secrets.GHCR_TOKEN || github.token }}

      - name: Build and push image
        id: build
        uses: docker/build-push-action@v4
        with:
          context: '.'
          push: true
          tags: ghcr.io/${{ github.repository_owner }}/myapp:${{ github.sha }}
        
      - name: Set output image
        run: echo "image=ghcr.io/${{ github.repository_owner }}/myapp:${{ github.sha }}" >> $GITHUB_OUTPUT

  deploy:
    needs: build-and-push
    runs-on: ubuntu-latest
    steps:
      - name: Checkout
        uses: actions/checkout@v4

      - name: Install flyctl
        run: |
          curl -L https://fly.io/install.sh | sh
          echo "$HOME/.fly/bin" >> $GITHUB_PATH

      - name: Login to Fly
        env:
          FLY_API_TOKEN: ${{ secrets.FLY_API_TOKEN }}
        run: flyctl auth login --access-token "$FLY_API_TOKEN"

      - name: Deploy (from GHCR image)
        env:
          IMAGE: ${{ needs.build-and-push.outputs.image }}
        run: |
          # deploy using the pre-built image to avoid remote builder queue
          flyctl deploy --app "${{ secrets.FLY_APP_NAME }}" --image "$IMAGE"

      - name: Smoke tests (inline)
        run: |
          # simple health checks without external script
          APP_HOST="${{ secrets.FLY_APP_NAME }}.fly.dev"
          echo "Checking https://${APP_HOST}/ping"
          curl -sSf "https://${APP_HOST}/ping" || (echo "ping failed" && exit 1)
          echo "Fetching metrics (first 50 lines)"
          curl -sS "https://${APP_HOST}/metrics" | head -n 50 || true

      - name: Collect evidence
        run: |
          bash scripts/collect_fly_evidence.sh "${{ secrets.FLY_APP_NAME }}"
```