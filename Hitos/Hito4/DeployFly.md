Despliegue en Fly — Guía y evidencia

Esta guía explica cómo desplegar la aplicación en Fly (PaaS), cómo automatizar el despliegue desde GitHub Actions y qué evidencia generar para la entrega.

1) Requisitos locales
- Tener `flyctl` instalado y configurado: https://fly.io/docs/hands-on/install-flyctl/
- Tener acceso al repositorio y permisos para añadir secrets en GitHub.

2) Pasos para desplegar manualmente con `flyctl`

- Login en Fly (abrirá el navegador para autenticar):

```bash
flyctl auth login
```

- Crear la app (si no existe) y seleccionar región:

```bash
# crea la app con nombre <APP_NAME>
flyctl apps create <APP_NAME> --org personal --region ams
```

- Ajustar `fly.toml` si hace falta (ya existe en el repo); revisar `app` y `env`.

- Desplegar (desde la raíz del repo):

```bash
flyctl deploy --app <APP_NAME>
```

3) Recolectar evidencia (comandos y archivos que debes incluir en la entrega)

- Guardar la URL pública de la app (output de `flyctl status`):

```bash
flyctl status --app <APP_NAME> > evidence/fly_status.txt
```

- Comprobar endpoints básicos y guardar respuestas (por ejemplo `/ping` y `/metrics`):

```bash
curl -sS -L https://cc-benigno-parra.fly.dev/metrics | head -n 200 -o evidence/ping_response.txt
curl -sS https://cc-benigno-parra.fly.dev/metrics -o evidence/metrics_response.txt
```

- Recoger logs (últimos 10 minutos) y guardarlos:

```bash
flyctl logs --app cc-benigno-parra --since 10m > evidence/fly_logs.txt
```

- Tomar un *smoke-test* automático y guardar salida (ver `scripts/smoke_test.sh`).

- Ejecutar una prueba de carga (k6) contra la URL pública y guardar resultados (ver ejemplo abajo).

4) Integración continua (GitHub Actions) — plantilla

- Añade el secret `FLY_API_TOKEN` y `FLY_APP_NAME` en el repo (Settings → Secrets). La plantilla de workflow usa estos secrets.
- Workflow (archivo ejemplo en `.github/workflows/deploy-fly.yml`) construye y despliega la app con `flyctl`.

5) Ejemplo de `k6` rápido (local)

Instalar `k6` y ejecutar:

```bash
# ejemplo muy simple
K6_TARGET=cc-benigno-parra.fly.dev k6 run --out json=evidence/k6_results.json k6_simple.js
k6 run --out json=evidence/k6_results.json k6_simple.js
```

Luego incluye `results/k6_results.json` y un resumen en la evidencia.

6) Qué incluir en la entrega (lista final)
- `evidence/fly_status.txt` (salida de `flyctl status`)
- `evidence/ping_response.txt` y `evidence/metrics_response.txt`
- `evidence/fly_logs.txt`
- `evidence/k6_results.json` y un resumen (latencia media, p95, errores)
- Capturas de pantalla de Grafana mostrando `rate(http_requests_total[1m])` y otros dashboards.
- En el README/Hito: explicación paso a paso + comandos usados para generar la evidencia.

7) Notas y consideraciones
- Si usas GitHub Actions para deploy, añade el secret `FLY_API_TOKEN` y evita ponerlo en el repo.
- En la documentación justifica tu elección de Fly (facilidad con Docker, integración con GitHub Actions, free tier, gestión de secretos).

---
Si quieres, puedo añadir el workflow y los scripts que automatizan la recolección de evidencia al repo ahora.
