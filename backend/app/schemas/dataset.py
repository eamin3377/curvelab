"""Dataset-related request/response schemas."""

from __future__ import annotations

from pydantic import BaseModel, Field


class CleaningReport(BaseModel):
    """Summary of every automatic cleaning action applied to a dataset."""

    duplicates_removed: int = 0
    empty_dropped: int = 0
    non_numeric_dropped: int = 0


class ParsedDataset(BaseModel):
    """Result of parsing pasted text or an uploaded file."""

    x: list[float]
    y: list[float]
    n: int
    cleaning_report: CleaningReport


class ParseTextRequest(BaseModel):
    """Raw pasted text (CSV/TSV/whitespace separated, two columns)."""

    text: str = Field(..., min_length=1, max_length=20_000_000)
    remove_duplicates: bool = True


class SampleSummary(BaseModel):
    """Sample dataset metadata for the listing endpoint."""

    id: str
    name: str
    description: str
    model: str
    n: int


class SampleDataset(BaseModel):
    """A full sample dataset including its points."""

    id: str
    name: str
    description: str
    model: str
    x: list[float]
    y: list[float]
