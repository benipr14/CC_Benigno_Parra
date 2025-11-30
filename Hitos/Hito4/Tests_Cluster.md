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

## Qué comprueba el test

El test no solo arranca el stack: realiza las siguientes comprobaciones concretas (las que hacen que la prueba pase o falle):

- Presencia de la CLI `docker` en `PATH`.
- Capacidad de comunicarse con el daemon Docker: `docker info` debe devolver código de salida 0 (esto detecta si el daemon está encendido y el usuario tiene permisos).
- `docker compose up --build -d` debe completarse sin errores al lanzar el stack.
- Cada réplica debe responder sobre HTTP 200 en su endpoint `/ping` (se comprueba para `localhost:8000`, `localhost:8001` y `localhost:8002`).
- El cuerpo de la respuesta JSON de cada réplica debe contener exactamente la clave/valor esperado: `{"msg": "pong"}`.
- Al finalizar (éxito o fallo) se intenta limpiar con `docker compose down -v` para eliminar contenedores y volúmenes.

Si alguna de estas comprobaciones falla, el test registra el fallo y el job devuelve error; los pasos de troubleshooting en la sección siguiente indican cómo recopilar logs y diagnosticar la causa.

## Ejecutar el test mediante `Makefile`

Requisitos previos:

- Docker y Docker Compose instalados y accesibles en la sesión (`docker` en `PATH`).
- Permisos para usar Docker (usuario en grupo `docker` o usar `sudo` cuando sea necesario).

El repositorio incluye un `Makefile` con un objetivo específico para este caso: `test-integration-compose`.

Pasos recomendados desde la raíz del repositorio:

```bash
# Crear e instalar dependencias en el virtualenv local (si no está hecho)
make install

# Ejecutar el test de integración que levanta el cluster (usa .venv/bin/python internamente)
make test-integration-compose
```

Detalles: el objetivo `test-integration-compose` ejecuta:

```
.venv/bin/python -m pytest -q tests/test_compose_integration.py
```

Ese pytest invoca `docker compose -f compose.yaml up --build -d` internamente (desde el propio test) y, al terminar, realiza el `down -v` de limpieza en el bloque `finally`.
