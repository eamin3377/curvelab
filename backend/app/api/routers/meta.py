"""Operational endpoints: health check and version info."""

from __future__ import annotations

from fastapi import APIRouter

from app.core.config import get_settings

router = APIRouter(tags=["meta"])


@router.get("/health")
def health() -> dict[str, str]:
    """Liveness probe used by Docker HEALTHCHECK and uptime monitors."""
    return {"status": "ok"}


@router.get("/version")
def version() -> dict[str, str]:
    """Return the running API name and version."""
    settings = get_settings()
    return {"name": settings.app_name, "version": settings.version}
