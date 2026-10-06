import logging
import os
import time
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from typing import Any

from app.api.v1 import analytics, auth, data, predictions, users
from app.core.error_middleware import add_error_handlers
from app.core.security import validate_security_settings
from app.db.database import init_db
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    validate_security_settings()
    init_db()
    logger.info("Application startup complete.")
    yield
    logger.info("Application shutdown.")


app = FastAPI(
    title="Fluxora API",
    description="API for energy data management and prediction.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

_raw_origins = os.getenv(
    "CORS_ORIGINS", "http://localhost,http://localhost:3000,http://localhost:5173"
)
origins = [o.strip() for o in _raw_origins.split(",") if o.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

add_error_handlers(app)


@app.middleware("http")
async def log_requests(request: Request, call_next: Any) -> Any:
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start
    logger.info(
        "%s %s -> %s (%.3fs)",
        request.method,
        request.url.path,
        response.status_code,
        duration,
    )
    return response


app.include_router(auth.router, prefix="/v1")
app.include_router(data.router, prefix="/v1")
app.include_router(analytics.router, prefix="/v1")
app.include_router(predictions.router, prefix="/v1")
app.include_router(users.router, prefix="/v1")


@app.get("/health", tags=["system"])
def health_check() -> Any:
    return {"status": "ok"}


@app.get("/", tags=["system"])
def root() -> Any:
    return {"message": "Fluxora API", "version": "1.0.0", "docs": "/docs"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=os.getenv("API_HOST", "0.0.0.0"),
        port=int(os.getenv("API_PORT", "8000")),
        workers=int(os.getenv("API_WORKERS", "1")),
        reload=os.getenv("ENV", "development") == "development",
    )
