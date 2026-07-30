"""Shared exporter plumbing.

Every exporter turns one canonical :class:`ExportPayload` (raw data + the
full FitResult + report metadata + optional chart PNG) into an
:class:`ExportedFile` (bytes + media type). New formats register
themselves in ``EXPORTERS`` at the bottom of this module's siblings.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from app.schemas.export import ReportMeta
from app.schemas.fit import FitResult


@dataclass
class ExportPayload:
    """Everything an exporter needs to build its document."""

    fit: FitResult
    x: list[float]
    y: list[float]
    meta: ReportMeta
    chart_png: bytes | None


@dataclass
class ExportedFile:
    """A rendered export ready to stream to the client."""

    content: bytes
    media_type: str
    extension: str


# format -> builder(payload). Populated by the sibling modules' imports in
# app.services.export_service so this registry never holds a stale entry.
EXPORTERS: dict[str, Callable[[ExportPayload], ExportedFile]] = {}


def exporter(fmt: str) -> Callable[[Callable[[ExportPayload], ExportedFile]], Callable[[ExportPayload], ExportedFile]]:
    """Decorator registering a builder function under a format name."""
    def register(fn: Callable[[ExportPayload], ExportedFile]) -> Callable[[ExportPayload], ExportedFile]:
        EXPORTERS[fmt] = fn
        return fn

    return register


def escape_csv_cell(value: object) -> str:
    """Neutralize spreadsheet formula injection (cells starting with =+-@)."""
    text = str(value)
    if text[:1] in ("=", "+", "-", "@"):
        return "'" + text
    return text


def fmt_num(value: float, precision: int = 6) -> str:
    """Consistent number formatting across all text-based exporters."""
    if value != 0.0 and (abs(value) >= 1e9 or abs(value) < 1e-6):
        return f"{value:.{precision}e}"
    return f"{value:.{precision}f}".rstrip("0").rstrip(".") if "." in f"{value:.{precision}f}" else f"{value:.{precision}f}"
