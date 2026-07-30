"""Data ingestion endpoints: text/file parsing and sample datasets."""

from __future__ import annotations

from fastapi import APIRouter, UploadFile

from app.core.config import get_settings
from app.core.errors import DatasetValidationError, FileParseError
from app.schemas.dataset import (
    ParsedDataset,
    ParseTextRequest,
    SampleDataset,
    SampleSummary,
)
from app.services import data_service
from app.core.constants import get_sample, list_samples

router = APIRouter(prefix="/data", tags=["data"])


@router.post(
    "/parse-text",
    response_model=ParsedDataset,
    summary="Parse pasted text into a dataset",
)
def parse_text(request: ParseTextRequest) -> ParsedDataset:
    """Parse two-column pasted text (Excel/CSV/whitespace) into x/y arrays,
    reporting every cleaning action applied."""
    return data_service.parse_text(request.text, request.remove_duplicates)


@router.post(
    "/parse-file",
    response_model=ParsedDataset,
    summary="Parse an uploaded CSV / TXT / JSON file",
)
async def parse_file(file: UploadFile) -> ParsedDataset:
    """Parse an uploaded data file. The payload is processed fully in
    memory and never written to disk; size is capped by configuration."""
    settings = get_settings()
    content = await file.read()
    if not data_service.buffer_size_ok(content, settings.max_upload_mb):
        raise DatasetValidationError(
            title="File too large",
            detail=f"Uploads are limited to {settings.max_upload_mb} MB.",
            field="file",
        )
    if not file.filename:
        raise FileParseError(title="Missing filename", detail="The upload has no filename.")
    return data_service.parse_upload(file.filename, content)


@router.get(
    "/samples",
    response_model=list[SampleSummary],
    summary="List built-in sample datasets",
)
def samples() -> list[SampleSummary]:
    """Return metadata for the demo datasets (without the point arrays)."""
    return list_samples()  # type: ignore[return-value]


@router.get(
    "/samples/{sample_id}",
    response_model=SampleDataset,
    summary="Get one full sample dataset",
)
def sample(sample_id: str) -> SampleDataset:
    """Return a complete sample dataset, including x and y arrays."""
    ds = get_sample(sample_id)
    if ds is None:
        raise DatasetValidationError(
            title="Unknown sample dataset",
            detail=f"No sample dataset with id '{sample_id}'.",
        )
    return ds  # type: ignore[return-value]
