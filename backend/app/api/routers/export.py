"""Export endpoint: POST /api/v1/export/{format} → downloadable file."""

from __future__ import annotations

from fastapi import APIRouter, Response

from app.schemas.export import ExportRequest
from app.services import export_service

router = APIRouter(tags=["export"])


@router.post(
    "/export/{fmt}",
    summary="Export the fit as a downloadable file",
    responses={200: {"content": {"application/octet-stream": {}}}},
)
def export(fmt: str, request: ExportRequest) -> Response:
    """Generate CSV, JSON, TXT, XLSX, PDF or DOCX for the given fit.

    The fit is recomputed server-side; document formats embed the chart
    PNG captured from the on-screen graph when provided.
    """
    file, filename = export_service.run_export(fmt.lower(), request)
    return Response(
        content=file.content,
        media_type=file.media_type,
        headers={"Content-Disposition": f'attachment; filename="{filename}"'},
    )
