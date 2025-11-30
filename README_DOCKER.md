# Ejecutar con Docker Compose

Este proyecto contiene un fichero de Docker Compose `compose.yaml` y un `Dockerfile` para construir la imagen de la aplicación.

Resumen de lo añadido:

- `Dockerfile`: construye una imagen de Python (3.11-slim), instala `requirements-dev.txt` y ejecuta `uvicorn app.deps:app`.
- `compose.yaml`: define un servicio `data` (contenedor de datos) y tres réplicas `app1`, `app2` y `app3` que comparten el volumen `app_data` proporcionado por `data`. También mapea los puertos 8000, 8001 y 8002 del host a cada réplica.

Cómo usarlo (requiere Docker y Docker Compose):

1) Construir y arrancar el stack en primer plano:

```bash
docker compose -f compose.yaml up --build
```

2) Acceder a la API desde el host:

- `http://localhost:8000/ping` -> app1
- `http://localhost:8001/ping` -> app2
- `http://localhost:8002/ping` -> app3

3) Detener y eliminar contenedores/volúmenes:

```bash
docker compose -f compose.yaml down -v
```

Notas importantes:

- Para demostrar el uso de un contenedor de datos, `compose.yaml` crea el servicio `data` basado en `busybox` que monta el volumen `app_data`. Las réplicas montan el mismo volumen en `/app/data`.
- La configuración está hecha con ficheros (`Dockerfile`, `compose.yaml`) y variables de entorno para permitir reproducibilidad.
