"""JSON export: the complete FitResult plus raw input and report metadata."""

from __future__ import annotations

import json

from app.engines.export.base import ExportedFile, ExportPayload, exporter


@exporter("json")
def build_json(payload: ExportPayload) -> ExportedFile:
    """Dump the full structured result (machine-readable, mirrors the API)."""
    document = {
        "meta": payload.meta.model_dump(),
        "input": {"x": payload.x, "y": payload.y},
        "result": json.loads(payload.fit.model_dump_json()),
    }
    return ExportedFile(
        json.dumps(document, indent=2).encode("utf-8"),
        "application/json",
        "json",
    )
