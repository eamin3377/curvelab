"""Dataset ingestion: cleaning, validation and text/file parsing.

The cleaning pipeline is deliberately transparent — every dropped or
modified row is counted in a :class:`CleaningReport` that is shown to the
user (\"2 duplicates removed · 1 invalid row dropped\").
"""

from __future__ import annotations

import io
import json
import re

import numpy as np

from app.core.errors import DatasetValidationError, FileParseError
from app.schemas.dataset import CleaningReport, ParsedDataset

_SPLIT_RE = re.compile(r"[\t,;]+|\s+")


def clean_arrays(
    x: list[float],
    y: list[float],
    remove_duplicates: bool = True,
) -> tuple[np.ndarray, np.ndarray, CleaningReport]:
    """Validate and clean raw x/y lists into float64 arrays.

    Drops pairs containing NaN/inf, optionally removes duplicate (x, y)
    pairs, and enforces the minimum size of two distinct points.

    Args:
        x, y: Raw values (already length-checked by the schema).
        remove_duplicates: When True, exact duplicate pairs are dropped.

    Returns:
        (x_array, y_array, cleaning_report).

    Raises:
        DatasetValidationError: When fewer than 2 usable points remain.
    """
    xa = np.asarray(x, dtype=np.float64)
    ya = np.asarray(y, dtype=np.float64)
    report = CleaningReport()

    finite = np.isfinite(xa) & np.isfinite(ya)
    report.empty_dropped = int(len(xa) - np.count_nonzero(finite))
    xa, ya = xa[finite], ya[finite]

    if remove_duplicates and len(xa) > 1:
        _, unique_idx = np.unique(
            np.column_stack([xa, ya]), axis=0, return_index=True
        )
        unique_idx.sort()
        report.duplicates_removed = int(len(xa) - len(unique_idx))
        xa, ya = xa[unique_idx], ya[unique_idx]

    if len(xa) < 2:
        raise DatasetValidationError(
            title="Not enough usable data points",
            detail="At least 2 valid (x, y) pairs are required after cleaning.",
            field="x",
        )
    return xa, ya, report


def parse_text(text: str, remove_duplicates: bool = True) -> ParsedDataset:
    """Parse pasted text into a dataset.

    Accepts two numeric columns separated by tabs, commas, semicolons or
    whitespace — exactly what a copy from Excel or a CSV produces. Lines
    that do not yield two finite numbers are counted and skipped.

    Raises:
        FileParseError: When no valid rows are found at all.
    """
    xs: list[float] = []
    ys: list[float] = []
    skipped = 0

    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        cells = [c for c in _SPLIT_RE.split(line) if c != ""]
        if len(cells) < 2:
            skipped += 1
            continue
        try:
            xs.append(float(cells[0]))
            ys.append(float(cells[1]))
        except ValueError:
            skipped += 1

    if not xs:
        raise FileParseError(
            title="No numeric rows found",
            detail="Expected two numeric columns per line (e.g. \"1, 2.9\").",
        )

    xa, ya, report = clean_arrays(xs, ys, remove_duplicates)
    report.non_numeric_dropped += skipped
    return ParsedDataset(
        x=xa.tolist(), y=ya.tolist(), n=len(xa), cleaning_report=report
    )


def parse_upload(
    filename: str, content: bytes, remove_duplicates: bool = True
) -> ParsedDataset:
    """Parse an uploaded CSV / TXT / JSON file into a dataset.

    JSON files may be ``{"x": [...], "y": [...]}`` or ``[[x, y], ...]``.
    CSV and TXT are decoded as UTF-8 and parsed like pasted text.
    Binary spreadsheets (xlsx) are intentionally rejected with a clear
    message until the Excel engine ships.

    Raises:
        FileParseError: On unsupported extensions, decode failures, or
            malformed content.
    """
    name = filename.lower()
    if name.endswith((".xlsx", ".xls")):
        raise FileParseError(
            title="Excel files are not supported yet",
            detail="Please save the sheet as CSV and upload that instead.",
        )

    if name.endswith(".json"):
        try:
            payload = json.loads(content.decode("utf-8"))
        except (UnicodeDecodeError, json.JSONDecodeError) as exc:
            raise FileParseError(
                title="Invalid JSON file", detail=f"Could not parse the file: {exc}"
            ) from exc
        return _dataset_from_json(payload, remove_duplicates)

    try:
        text = content.decode("utf-8-sig")
    except UnicodeDecodeError as exc:
        raise FileParseError(
            title="Unsupported file encoding",
            detail="Please upload a UTF-8 encoded text file.",
        ) from exc
    return parse_text(text, remove_duplicates)


def _dataset_from_json(payload: object, remove_duplicates: bool) -> ParsedDataset:
    """Convert a decoded JSON payload into a ParsedDataset."""
    xs: list[float] = []
    ys: list[float] = []
    try:
        if isinstance(payload, dict) and "x" in payload and "y" in payload:
            xs = [float(v) for v in payload["x"]]  # type: ignore[union-attr]
            ys = [float(v) for v in payload["y"]]  # type: ignore[union-attr]
        elif isinstance(payload, list):
            for row in payload:
                xs.append(float(row[0]))  # type: ignore[index]
                ys.append(float(row[1]))  # type: ignore[index]
        else:
            raise TypeError("unexpected shape")
    except (TypeError, ValueError, IndexError) as exc:
        raise FileParseError(
            title="Unsupported JSON shape",
            detail='Expected {"x": [...], "y": [...]} or [[x, y], ...].',
        ) from exc

    if len(xs) != len(ys):
        raise FileParseError(
            title="Mismatched column lengths",
            detail=f"x has {len(xs)} values but y has {len(ys)}.",
        )
    xa, ya, report = clean_arrays(xs, ys, remove_duplicates)
    return ParsedDataset(
        x=xa.tolist(), y=ya.tolist(), n=len(xa), cleaning_report=report
    )


def validate_for_model(
    xa: np.ndarray, model: str, degree: int
) -> None:
    """Enforce model-specific dataset requirements before fitting.

    Args:
        xa: Cleaned x array (used to detect the all-equal-x singular case).
        model: 'linear' | 'polynomial' | 'exponential'.
        degree: Polynomial degree (ignored for other models).

    Raises:
        DatasetValidationError: On insufficient points or constant x.
        NonPositiveYValuesError: Never raised here — see fitting_service,
            which checks y so it can report exact row indices.
    """
    if model == "polynomial" and len(xa) <= degree:
        raise DatasetValidationError(
            title="Not enough points for this degree",
            detail=(
                f"A degree-{degree} polynomial needs at least {degree + 1} points; "
                f"the dataset has {len(xa)}. Lower the degree or add data."
            ),
            field="degree",
        )
    if float(np.ptp(xa)) == 0.0:
        raise DatasetValidationError(
            title="All x values are identical",
            detail=(
                "Curve fitting requires at least two distinct x values; "
                "with constant x the normal equations are singular."
            ),
            field="x",
        )


def buffer_size_ok(content: bytes, max_mb: int) -> bool:
    """Return True when an uploaded payload respects the size limit."""
    return len(content) <= max_mb * 1024 * 1024


def text_to_io(text: str) -> io.StringIO:
    """Wrap text in a StringIO (helper for future pandas-based parsers)."""
    return io.StringIO(text)
