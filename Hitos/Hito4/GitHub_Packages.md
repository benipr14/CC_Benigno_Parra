# Publicación en GitHub Packages (GHCR) y actualizaciones automáticas

Este documento describe cómo se publican correctamente las imágenes de los microservicios en GitHub Container Registry (GHCR) desde la pipeline CI del repositorio y cómo se configuran las actualizaciones automáticas (builds al hacer push/PR).

## Resumen del flujo usado en este repositorio
- El workflow `CI` define un job `build-and-push` que:
  1. Hace checkout del código.
  2. Configura Buildx (`docker/setup-buildx-action`).
  3. Se autentica en GHCR usando `docker/login-action` con `registry: ghcr.io` y `password: ${{ secrets.GITHUB_TOKEN }}`.
  4. Construye y publica la imagen con `docker/build-push-action`, etiquetando `:latest` y `:${{ github.sha }}` y empujando al registro `ghcr.io/benipr14/cc_benigno_parra`.

Esta configuración garantiza que en cada `push` (o `pull_request`) en `main` se construyan y publiquen imágenes nuevas automáticamente.

## Etiquetado y trazabilidad
- Etiquetas usadas en CI:
  - `ghcr.io/benipr14/cc_benigno_parra:latest` — etiqueta flotante útil para despliegues que siempre usan la última versión publicada.
  - `ghcr.io/benipr14/cc_benigno_parra:${{ github.sha }}` — etiqueta inmutable con el SHA del commit, imprescindible para trazabilidad y reproducibilidad.

## Verificación de que la imagen fue publicada
- Interfaz web: ir a `https://github.com/benipr14/CC_Benigno_Parra/packages`, ahí aparecerán los containers.

- Probar descarga local: después de login (`docker login ghcr.io`), hacer:

```bash
docker pull ghcr.io/benipr14/cc_benigno_parra:<sha>
docker run --rm -p 8000:8000 ghcr.io/benipr14/cc_benigno_parra:<sha>
```

## Actualizaciones automáticas (triggers y prácticas)
- Triggers: el workflow está configurado con `on: push` y `on: pull_request` hacia `main`. Esto provoca builds y publicaciones en cada push/PR que afecte a `main`.

## Cómo probar localmente el pipeline (resumen)
1. Clonar el repositorio.
2. Construir localmente: `docker build -t local-cc:latest .`.

```bash
echo $PAT | docker login ghcr.io -u <usuario> --password-stdin
docker tag local-cc:latest ghcr.io/<usuario>/cc_benigno_parra:localtest
docker push ghcr.io/<usuario>/cc_benigno_parra:localtest
```
