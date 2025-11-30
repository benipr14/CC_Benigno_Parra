# Documentación del `Dockerfile`

Este documento describe la configuración del `Dockerfile` usado para construir las imágenes de los microservicios (las tres réplicas `app1/app2/app3`) y justifica las decisiones principales.

## Resumen breve
- Base: `python:3.11-slim` — imagen oficial de CPython, ligera y compatible con la aplicación FastAPI.
- Dependencias: se instalan desde `requirements-dev.txt` con `pip --no-cache-dir` para reproducibilidad.
- Ejecutable: `uvicorn app.api.main:app --host 0.0.0.0 --port 8000`.

## Línea por línea — decisiones y justificación

- `FROM python:3.11-slim`
	- Justificación: proporciona un runtime Python oficial y mantenido, con menor tamaño que las imágenes completas. Permite instalar paquetes nativos si fuese necesario. Elegir `3.11` asegura compatibilidad con las dependencias modernas y mejor rendimiento que versiones previas.

- `ENV PYTHONDONTWRITEBYTECODE=1 PIP_NO_CACHE_DIR=1`
	- Justificación: evita generar ficheros .pyc en la imagen y evita cache de pip en la capa de imagen, manteniendo las imágenes más limpias y pequeñas.

- `WORKDIR /app` y `COPY . /app`
	- Justificación: establece un directorio de trabajo estándar donde reside el código; copiar todo el proyecto permite que la imagen contenga la aplicación completa. Para producción puede considerarse copiar solo los ficheros necesarios (o usar multistage builds) para reducir tamaño.

- `COPY requirements-dev.txt ./` y `RUN pip install --upgrade pip && pip install --no-cache-dir -r requirements-dev.txt`
	- Justificación: instalar dependencias declaradas garantiza que la imagen tenga todas las librerías necesarias. Reusar `requirements-dev.txt` sincroniza el entorno de desarrollo y el de contenedor, facilitando reproducibilidad de tests y ejecución. Nota: en producción se recomienda separar dependencias de desarrollo y de producción y fijar versiones explícitas.

- `EXPOSE 8000`
	- Justificación: documenta el puerto interno que usa la aplicación (uvicorn por defecto en 8000). En Compose se mapearán puertos distintos por réplica para pruebas.

- `CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]`
	- Justificación: arranca el servidor ASGI (Uvicorn) exponiendo la aplicación FastAPI. Ejecutar el proceso principal en primer plano facilita la integración con Docker y la orquestación.
