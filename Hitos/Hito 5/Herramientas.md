# Descripción y justificación de las herramientas para el despliegue

Este documento describe y justifica las herramientas utilizadas para construir, publicar y desplegar la aplicación en la plataforma PaaS seleccionada (Fly). Se explica por qué se eligieron cada una, qué papel desempeñan en el flujo (local → CI → registro de contenedores → despliegue), y notas prácticas para su configuración segura y reproducible.

Herramientas principales
- **Docker / Dockerfile**: se usa para empaquetar la aplicación y sus dependencias en una imagen reproducible. Justificación: proporciona un artefacto idéntico en local, CI y en el PaaS, simplificando debugging y garantizando que el entorno de ejecución sea consistente.

- **GitHub Container Registry (GHCR)**: registry para publicar imágenes construidas en CI. Justificación: permite desacoplar la construcción de la plataforma de despliegue —la imagen se construye en GH Actions y luego puede ser desplegada por `flyctl` usando `--image`— evitando esperas de builders remotos y mejorando la trazabilidad (tags y versiones).

- **GitHub Actions**: flujo de CI para construir, testear y opcionalmente publicar la imagen en GHCR. Justificación: integración nativa con el repositorio, permite ejecutar pruebas automatizadas y generar artefactos (imágenes) como paso previo al despliegue. Las acciones proveen entornos reproducibles y runners gestionados.

- **flyctl**: CLI oficial de Fly que permite autenticarse, desplegar (`flyctl deploy`) y consultar estado/logs. Justificación: es la herramienta recomendada para interactuar con Fly, y facilita recuperar evidencia (status, logs, endpoints) mediante scripts (`collect_fly_evidence.sh`) y para despliegues tanto remotos como mediante `--image`.

- **scripts/collect_fly_evidence.sh**: script auxiliar incluido en el repo para comprobar salud (endpoints `/ping`, `/metrics`) y recolectar logs/estado/endpoint después del despliegue. Justificación: automatiza la recolección de artefactos (salidas) que sirven como evidencia para la entrega y facilitan validaciones manuales o automáticas.

Herramientas de apoyo y observabilidad (resumen)
- **Prometheus + Grafana (local)**: se usan para almacenar y visualizar métricas durante pruebas locales y en entornos compuestos por Docker Compose. Justificación: ofrecen métricas detalladas y dashboards para evaluar comportamiento y rendimiento antes o en paralelo al despliegue en Fly.

- **OpenTelemetry / OTLP**: ayuda a propagar trazas y métricas a backends compatibles (por ejemplo Grafana Cloud). Justificación: proporciona contexto distribuido y trazas cuando se integra con una recolección remota.

Notas prácticas para reproducibilidad
-
- Para una entrega reproducible y evitar bloqueos del builder remoto, el pipeline recomendado es:
  1. GitHub Actions: ejecutar tests unitarios, construir imagen Docker, etiquetar y publicar en GHCR.
  2. Despliegue: usar `flyctl deploy --image <ghcr.io/owner/repo:tag>` para despliegues deterministas.

- Para pruebas locales y recolección de métricas: usar `docker compose -f compose.yaml up --build` y abrir Prometheus/Grafana locales.

Referencias rápidas
- `scripts/collect_fly_evidence.sh` — script para recoger `flyctl status`, `flyctl logs` y endpoints.
- `k6_simple.js` — script de k6 para pruebas de carga contra el dominio público.
