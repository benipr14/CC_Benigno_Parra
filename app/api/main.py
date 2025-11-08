from fastapi import FastAPI, Request
import time
import logging

from app.core.logging_config import setup_logging

setup_logging()

app = FastAPI(title="MiMicroservicio")


@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Simple request logging middleware (console).

    Logs: method, path, status code and duration in seconds.
    """
    logger = logging.getLogger("app")
    start = time.time()
    try:
        response = await call_next(request)
    except Exception:
        logger.exception("Request error: %s %s", request.method, request.url.path)
        raise
    duration = time.time() - start
    logger.info("%s %s %s %.3fs", request.method, request.url.path, response.status_code, duration)
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
