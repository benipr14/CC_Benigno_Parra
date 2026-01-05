# Descripción y justificación de la elección de IaaS/PaaS

Para desplegar y operar la aplicación se valoraron tanto plataformas PaaS (Platform as a Service) como opciones más IaaS (Infrastructure as a Service). Tras analizar criterios técnicos, operativos y académicos, se optó por centrar la integración en un servicio PaaS (Fly) para las fases de demostración y despliegue sencillo, manteniendo la posibilidad de publicar imágenes en GHCR y ejecutar despliegues manuales o en CI en caso de necesitar más control.

Criterios considerados
-
- **Facilidad de uso y velocidad de despliegue:** se priorizó una plataforma que permita pasar de código a servicio con el mínimo número de pasos, para obtener evidencia reproducible (estado, logs, endpoints).
- **Integración con CI/CD y repositorios:** capacidad para integrarse con GitHub Actions y/o poder desplegar usando una imagen de contenedor desde GHCR.
- **Coste y disponibilidad educativa:** se consideraron plataformas con plan gratuito suficiente para pruebas y demostraciones, evitando soluciones con coste elevado.
- **Control y trazabilidad:** posibilidad de obtener logs, status y endpoints de la aplicación de forma automática para recopilar evidencia (scripts `collect_fly_evidence.sh`).
- **Simplicidad de red y DNS:** configuración sencilla de dominio/host público para ejecutar pruebas de carga (k6) y capturar métricas accesibles públicamente.

Opciones valoradas
-
- **Fly (PaaS)** — ventajas: despliegue directo desde Dockerfile, soporte de deploy remoto, integración con `flyctl`, dominio automático `*.fly.dev`, y planes gratuitos para prototipos y demostraciones. Inconvenientes: ocasionalmente la cola del builder remoto puede provocar esperas; la autenticación en CI requiere manejo de tokens con cuidado.
- **Render / Railway / Heroku (PaaS)** — ventajas: similares a Fly en facilidad de uso y despliegue; integración con GitHub. Inconvenientes: límites en el plan gratuito, diferencias en la gestión de builds y en la disponibilidad de logs, y en algunos casos la necesidad de adaptar Dockerfile o buildpacks.
- **GitHub Pages / Netlify (estático) + Backend en serverless (Cloud Functions)** — ventaja: muy económico para frontend estático; inconveniente: el proyecto es una API/servicio con estado que requiere contenedores o procesos persistentes, por lo que estas opciones no encajan directamente.
- **IaaS tradicional (DigitalOcean droplets, AWS EC2, GCP Compute Engine)** — ventaja: control total sobre la máquina y red; inconveniente: mayor complejidad operativa (configuración, seguridad, mantenimiento) y más tiempo invertido para obtener la misma evidencia que un PaaS.
- **Kubernetes en la nube (EKS/GKE/AKS)** — ventaja: orquestación y escalado profesionales; inconveniente: sobreingeniería para el alcance del proyecto y coste/tiempo de configuración significativo.

Justificación final
-
Para los objetivos del proyecto (entregable reproducible, demostraciones, evidencia —logs, endpoints, métricas— y facilidad para ejecutar pruebas de carga), la opción PaaS es la más adecuada por su rapidez de despliegue y baja fricción operativa. Entre las PaaS evaluadas, Fly ofreció un buen equilibrio: despliegues con Dockerfile sin cambios sustanciales, dominio público automático para pruebas de k6, y una CLI (`flyctl`) que facilita recoger evidencia. Por eso en las etapas de despliegue y pruebas se configuraron scripts y flujos pensados para Fly, manteniendo alternativas (publicar en GHCR y desplegar la imagen en otra plataforma o ejecutar localmente) para evitar bloqueos si el builder remoto o la autenticación fallan.

