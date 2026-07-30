# Phase 4 — Folder Structure, API Design, Database, Security & Performance

## 1. Enterprise Folder Structure

```
curvelab/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI factory, middleware, static mount
│   │   ├── api/
│   │   │   ├── deps.py                # shared dependencies (rate limit, request ctx)
│   │   │   └── routers/
│   │   │       ├── fit.py
│   │   │       ├── data.py
│   │   │       ├── export.py
│   │   │       └── meta.py
│   │   ├── schemas/                   # Pydantic models (single source of API truth)
│   │   │   ├── dataset.py             # DataPoint, Dataset, CleaningReport
│   │   │   ├── fit.py                 # FitRequest, FitResult, Step, Metrics
│   │   │   ├── graph.py               # GraphPayload, Series, ConfidenceBand
│   │   │   └── export.py              # ExportRequest, ReportMeta
│   │   ├── services/
│   │   │   ├── fitting_service.py
│   │   │   ├── data_service.py
│   │   │   └── export_service.py
│   │   ├── engines/
│   │   │   ├── math/                  # summations, solver, models, metrics, steps
│   │   │   ├── graph/                 # curve_sampler, confidence, theme
│   │   │   └── export/                # exporters + chart_renderer
│   │   ├── core/
│   │   │   ├── config.py
│   │   │   ├── errors.py
│   │   │   ├── logging.py
│   │   │   └── constants.py           # limits, sample datasets registry
│   │   └── assets/                    # fonts, logo placeholder, report templates
│   ├── tests/
│   │   ├── unit/                      # engines (math, graph, export)
│   │   ├── integration/               # API via httpx TestClient
│   │   ├── property/                  # Hypothesis suites
│   │   └── fixtures/                  # golden datasets + expected coefficients
│   ├── pyproject.toml                 # deps, ruff, mypy, pytest config
│   └── Dockerfile
├── frontend/
│   ├── src/
│   │   ├── app/                       # router, providers, App shell
│   │   ├── pages/                     # Landing, Workspace, Methods, NotFound
│   │   ├── features/
│   │   │   ├── data-input/            # ManualGrid, PastePanel, UploadZone, Samples
│   │   │   ├── fitting/               # ModelSelector, FitControls, useFit hook
│   │   │   ├── results/               # MetricCards, EquationCard, PredictionCard
│   │   │   ├── charts/                # MainChart, ResidualChart, ChartToolbar
│   │   │   ├── tables/                # DataTable, CalcTable, SummationTable
│   │   │   ├── steps/                 # StepTimeline, StepItem
│   │   │   └── export/                # ExportBar, useExport
│   │   ├── components/ui/             # design-system primitives
│   │   ├── lib/                       # api client, formatters, plotly themes
│   │   ├── styles/                    # tailwind.css, tokens.css
│   │   └── assets/                    # lottie/*.json, illustrations
│   ├── public/
│   ├── index.html
│   ├── tailwind.config.ts
│   ├── vite.config.ts
│   └── package.json
├── deploy/
│   ├── docker-compose.yml             # dev: backend + frontend hot-reload
│   ├── docker-compose.prod.yml        # prod: app + nginx
│   ├── nginx/nginx.conf
│   └── render.yaml / railway.json
├── docs/
├── .github/workflows/                 # ci.yml, deploy.yml
├── README.md  LICENSE  CHANGELOG.md  CONTRIBUTING.md
├── CODE_OF_CONDUCT.md  SECURITY.md  .gitignore  .editorconfig
└── Makefile                           # make dev / test / lint / build / docker
```

Principles: feature-folder frontend (no giant `components/` dump), engines importable without FastAPI, tests mirror source tree, one canonical schema layer shared by services and exporters.

---

## 2. API Design (REST, prefix `/api/v1`)

Auto-docs at `/api/docs` (Swagger) and `/api/redoc`.

| # | Method & Path | Purpose |
|---|---|---|
| 1 | `POST /fit` | Fit one model, return complete result |
| 2 | `POST /fit/compare` | Fit linear + polynomial(m) + exponential, ranked |
| 3 | `POST /predict` | Predict ŷ for x values given raw data + model (recompute) |
| 4 | `POST /data/parse-file` | multipart upload → cleaned Dataset + CleaningReport |
| 5 | `POST /data/parse-text` | pasted text → cleaned Dataset + CleaningReport |
| 6 | `GET /data/samples` / `GET /data/samples/{id}` | demo datasets |
| 7 | `POST /export/{format}` | format ∈ csv,json,txt,xlsx,pdf,docx,png,svg → file stream |
| 8 | `GET /health`, `GET /version` | ops |

**Key contracts (abbreviated):**

`POST /fit` request:
```json
{
  "x": [1, 2, 3, 4],
  "y": [2.1, 4.2, 6.1, 8.3],
  "model": "polynomial",
  "degree": 2,
  "precision": 4,
  "options": { "remove_duplicates": true, "confidence_band": true }
}
```

`FitResult` response (200):
```json
{
  "model": "polynomial",
  "n": 4,
  "cleaning_report": { "duplicates_removed": 0, "empty_dropped": 0, "coerced": 0 },
  "summations": { "sum_x": 10, "sum_y": 20.7, "sum_x2": 30, "sum_x3": 100,
                  "sum_x4": 354, "sum_xy": 61.9, "sum_x2y": 205.3 },
  "normal_equations": { "matrix": [[0]], "vector": [0],
                        "latex_symbolic": "...", "latex_substituted": "..." },
  "solver": { "method": "gaussian_elimination_partial_pivoting",
              "condition_warning": null },
  "coefficients": [{ "name": "a0", "value": 0.1052 }],
  "equation": { "plain": "y = 0.1052 + 1.9820x + 0.0125x^2",
                "latex": "y = 0.1052 + 1.9820x + 0.0125x^{2}" },
  "metrics": { "r2": 0.9993, "adj_r2": 0.9986, "rmse": 0.0721,
               "mse": 0.0052, "mae": 0.0618, "sse": 0.0208, "sst": 29.61 },
  "calculation_table": { "columns": ["x","y","x2","x3","x4","xy","x2y","y_hat","residual","residual2"],
                          "rows": [[0]], "sums": [0] },
  "steps": [{ "index": 1, "title": "Model formula", "latex": "...", "table": null }],
  "graph": { "scatter": {}, "curve": {"x":[],"y":[]},
             "residuals": {}, "confidence_band": {"upper":[],"lower":[],"approximate": false},
             "axis": { "x_range": [], "y_range": [] } }
}
```

`POST /export/{format}` request: `{ "fit_request": {…same as /fit…}, "report_meta": { "title", "author", "student_id", "course", "institution", "date" } }` → binary stream with `Content-Disposition`.

**Error shape (all 4xx):**
```json
{ "type": "validation_error", "title": "Exponential fit requires positive y values",
  "detail": "Rows 3, 7 have y ≤ 0. Remove them or choose another model.",
  "field": "y", "offending_indices": [3, 7] }
```

Conventions: versioned prefix, snake_case JSON, idempotent POSTs (pure compute), GZip on responses > 1 KB, `X-Request-ID` echoed, OpenAPI examples for every schema.

---

## 3. Database Requirement — Decision: **No database in v1**

Rationale: every operation is a pure computation; persistence adds accounts, migrations, privacy concerns, and deployment friction with zero grading value.
- Sample datasets: static JSON in `core/constants.py` / assets
- "Recent work": browser `localStorage` (last 5 datasets + settings), export/import as JSON
- **v2 (documented, not built):** optional SQLite + SQLModel `sessions` table `(id, created_at, name, dataset_json, fit_request_json)` behind a feature flag; architecture already isolates this behind a `HistoryRepository` interface so it can be added without refactor

---

## 4. Security Requirement

| ID | Control |
|---|---|
| SEC-1 | Input validation: Pydantic strict mode; numeric coercion whitelist; n, degree, precision, string-length bounds enforced before any compute |
| SEC-2 | File uploads: 10 MB cap (checked streaming), extension + MIME + content sniff (pandas parse in try/except sandbox), processed fully in memory, **never written to disk**, no macros evaluated (openpyxl `data_only`, xlsx read-only mode) |
| SEC-3 | Rate limiting: 60 req/min/IP global, 10/min on `/export/*` (CPU-heavy) via slowapi; 429 + Retry-After |
| SEC-4 | Headers (Nginx + middleware): `Content-Security-Policy` (self + inline-styles for KaTeX only), `X-Content-Type-Options: nosniff`, `X-Frame-Options: DENY`, `Referrer-Policy: strict-origin-when-cross-origin`, HSTS in production |
| SEC-5 | CORS locked to configured origins (localhost:5173 dev, domain prod); no wildcard |
| SEC-6 | No secrets in repo: `.env` + `.env.example`, settings via environment; Docker secrets for prod |
| SEC-7 | Error hygiene: stack traces never leak to clients; problem-JSON only; full traces to server logs |
| SEC-8 | Dependency safety: pinned lockfiles (uv/pip-tools + package-lock), `pip-audit` + `npm audit` in CI, Dependabot enabled |
| SEC-9 | Export injection defenses: CSV formula-injection escaping (prefix `'` on `=+-@` cells), filename sanitization, user-provided report fields length-capped and escaped in PDF/DOCX |
| SEC-10 | DoS guards: request body limit 12 MB, compute timeout 10 s per request (anyio timeout), Plotly/Kaleido worker capped |
| SEC-11 | HTTPS everywhere in production (Let's Encrypt via Nginx/certbot), HTTP→HTTPS redirect |
| SEC-12 | SECURITY.md with responsible-disclosure instructions |

---

## 5. Performance Requirement (detailed)

**Backend budgets (p95, n = 10,000 points):**
| Operation | Budget |
|---|---|
| /fit (linear/exp) | ≤ 150 ms |
| /fit (poly deg 6) | ≤ 300 ms |
| /data/parse-file 10 MB CSV | ≤ 1.5 s |
| /export pdf/docx/xlsx | ≤ 3 s |
| /export png/svg (Kaleido) | ≤ 2 s |

Tactics: vectorized NumPy throughout (no Python loops over points), pandas C engine for parsing, calculation_table capped at 1,000 rows in JSON response (full table only in CSV/XLSX exports; UI paginates server-truncated set with notice), GZip, uvicorn with 2–4 workers, Kaleido process reused (warm start).

**Frontend budgets:**
| Metric | Target |
|---|---|
| Lighthouse Perf / A11y / Best-Practices | ≥ 90 / ≥ 95 / ≥ 95 |
| FCP / LCP / CLS / TTI | ≤ 1.5 s / ≤ 2.5 s / < 0.1 / ≤ 3 s |
| Initial JS (gzip) | ≤ 250 KB (Plotly lazy-loaded as separate chunk on Workspace only) |

Tactics: route-based code splitting (Landing loads no Plotly/KaTeX), `plotly.js-basic-dist-min` (not full bundle), KaTeX + Lottie lazy, WebGL scatter (`scattergl`) automatically for n > 2,000, virtualized tables (TanStack Virtual) for large datasets, debounced auto-fit (300 ms), memoized chart props, font subsetting + `font-display: swap`, all animations transform/opacity only, image-free design (SVG/CSS gradients).

**Verification:** pytest-benchmark suite for engine timings + Lighthouse CI in GitHub Actions with budget assertions.
