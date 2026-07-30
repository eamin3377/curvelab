"""Export orchestration: recompute the fit, dispatch to the right exporter."""

from __future__ import annotations

from datetime import datetime

from app.core.errors import DomainError
from app.engines.export import EXPORTERS, ExportedFile, ExportPayload

# Importing the modules registers their builders in EXPORTERS.
from app.engines.export import (  # noqa: F401
    csv_exporter,
    docx_exporter,
    excel_exporter,
    json_exporter,
    pdf_exporter,
    txt_exporter,
)
from app.schemas.export import ExportRequest
from app.services import fitting_service

SUPPORTED_FORMATS = tuple(sorted(EXPORTERS.keys()))


def _normalize_png(raw: bytes) -> bytes:
    """Re-encode a chart PNG as clean RGB.

    Browsers occasionally emit PNG variants (indexed/16-bit/alpha streams)
    that ReportLab or Pillow trips over; a decode→RGB→re-encode pass makes
    the bytes safe for every document exporter.
    """
    import io

    from PIL import Image

    img = Image.open(io.BytesIO(raw))
    if img.mode != "RGB":
        img = img.convert("RGB")
    out = io.BytesIO()
    img.save(out, format="PNG")
    return out.getvalue()


class UnknownFormatError(DomainError):
    """Requested export format is not registered."""

    status_code = 400
    error_type = "unknown_export_format"


def run_export(fmt: str, request: ExportRequest) -> tuple[ExportedFile, str]:
    """Build an export file and its download filename.

    The fit is recomputed from the raw request data so an exported
    document always reflects verified server-side computation.

    Args:
        fmt: One of ``SUPPORTED_FORMATS``.
        request: Fit request + report metadata + optional chart PNG.

    Returns:
        (exported file, download filename like
        ``curvelab_linear_2026-07-30_021530.pdf``).

    Raises:
        UnknownFormatError: For unregistered formats.
    """
    builder = EXPORTERS.get(fmt)
    if builder is None:
        raise UnknownFormatError(
            title="Unknown export format",
            detail=f"Supported formats: {', '.join(SUPPORTED_FORMATS)}.",
        )

    fit = fitting_service.run_fit(request.fit_request)
    chart = request.chart_bytes()
    payload = ExportPayload(
        fit=fit,
        x=list(request.fit_request.x),
        y=list(request.fit_request.y),
        meta=request.report_meta,
        chart_png=_normalize_png(chart) if chart else None,
    )
    file = builder(payload)
    stamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    filename = f"curvelab_{fit.model.value}_{stamp}.{file.extension}"
    return file, filename
