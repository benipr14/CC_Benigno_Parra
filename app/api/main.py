from fastapi import FastAPI, Request
import time
import logging
from fastapi import FastAPI, Request
import time
import logging
import os

from app.core.logging_config import setup_logging


# Prometheus metrics
from prometheus_client import Counter, Histogram, make_asgi_app


setup_logging()

app = FastAPI(title="MiMicroservicio")

# Initialize tracing if OTLP env vars are present
if os.getenv("OTEL_EXPORTER_OTLP_ENDPOINT") and os.getenv("OTEL_API_KEY"):
    try:
        from observability.telemetry import init_tracing

        init_tracing("cc-app")
        logging.getLogger("app").info("Tracing initialized via OTLP")
    except Exception as e:
        logging.getLogger("app").warning("Tracing not initialized: %s", e)


# Define Prometheus metrics
REQUESTS = Counter("http_requests_total", "Total HTTP requests", ["method", "path", "status"])
LATENCY = Histogram("http_request_latency_seconds", "Request latency seconds", ["method", "path"])


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Simple request logging middleware (console) and metrics.

    Logs: method, path, status code and duration in seconds.
    Also increments Prometheus counters and observes latency.
    """
    logger = logging.getLogger("app")
    start = time.time()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("Request error: %s %s", request.method, request.url.path)
        raise
    duration = time.time() - start
    status_code = getattr(response, "status_code", 500)
    logger.info("%s %s %s %.3fs", request.method, request.url.path, status_code, duration)

    # Update Prometheus metrics
    try:
        REQUESTS.labels(request.method, request.url.path, str(status_code)).inc()
        LATENCY.labels(request.method, request.url.path).observe(duration)
    except Exception:
        # don't let metrics failures affect the response
        logger.debug("Failed to update metrics")

    return response


@app.get("/ping")
def ping():
    return {"msg": "pong"}

# include routers
from app.api.routers.usuarios import router as usuarios_router
from app.api.routers.partidos import router as partidos_router
from app.api.routers.apuestas import router as apuestas_router

app.include_router(usuarios_router)
app.include_router(partidos_router)
app.include_router(apuestas_router)

# Expose Prometheus metrics at /metrics
app.mount("/metrics", make_asgi_app())

