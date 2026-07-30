# Phase 3 — Backend, Mathematical Engine, Graph Engine & Export Engine

## 1. Backend Requirement Document (FastAPI)

### 1.1 Architectural Style
Layered, stateless, service-oriented monolith:

```
Request → Router (API layer) → Service (orchestration) → Engine (pure math/export) → Response
```

**Hard rules:**
- Routers contain zero business logic (validate, delegate, serialize only)
- Engines are pure functions/classes: no FastAPI, no I/O, no globals → 100% unit-testable
- All request/response bodies are Pydantic v2 models with strict types and examples (drives auto OpenAPI docs at `/api/docs`)
- Stateless: every request carries all needed data; no server session; exports **recompute server-side from raw input** to keep payloads small and guarantee integrity

### 1.2 Modules

| Module | Responsibility |
|---|---|
| `api/routers/fit.py` | POST fit, POST compare, POST predict |
| `api/routers/data.py` | POST parse-file, POST parse-text (paste), GET samples |
| `api/routers/export.py` | POST export/{format} |
| `api/routers/meta.py` | GET health, GET version |
| `services/fitting_service.py` | Orchestrates: clean → validate → dispatch to engine → assemble FitResult |
| `services/data_service.py` | File/paste parsing (pandas), delimiter sniffing, cleaning pipeline, cleaning report |
| `services/export_service.py` | Dispatch to exporters, filename/timestamping, streaming response |
| `core/config.py` | Pydantic Settings (env-driven: CORS origins, limits, debug) |
| `core/errors.py` | Domain exceptions → RFC 7807-style problem JSON (`{type, title, detail, field?}`) |
| `core/logging.py` | Structured JSON logs, request-ID middleware |
| `engines/…` | Math, graph-data, export engines (below) |

### 1.3 Cross-Cutting
- **Validation limits:** n ≤ 50,000 points; file ≤ 10 MB; degree ∈ [2,6]; precision ∈ [2,8]
- **Middleware:** CORS (locked to frontend origin), GZip, request-ID, timing header, rate limit (slowapi: 60 req/min/IP, 10/min on exports)
- **Error taxonomy:** `ValidationError(422)`, `SingularMatrixError(422 with suggestion)`, `FileParseError(400)`, `PayloadTooLarge(413)`, `RateLimited(429)` — never a raw 500 to the client
- **Serving:** In production FastAPI mounts the built React `dist/` as static files with SPA fallback; single container, single port

---

## 2. Mathematical Engine Requirement (`engines/math/`)

### 2.1 Components
```
math/
├── summations.py      # Σ builders (vectorized)
├── normal_equations.py# builds A, b for each model
├── gaussian_solver.py # own Gaussian elimination + partial pivoting, step recorder
├── models/
│   ├── linear.py      # y = a + bx
│   ├── polynomial.py  # y = a0 + a1x + ... + amx^m
│   └── exponential.py # y = a·e^(bx) via ln-linearization
├── metrics.py         # R², adj-R², RMSE, MSE, MAE, SSE, SST, residuals
├── predictor.py       # ŷ evaluation, extrapolation detection
├── steps.py           # StepRecorder → ordered pedagogical steps (text + LaTeX)
└── formatting.py      # sig-figs, LaTeX/plain equation string builders
```

### 2.2 Algorithm Specifications

**MATH-1 Summations** — For polynomial degree m compute Σx^k for k = 0..2m and Σx^k·y for k = 0..m using float64 NumPy with pairwise summation. For exponential: Σx, Σx², Σln y, Σx·ln y. Every summation value is included in the response (used for the summation table and steps).

**MATH-2 Normal equations** — Assemble symmetric (m+1)×(m+1) system A·c = b from summations. Return both the numeric matrix and its LaTeX rendering with substituted values.

**MATH-3 Gaussian solver (own implementation, the academic centerpiece)**
- Partial pivoting; records every elimination operation (`R2 ← R2 − (k)·R1`) with the resulting augmented matrix snapshot for step-by-step display
- Condition estimate; if |pivot| < 1e-12 → `SingularMatrixError` with human suggestion ("data may be collinear; try lower degree")
- For degree ≥ 4, x-values are mean-centered/scaled internally for stability, coefficients transformed back; the steps view notes this transparently

**MATH-4 Exponential model** — Guard: all y > 0 (else 422 explaining why ln is impossible, offering to drop offending rows). Fit ln y = ln a + bx by linear least squares; report both linearized and final form; metrics computed in **original y-space** (honest R²).

**MATH-5 Metrics** — SSE = Σ(y−ŷ)², SST = Σ(y−ȳ)², R² = 1−SSE/SST (guard SST=0), adj-R² with p = params, RMSE = √(SSE/n), MSE, MAE, per-point residuals.

**MATH-6 Prediction** — Evaluate model at arbitrary x (scalar/array); flag `extrapolated: true` when x outside [min x, max x].

**MATH-7 Step recorder** — Emits ordered `Step{index, title, description, latex, table?}` covering: model formula → summation table → normal equations (symbolic → substituted) → Gaussian elimination snapshots → back-substitution → coefficients → final equation → metric formulas with numbers.

**MATH-8 Accuracy contract** — Test suite compares coefficients against `numpy.polyfit`/`scipy.optimize` references: agreement ≥ 10 significant digits on well-conditioned data; documented tolerance on stress cases. Property-based tests (Hypothesis) for invariants (e.g., R² ≤ 1, residuals sum ≈ 0 for linear with intercept).

---

## 3. Graph Engine Requirement (`engines/graph/`)

Backend produces **chart-ready data**, frontend renders with Plotly. Kaleido renders server-side images for PDF/DOCX/XLSX embedding using the same spec (single source of truth for chart appearance).

| ID | Requirement |
|---|---|
| GR-1 | `curve_sampler.py`: 300 evenly spaced x samples across [min x − 5% pad, max x + 5% pad]; exponential sampled in original space |
| GR-2 | Series payload: `scatter(actual)`, `curve(fitted)`, `predictions[]`, `residuals[]` (paired with x), plus axis ranges |
| GR-3 | Confidence band (linear): 95% CI for mean response using t-distribution, SE(ŷ₀) = s·√(1/n + (x₀−x̄)²/Sxx); returned as upper/lower arrays; for polynomial/exponential v1 returns band via same formula on the linearized/design-matrix form with an "approximate" flag shown in UI |
| GR-4 | `theme.py`: two Plotly layout templates — `curvelab_light` (white, slate grid #E2E8F0, indigo/sky series, Inter font) and `curvelab_dark` (slate-900 canvas — only inside the chart card); identical templates used by Kaleido exports |
| GR-5 | Chart config contract (frontend): scroll-zoom, box-zoom, pan, double-click reset, hover unified tooltip (x, y, ŷ, residual), legend toggle, `toImage` PNG (2x scale) and SVG buttons, equation + R² annotation top-left |
| GR-6 | Residual chart spec: stem/marker plot, zero line, symmetric y-range |
| GR-7 | Animation contract: frontend draws curve via progressive reveal; backend guarantees monotone x ordering of samples to make this trivial |

---

## 4. Export Engine Requirement (`engines/export/`)

```
export/
├── base.py         # Exporter protocol: build(payload) -> bytes, media_type, filename
├── csv_exporter.py / json_exporter.py / txt_exporter.py
├── excel_exporter.py   # openpyxl
├── pdf_exporter.py     # ReportLab Platypus
├── docx_exporter.py    # python-docx
└── chart_renderer.py   # Kaleido PNG/SVG from Plotly spec
```

All exporters consume one canonical `ReportPayload` (raw data + full FitResult + metadata: project title, author fields, date, model). Streaming `Response` with correct `Content-Disposition`; filenames like `curvelab_linear_2026-07-30.pdf`.

| ID | Format | Spec |
|---|---|---|
| EX-1 | CSV | Two sections: input data; calculation table with summation row |
| EX-2 | JSON | Full structured FitResult (machine-readable, mirrors API schema) |
| EX-3 | TXT | Monospace formatted report: tables via aligned columns, equations in plain text, steps numbered |
| EX-4 | XLSX | Sheets: `Input` \| `Calculation` (formulas as real Excel formulas where feasible, summation row bold) \| `Results` (coefficients, metrics, equation) \| `Graph` (embedded PNG) \| `Summary`; styled: indigo header fills, frozen panes, autofit widths, number formats per precision |
| EX-5 | PDF | ReportLab template: **Cover** (university-style: institution line, course, project title, student name/ID fields, date, subtle indigo gradient band + logo placeholder) → TOC → Input table → Method & formulas → Summation table → Normal equations → Step-by-step (matrix snapshots as styled tables) → Chart (Kaleido PNG, 300 dpi) → Residual plot → Equation & coefficients → Predictions → Metrics summary card → Conclusion; header/footer with page numbers, Inter-compatible embedded fonts |
| EX-6 | DOCX | Mirrors PDF structure using proper Word styles (Heading 1/2, styled tables, embedded images) so users can edit before submission |
| EX-7 | PNG/SVG | Client-side via Plotly toolbar (instant) AND server route via Kaleido (for consistency in reports) |
| EX-8 | Print | Frontend print stylesheet: hides nav/inputs, expands all steps, page-break rules per card |
| EX-9 | Performance | PDF/DOCX/XLSX generation ≤ 3 s for n ≤ 1,000 rows; tables beyond 1,000 rows are truncated in documents with an explicit "first 1,000 of N rows" note (full data always available via CSV/JSON) |
