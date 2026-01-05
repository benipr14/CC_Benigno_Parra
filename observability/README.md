Observability templates for Grafana Cloud
--------------------------------------

Files in this folder:
- `grafana-agent.yaml`: Grafana Agent / Prometheus configuration template.
- `telemetry.py`: Minimal OpenTelemetry initializer (OTLP/HTTP) used to send traces.

What you already found
- Prometheus remote_write endpoint: `https://prometheus-prod-65-prod-eu-west-2.grafana.net/api/prom/push`

Secrets / environment variables to create
- `GRAFANA_API_KEY` : API key for Grafana Cloud used for Prometheus remote_write (recommended role: "MetricsPublisher").
- `OTEL_EXPORTER_OTLP_ENDPOINT` : OTLP HTTP endpoint for Grafana Cloud (found in Grafana Cloud "Integrations" / "APIs" dashboard).
- `OTEL_API_KEY` : API key for traces (Grafana Cloud API key with appropriate ingestion permissions).

How to create the Grafana API key
1. Sign in to Grafana Cloud and open the "Grafana Cloud" portal for your stack.
2. In the left menu, go to "Stack" -> "Settings" -> "API Keys" (or "Configuration"/"API Keys").
3. Create a new API key:
   - Name: `cc-grafana-agent`
   - Role: `MetricsPublisher` (for remote_write) and/or `Editor`/custom for traces depending on your stack.
4. Copy the API key value — you will not be able to see it again.

Add secrets to GitHub repository
1. Go to your GitHub repo -> Settings -> Secrets -> Actions -> New repository secret.
2. Add the following secrets:
   - `GRAFANA_REMOTE_WRITE_URL` : `https://prometheus-prod-65-prod-eu-west-2.grafana.net/api/prom/push`
   - `GRAFANA_API_KEY` : (the API key value you created)
   - `OTEL_EXPORTER_OTLP_ENDPOINT` : (Grafana OTLP endpoint)
   - `OTEL_API_KEY` : (API key for traces)

Using the templates
- Grafana Agent (local): run the grafana-agent container and mount `grafana-agent.yaml`. Pass `GRAFANA_API_KEY` as an env var so the basic_auth password is set.
- Telemetry (app): install `opentelemetry-sdk` and `opentelemetry-exporter-otlp` and then import and call `observability.telemetry.init_tracing("cc-app")` early in `app/api/main.py` when the OTLP env vars are present.

Example: local docker run (replace with your orchestration)
```
docker run -e GRAFANA_API_KEY=<<your_key>> -v $(pwd)/grafana-agent.yaml:/etc/agent/grafana-agent.yaml grafana/agent:latest --config.file=/etc/agent/grafana-agent.yaml
```

Next steps I can help with
- Add `observability` deployment to the Compose stack or create a Fly app for the Grafana Agent and wire secrets into the Fly deploy workflow.
- Integrate `observability.telemetry.init_tracing()` into `app/api/main.py` behind a feature flag or env var.

Local Prometheus + Grafana (quick setup)
---------------------------------------
If you prefer not to use Grafana Cloud, you can run Prometheus and Grafana locally to visualise metrics and collect evidence for the assignment.

Files added:
- `observability/prometheus.yml` : Prometheus scrape config (scrapes the 3 local app instances).
- `observability/docker-compose.observability.yml` : Docker Compose file to run Prometheus and Grafana.
- `observability/grafana/provisioning/datasources/datasource.yml` : Grafana provisioning that sets Prometheus as default datasource.

Quick start (from the repo root):
1. Ensure your app replicas are running via your existing `docker compose up` (so ports 8000,8001,8002 are mapped).
2. Start Prometheus + Grafana:

```bash
docker compose -f observability/docker-compose.observability.yml up -d
```

3. Open Grafana at `http://localhost:3000` (default user `admin`; password `admin` as set by the compose file).
4. In Grafana -> Explore run the query:

```
rate(http_requests_total[1m])
```

Notes and troubleshooting:
- If Grafana shows no data, ensure Prometheus is scraping the right host IP. On Linux the Docker host gateway is usually `172.17.0.1`. If you used Docker Desktop (mac/Windows) replace targets in `observability/prometheus.yml` with `host.docker.internal:8000,...`.
- To stop the observability stack:

```bash
docker compose -f observability/docker-compose.observability.yml down
```

Evidence to include in your submission:
- Screenshot of Grafana Explore or a dashboard showing `rate(http_requests_total[1m])` or `histogram_quantile(0.95, ...)`.
- `observability/prometheus.yml` file in the repo.
- `docker compose -f observability/docker-compose.observability.yml ps` output showing Prometheus and Grafana running.

