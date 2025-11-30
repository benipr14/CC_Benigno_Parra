# Configuración y justificación de los contenedores

A continuación se documenta la configuración y la justificación de diseño de cada contenedor que compone el clúster.

## Contenedor de aplicación (`app1`, `app2`, `app3`)

- Imagen base: `python:3.11-slim`.
  - Justificación: ofrece una imagen oficial de CPython con tamaño reducido (slim), compatibilidad total con la aplicación FastAPI y disponibilidad de paquetes necesarios vía `pip`. Es adecuada para entornos de desarrollo y despliegue ligeros y permite instalar dependencias de forma reproducible.

- Instalación de dependencias:
  - Se usa `requirements-dev.txt` y `pip install --no-cache-dir -r requirements-dev.txt` (según `Dockerfile`). Justificación: reusar `requirements-dev.txt` asegura que las mismas dependencias que se usan en desarrollo y pruebas se instalen en la imagen, lo que facilita reproducibilidad y evita divergencias entre entornos.

- Variables de entorno en imagen:
  - `PYTHONDONTWRITEBYTECODE=1` y `PIP_NO_CACHE_DIR=1` (definidas en el `Dockerfile`) reducen artefactos en la imagen y evitan caching innecesario de pip.

- Estructura y ejecución:
  - `WORKDIR /app`, copia del código fuente en `/app`, `EXPOSE 8000` y `CMD` ejecutando `uvicorn app.api.main:app --host 0.0.0.0 --port 8000`.
  - Justificación: esta configuración simple arranca la aplicación FastAPI de forma predecible y expone el puerto estándar interno `8000`.

- Volumen y configuración en `compose.yaml`:
  - Cada réplica monta el volumen nombrado `app_data` en `/app/data` para compartir datos no transaccionales (logs, artefactos de prueba, etc.).
  - Se define una variable `INSTANCE` diferente por réplica para distinguir instancias durante pruebas.


## Contenedor de datos (`data`)

- Imagen base: `busybox:1.36` (servicio `data` en `compose.yaml`).
  - Justificación: `busybox` es una imagen mínima y portable ideal para contenedores cuyo único propósito es poseer un volumen o ejecutar comandos triviales. Es liviana y reduce la superficie de vulnerabilidad.

- Rol y configuración:
  - El contenedor `data` monta el volumen nombrado `app_data:/app/data` y ejecuta un comando simple (`sleep` en `compose.yaml`) para mantenerse activo y conservar la propiedad del volumen.
  - Justificación: separar la propiedad del volumen en un contenedor facilita demostrar persistencia compartida sin introducir servicios de almacenamiento adicionales.

- Limitaciones:
  - El contenedor de datos solo es adecuado para demostrar persistencia y compartir ficheros entre réplicas; no sustituye a una base de datos o a un almacenamiento de producción.

## Comportamiento orquestado (justificación de configuración conjunta)

- `depends_on: [data]` en las réplicas garantiza que el contenedor de datos esté creado antes de que las aplicaciones intenten montar el volumen. Justificación: evita condiciones de carrera al arrancar el stack en pruebas locales.

- Mapear puertos diferentes por réplica (8000, 8001, 8002) simplifica pruebas puntuales e inspección directa de cada instancia sin necesidad de un balanceador. Justificación: en la práctica formativa es preferible poder acceder a cada réplica individualmente para verificar comportamiento y logs.

