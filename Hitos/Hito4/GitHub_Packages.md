# Publicación en GitHub Packages (GHCR) y actualizaciones automáticas

Este documento describe cómo se publican correctamente las imágenes de los microservicios en GitHub Container Registry (GHCR) desde la pipeline CI del repositorio y cómo se configuran las actualizaciones automáticas (builds al hacer push/PR).

## Resumen del flujo usado en este repositorio
- El workflow `CI` define un job `build-and-push` que:
  1. Hace checkout del código.
  2. Configura Buildx (`docker/setup-buildx-action`).
  3. Se autentica en GHCR usando `docker/login-action` con `registry: ghcr.io` y `password: ${{ secrets.GITHUB_TOKEN }}`.
  4. Construye y publica la imagen con `docker/build-push-action`, etiquetando `:latest` y `:${{ github.sha }}` y empujando al registro `ghcr.io/benipr14/cc_benigno_parra`.

Esta configuración garantiza que en cada `push` (o `pull_request`) en `main` se construyan y publiquen imágenes nuevas automáticamente.

## Requisitos y permisos
- En el workflow se configuran permisos mínimos:
  - `contents: read`, `packages: write`, `id-token: write`.
  - `packages: write` permite al `GITHUB_TOKEN` empujar imágenes a GHCR durante la ejecución del workflow.

- Para usuarios que publiquen manualmente desde su máquina local:
  - Pueden usar un token personal (`PAT`) con el scope `write:packages` y autenticarse con:

```bash
echo $PAT | docker login ghcr.io -u <github-username> --password-stdin
```

## Etiquetado y trazabilidad
- Etiquetas usadas en CI:
  - `ghcr.io/benipr14/cc_benigno_parra:latest` — etiqueta flotante útil para despliegues que siempre usan la última versión publicada.
  - `ghcr.io/benipr14/cc_benigno_parra:${{ github.sha }}` — etiqueta inmutable con el SHA del commit, imprescindible para trazabilidad y reproducibilidad.

## Verificación de que la imagen fue publicada
- Interfaz web: ir a `https://github.com/benipr14/CC_Benigno_Parra/packages` según la visibilidad; ahí aparecerán los paquetes/containers.
- CLI `gh`: usar `gh` para listar paquetes (requiere login con `gh auth login`):

```bash
gh api -H "Accept: application/vnd.github.v3+json" /user/packages/container --paginate
```

- Probar descarga local: después de login (`docker login ghcr.io`), hacer:

```bash
docker pull ghcr.io/benipr14/cc_benigno_parra:<sha>
docker run --rm -p 8000:8000 ghcr.io/benipr14/cc_benigno_parra:<sha>
```

## Actualizaciones automáticas (triggers y prácticas)
- Triggers: el workflow está configurado con `on: push` y `on: pull_request` hacia `main`. Esto provoca builds y publicaciones en cada push/PR que afecte a `main`.

- Buenas prácticas para evitar publicaciones no deseadas:
  - Limitar branches que disparan publicación (`branches: [ main ]`) — ya aplicado.
  - Si se desea publicar desde otras ramas, configurar jobs condicionales o añadir `if: github.ref == 'refs/heads/main'` en el job de publicación.

- Control de versiones: incluir un job adicional que cree releases (GitHub Release) y publique imágenes sólo cuando se crea una release, si quieres controlar cuándo las imágenes llegan a `latest` o a canales de producción.

## Seguridad y visibilidad del paquete
- Visibilidad: las imágenes publicadas en GHCR pueden ser públicas o privadas. Por defecto, las imágenes del repositorio son accesibles según permisos del repositorio/organización. Puedes ajustar la visibilidad en la sección Packages del repositorio en GitHub.

- Tokens y secretos:
  - Usar `secrets.GITHUB_TOKEN` en Actions es la forma más segura y ya configurada; evita exponer PATs cuando no son necesarios.
  - Para acciones que ejecutan fuera de Actions (por ejemplo, scripts locales), usar un PAT con scope `write:packages` y almacenarlo de forma segura en el runner o CI.

## Limpieza y retención de imágenes
- GHCR no limpia automáticamente versiones antiguas: considerar crear un job programado que elimine tags antiguos (por fecha o por número de versiones) si el repositorio genera muchas imágenes.

Ejemplo de estrategia simple: conservar las últimas N etiquetas semánticas y eliminar `:latest` y tags SHA más antiguos.

## Cómo probar localmente el pipeline (resumen)
1. Clonar el repositorio.
2. Construir localmente: `docker build -t local-cc:latest .`.

```bash
echo $PAT | docker login ghcr.io -u <usuario> --password-stdin
docker tag local-cc:latest ghcr.io/<usuario>/cc_benigno_parra:localtest
docker push ghcr.io/<usuario>/cc_benigno_parra:localtest
```
