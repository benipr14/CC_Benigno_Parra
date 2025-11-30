# Test de integración: validación del clúster de contenedores

Este documento describe la implementación y la forma correcta de ejecutar el test que valida el funcionamiento del clúster de contenedores (`tests/test_compose_integration.py`). Contiene una explicación del contenido del test, cómo ejecutarlo localmente y qué comprobar en caso de fallos.

## Qué hace el test

- Construye y levanta el stack definido en `compose.yaml` usando `docker compose -f compose.yaml up --build -d`.
- Espera a que cada réplica responda en `/ping` en los puertos `8000`, `8001` y `8002`.
- Comprueba que la respuesta JSON contenga `{"msg": "pong"}` en cada réplica.
- Al finalizar (éxito o fallo), hace un `docker compose -f compose.yaml down -v` para limpiar contenedores y volúmenes.

## Implementación (resumen del código)

- El test está marcado con `@pytest.mark.integration`.
- Antes de arrancar comprueba dos condiciones para no fallar en entornos sin Docker:
  - Existe la CLI `docker` en `PATH`.
  - `docker info` devuelve código de salida 0 (permite detectar permisos insuficientes o ausencia del daemon).
- Para cada puerto se llama a `wait_for_url(url, timeout=60)` que reintenta conectarse hasta que la URL devuelve 200 OK o hasta agotarse el timeout.

## Ejecutar el test localmente

Requisitos previos:

- Docker y Docker Compose instalados y accesibles en la sesión (`docker` en `PATH`).
- Permisos para usar Docker (usuario en grupo `docker` o usar `sudo` cuando sea necesario).

Comandos para ejecutar el test localmente (desde la raíz del repo):

```bash
# (opcional) activar virtualenv si usas uno
python -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements-dev.txt

# Ejecutar solo el test de integración
.venv/bin/python -m pytest -q tests/test_compose_integration.py -k integration
```

Nota: el test usará el `docker` del host; si tu usuario no tiene permisos, puedes ejecutar el proceso con `sudo`, por ejemplo usar `sudo pytest ...`, aunque es preferible añadir el usuario al grupo `docker`.

## Comprobación y solución de problemas comunes

- Error: "docker CLI not found on PATH"
  - Solución: instalar Docker o asegurarse de que el ejecutable `docker` está en `PATH`.

- Error: test saltado por `docker info` (permiso denegado / daemon no disponible)
  - Solución: arrancar el servicio docker (`sudo systemctl start docker`) o ajustar permisos (añadir usuario al grupo `docker` y volver a iniciar sesión).

- Timeout esperando `/ping` en alguna réplica
  - Posibles causas: la imagen no se construyó correctamente, la aplicación no arranca por errores en dependencias, o el contenedor está fallando al iniciar.
  - Comprobaciones:
    - Ejecuta `docker compose -f compose.yaml logs --no-color` para ver logs de todos los servicios.
    - Ejecuta `docker compose -f compose.yaml ps` para ver el estado de los contenedores.
    - Intenta levantar manualmente con `docker compose -f compose.yaml up --build` y observa la salida.

- Error al limpiar volúmenes/contenedores al final
  - El test hace limpieza "best-effort" en `finally`; si quedan recursos, puedes ejecutar manualmente:

```bash
docker compose -f compose.yaml down -v
docker ps -a    # para inspeccionar contenedores pendientes
docker volume ls # para inspeccionar volúmenes
```

## Ejecución en CI

- En el workflow `CI` del repositorio el job `integration` depende de `build-and-push` (para garantizar que las imágenes estén disponibles si se usan). El job ejecuta `docker compose -f compose.yaml up --build -d`, espera las réplicas con un bucle `curl` y ejecuta las pruebas de integración con `pytest` dentro del runner.
- Recomendación: asegurarse de que el runner dispone de Docker y permisos (en `ubuntu-latest` de GitHub Actions esto ya funciona con las acciones usadas en este repo).

## Nota final

Este documento describe únicamente la implementación y la ejecución correcta del test de integración que valida el clúster de contenedores. Si quieres, puedo:

- Añadir un script helper `scripts/run_integration.sh` que ejecute los pasos de setup, test y teardown de forma automática.
- Añadir comprobaciones adicionales en el test (por ejemplo, validar headers, latencia, o endpoints adicionales).
