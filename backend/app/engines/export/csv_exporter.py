"""CSV export: input data, calculation table and metrics in one sheet."""

from __future__ import annotations

import csv
import io

from app.engines.export.base import ExportedFile, ExportPayload, escape_csv_cell, exporter


@exporter("csv")
def build_csv(payload: ExportPayload) -> ExportedFile:
    """Render the fit as a multi-section CSV file.

    Sections: ``# Input Data`` (x, y), ``# Calculation Table`` (full table
    with a Σ row — uncapped, unlike the JSON API), and ``# Metrics``.
    """
    buf = io.StringIO()
    writer = csv.writer(buf)
    fit = payload.fit

    writer.writerow(["# CurveLab — " + escape_csv_cell(payload.meta.title)])
    writer.writerow(["# Model", fit.model.value, "# Equation", escape_csv_cell(fit.equation.plain)])
    writer.writerow([])

    writer.writerow(["# Input Data"])
    writer.writerow(["x", "y"])
    for xv, yv in zip(payload.x, payload.y):
        writer.writerow([xv, yv])
    writer.writerow([])

    writer.writerow(["# Calculation Table"])
    table = fit.calculation_table
    writer.writerow([escape_csv_cell(c) for c in table.columns])
    for row in table.rows:
        writer.writerow(row)
    writer.writerow(["SUM"] + [f"{v:.6g}" for v in table.sums])
    writer.writerow([])

    writer.writerow(["# Metrics"])
    for key, value in vars(fit.metrics).items():
        writer.writerow([key, f"{value:.8g}" if value is not None else ""])

    return ExportedFile(buf.getvalue().encode("utf-8-sig"), "text/csv", "csv")
