"""Export request schemas."""

from __future__ import annotations

import base64
import binascii
from datetime import date

from pydantic import BaseModel, Field, field_validator

from app.schemas.fit import FitRequest

PNG_SIGNATURE = b"\x89PNG\r\n\x1a\n"


class ReportMeta(BaseModel):
    """User-supplied report header fields for PDF/DOCX/XLSX documents."""

    title: str = Field(default="Curve Fitting Report", max_length=120)
    author: str = Field(default="", max_length=120)
    student_id: str = Field(default="", max_length=60)
    course: str = Field(default="Numerical Methods", max_length=120)
    institution: str = Field(default="", max_length=160)
    date: str = Field(default_factory=lambda: date.today().isoformat())


class ExportRequest(BaseModel):
    """Request body for POST /api/v1/export/{format}.

    The fit is recomputed server-side from ``fit_request`` so the exported
    document always matches the mathematical truth, and an optional chart
    PNG (captured from the on-screen Plotly chart) is embedded into the
    document formats.
    """

    fit_request: FitRequest
    report_meta: ReportMeta = ReportMeta()
    chart_png_base64: str | None = Field(default=None, max_length=15_000_000)

    @field_validator("chart_png_base64")
    @classmethod
    def validate_png(cls, value: str | None) -> str | None:
        """Ensure the embedded chart really decodes to a PNG image."""
        if value is None:
            return None
        try:
            raw = base64.b64decode(value, validate=True)
        except (binascii.Error, ValueError) as exc:
            raise ValueError("chart_png_base64 is not valid base64") from exc
        if not raw.startswith(PNG_SIGNATURE):
            raise ValueError("chart image must be a PNG")
        return value

    def chart_bytes(self) -> bytes | None:
        """Decode the embedded chart PNG, if present."""
        if self.chart_png_base64 is None:
            return None
        return base64.b64decode(self.chart_png_base64)
