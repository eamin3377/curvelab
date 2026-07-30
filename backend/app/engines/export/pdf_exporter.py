"""PDF export: a university-style report rendered with ReportLab.

Layout: cover page (institution / course / title / author / date over an
indigo band) → input data → summations → normal equations → step-by-step
solution → regression graph → results & metrics. Every page after the
cover carries a footer with the report title and page number.
"""

from __future__ import annotations

import io

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    PageBreak,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from app.engines.export.base import ExportedFile, ExportPayload, exporter, fmt_num

INDIGO = colors.HexColor("#4F46E5")
INDIGO_DARK = colors.HexColor("#312E81")
INDIGO_SOFT = colors.HexColor("#EEF2FF")
SLATE_200 = colors.HexColor("#E2E8F0")
SLATE_500 = colors.HexColor("#64748B")
SLATE_800 = colors.HexColor("#1E293B")

DOC_TABLE_ROWS = 40

TITLE = ParagraphStyle("TitleCL", fontName="Helvetica-Bold", fontSize=26, leading=32, textColor=INDIGO_DARK)
H1 = ParagraphStyle("H1CL", fontName="Helvetica-Bold", fontSize=14, leading=18, textColor=INDIGO_DARK, spaceBefore=14, spaceAfter=6)
BODY = ParagraphStyle("BodyCL", fontName="Helvetica", fontSize=9.5, leading=14, textColor=SLATE_800)
COVER_META = ParagraphStyle("CoverMeta", fontName="Helvetica", fontSize=11, leading=18, textColor=SLATE_800, alignment=1)
MONO = ParagraphStyle("MonoCL", fontName="Courier", fontSize=9, leading=13, textColor=SLATE_800)


def _table_style(header: bool = True) -> TableStyle:
    """Shared indigo-themed table styling."""
    commands = [
        ("FONTNAME", (0, 0), (-1, -1), "Courier"),
        ("FONTSIZE", (0, 0), (-1, -1), 8),
        ("GRID", (0, 0), (-1, -1), 0.4, SLATE_200),
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F8FAFC")]),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]
    if header:
        commands += [
            ("BACKGROUND", (0, 0), (-1, 0), INDIGO),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
        ]
    return TableStyle(commands)


def _footer(title: str):
    """Page footer painter: rule, report title, page number."""

    def paint(canvas, doc) -> None:  # type: ignore[no-untyped-def]
        canvas.saveState()
        canvas.setStrokeColor(SLATE_200)
        canvas.setLineWidth(0.5)
        canvas.line(2 * cm, 1.6 * cm, A4[0] - 2 * cm, 1.6 * cm)
        canvas.setFont("Helvetica", 8)
        canvas.setFillColor(SLATE_500)
        canvas.drawString(2 * cm, 1.1 * cm, f"CurveLab — {title}")
        canvas.drawRightString(A4[0] - 2 * cm, 1.1 * cm, f"Page {doc.page}")
        canvas.restoreState()

    return paint


def _cover(payload: ExportPayload) -> list:
    """Build the cover page flowables."""
    meta = payload.meta
    band = Table(
        [[""]], colWidths=[17 * cm], rowHeights=[0.35 * cm],
        style=TableStyle([("BACKGROUND", (0, 0), (-1, -1), INDIGO)]),
    )
    rows = [
        f"<b>{meta.institution}</b>" if meta.institution else "",
        meta.course,
        "",
        f"<b>Author:</b> {meta.author}" if meta.author else "",
        f"<b>Student ID:</b> {meta.student_id}" if meta.student_id else "",
        f"<b>Date:</b> {meta.date}",
    ]
    flow = [
        Spacer(1, 3 * cm),
        band,
        Spacer(1, 1.2 * cm),
        Paragraph(meta.title, TITLE),
        Spacer(1, 0.4 * cm),
        Paragraph("Least Squares Curve Fitting — Numerical Methods Project", COVER_META),
        Spacer(1, 1.6 * cm),
    ]
    flow += [Paragraph(r, COVER_META) for r in rows if r]
    flow += [
        Spacer(1, 2.2 * cm),
        Paragraph(
            f"Model: <b>{payload.fit.model.value}</b> &nbsp;·&nbsp; "
            f"Points: <b>{payload.fit.n}</b> &nbsp;·&nbsp; "
            f"R²: <b>{fmt_num(payload.fit.metrics.r2)}</b>",
            COVER_META,
        ),
        Spacer(1, 1.2 * cm),
        band,
        PageBreak(),
    ]
    return flow


@exporter("pdf")
def build_pdf(payload: ExportPayload) -> ExportedFile:
    """Render the fit as a paginated A4 PDF report and return its bytes."""
    fit = payload.fit
    buf = io.BytesIO()
    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=2 * cm,
        rightMargin=2 * cm,
        topMargin=2 * cm,
        bottomMargin=2.2 * cm,
        title=payload.meta.title,
        author=payload.meta.author or "CurveLab",
    )

    flow: list = _cover(payload)

    # 1. Input data
    flow.append(Paragraph("1. Input Data", H1))
    data_rows = [["i", "x", "y"]]
    for i, (xv, yv) in enumerate(zip(payload.x, payload.y), start=1):
        if i > DOC_TABLE_ROWS:
            data_rows.append(["…", f"first {DOC_TABLE_ROWS} of {fit.n} rows", ""])
            break
        data_rows.append([str(i), fmt_num(xv), fmt_num(yv)])
    flow.append(Table(data_rows, style=_table_style(), colWidths=[2 * cm, 6 * cm, 6 * cm]))

    # 2. Summations
    flow.append(Paragraph("2. Summations", H1))
    sum_rows = [["Quantity", "Value"]] + [
        [s.key, fmt_num(s.value)] for s in fit.summations
    ]
    flow.append(Table(sum_rows, style=_table_style(), colWidths=[5 * cm, 8 * cm]))

    # 3. Normal equations
    flow.append(Paragraph("3. Normal Equations  (A · c = b)", H1))
    ne = fit.normal_equations
    names = [c.name for c in fit.coefficients]
    ne_rows = [[""] + names + ["", "b"]]
    for row, rhs in zip(ne.matrix, ne.vector):
        ne_rows.append([""] + [fmt_num(v) for v in row] + ["|", fmt_num(rhs)])
    flow.append(Table(ne_rows, style=_table_style(header=False)))

    # 4. Steps
    flow.append(Paragraph("4. Step-by-Step Solution", H1))
    for step in fit.steps:
        flow.append(Paragraph(f"<b>Step {step.index} — {step.title}</b>", BODY))
        flow.append(Paragraph(step.description, BODY))
        flow.append(Spacer(1, 0.15 * cm))

    # 5. Graph
    if payload.chart_png:
        flow.append(Paragraph("5. Regression Graph", H1))
        img = Image(io.BytesIO(payload.chart_png))
        ratio = img.imageHeight / img.imageWidth
        img.drawWidth = 16 * cm
        img.drawHeight = 16 * cm * ratio
        flow.append(img)

    # 6. Results & metrics
    flow.append(Paragraph("6. Results", H1))
    flow.append(Paragraph(f"<b>{fit.equation.plain}</b>", MONO))
    flow.append(Spacer(1, 0.2 * cm))
    coeff_rows = [["Coefficient", "Value"]] + [
        [c.name, fmt_num(c.value, 8)] for c in fit.coefficients
    ]
    flow.append(Table(coeff_rows, style=_table_style(), colWidths=[5 * cm, 8 * cm]))

    flow.append(Paragraph("7. Goodness of Fit", H1))
    m = fit.metrics
    metric_rows = [["Metric", "Value"]] + [
        ["R²", fmt_num(m.r2, 8)],
        ["Adjusted R²", fmt_num(m.adj_r2, 8) if m.adj_r2 is not None else "—"],
        ["RMSE", fmt_num(m.rmse, 8)],
        ["MAE", fmt_num(m.mae, 8)],
        ["MSE", fmt_num(m.mse, 8)],
        ["SSE", fmt_num(m.sse, 8)],
        ["SST", fmt_num(m.sst, 8)],
    ]
    flow.append(Table(metric_rows, style=_table_style(), colWidths=[5 * cm, 8 * cm]))

    doc.build(flow, onFirstPage=_footer(payload.meta.title), onLaterPages=_footer(payload.meta.title))
    return ExportedFile(buf.getvalue(), "application/pdf", "pdf")
