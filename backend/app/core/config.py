"""Application configuration, driven by environment variables.

Defaults target local development (frontend on http://localhost:5173).
Override any field via a ``.env`` file or real environment variables,
e.g. ``CURVELAB_CORS_ORIGINS='["https://curvelab.example.com"]'``.
"""

from __future__ import annotations

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime settings for the CurveLab API."""

    model_config = SettingsConfigDict(env_prefix="CURVELAB_", env_file=".env")

    app_name: str = "CurveLab API"
    version: str = "0.1.0"
    environment: str = "development"
    cors_origins: list[str] = ["http://localhost:5173", "http://127.0.0.1:5173"]

    max_points: int = 50_000
    min_points_linear: int = 2
    max_polynomial_degree: int = 6
    min_polynomial_degree: int = 2
    default_precision: int = 4
    min_precision: int = 2
    max_precision: int = 8

    max_upload_mb: int = 10


def get_settings() -> Settings:
    """Return a Settings instance (injected into routers via Depends)."""
    return Settings()
