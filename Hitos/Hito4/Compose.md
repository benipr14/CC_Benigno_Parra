# Documentación breve de `compose.yaml`

Este fichero describe el stack usado para la práctica: una unidad de datos y tres réplicas de la aplicación.

Servicios principales

- `data`:
  - Imagen: `busybox:1.36`.
  - Rol: contenedor "data-only" que posee el volumen `app_data` montado en `/app/data`.
  - Comportamiento: ejecuta un comando simple (`sleep`) para permanecer vivo y conservar la propiedad del volumen.

- `app1`, `app2`, `app3`:
  - Construcción: cada réplica se construye desde el `Dockerfile` del repo (`build.context: .`).
  - Dependencias: `depends_on: [data]` — garantiza que el volumen exista antes de montar.
  - Volumen: montan el volumen nombrado `app_data` en `/app/data` para compartir datos no transaccionales.
  - Puertos: mapean `8000:8000`, `8001:8000`, `8002:8000` respectivamente para permitir pruebas directas a cada instancia.
  - Variable: `INSTANCE` se define por réplica para facilitar la distinción en logs/pruebas.

Volúmenes

- `app_data`: volumen nombrado (driver `local`) usado para persistencia simple y para demostrar compartición entre réplicas.

Decisiones clave

- Separar un contenedor de datos permite demostrar persistencia compartida sin añadir almacenamiento externo.
- Usar tres réplicas muestra escalado horizontal básico; mapear puertos distintos facilita pruebas manuales y automáticas.
- `depends_on` evita condiciones de carrera al arrancar el stack en pruebas locales.

Uso mínimo para levantar el stack (local):

```bash
docker compose -f compose.yaml up --build
```

Para bajar y borrar volúmenes:

```bash
docker compose -f compose.yaml down -v
```
