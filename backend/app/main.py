"""CurveLab API — FastAPI application factory.

Wires the routers under /api/v1, installs CORS for the configured frontend
origin, and renders every domain error as problem-JSON:

    {"type", "title", "detail", "field?", "offending_indices?"}
"""

from __future__ import annotations

import logging
import time
import uuid

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from fastapi.responses import JSONResponse

from app.api.routers import data, export, fit, meta
from app.core.config import get_settings
from app.core.errors import DomainError

logger = logging.getLogger("curvelab")
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")


def create_app() -> FastAPI:
    """Build and configure the FastAPI application."""
    settings = get_settings()
    app = FastAPI(
        title=settings.app_name,
        version=settings.version,
        docs_url="/api/docs",
        redoc_url="/api/redoc",
        openapi_url="/api/openapi.json",
    )

    app.add_middleware(GZipMiddleware, minimum_size=1024)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins,
        allow_methods=["GET", "POST"],
        allow_headers=["*"],
    )

    @app.middleware("http")
    async def request_context(request: Request, call_next):  # type: ignore[no-untyped-def]
        """Attach a request id and timing header to every response."""
        request_id = request.headers.get("X-Request-ID", str(uuid.uuid4()))
        start = time.perf_counter()
        response = await call_next(request)
        elapsed_ms = (time.perf_counter() - start) * 1000
        response.headers["X-Request-ID"] = request_id
        response.headers["X-Response-Time-ms"] = f"{elapsed_ms:.1f}"
        logger.info("%s %s -> %s (%.1f ms, %s)", request.method, request.url.path, response.status_code, elapsed_ms, request_id)
        return response

    @app.exception_handler(DomainError)
    async def domain_error_handler(_: Request, exc: DomainError) -> JSONResponse:
        """Render expected business failures as problem-JSON."""
        return JSONResponse(status_code=exc.status_code, content=exc.to_problem())

    @app.exception_handler(RequestValidationError)
    async def validation_error_handler(
        _: Request, exc: RequestValidationError
    ) -> JSONResponse:
        """Render schema validation failures in the same problem-JSON shape."""
        first = exc.errors()[0] if exc.errors() else {}
        loc = ".".join(str(part) for part in first.get("loc", []) if part != "body")
        return JSONResponse(
            status_code=422,
            content={
                "type": "validation_error",
                "title": "Invalid request",
                "detail": first.get("msg", "The request body failed validation."),
                "field": loc or None,
            },
        )

    app.include_router(meta.router, prefix="/api/v1")
    app.include_router(fit.router, prefix="/api/v1")
    app.include_router(data.router, prefix="/api/v1")
    app.include_router(export.router, prefix="/api/v1")

    return app


app = create_app()
