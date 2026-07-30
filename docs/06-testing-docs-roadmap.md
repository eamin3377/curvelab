# Phase 6 — Testing Plan, Documentation Plan & Implementation Roadmap

## 1. Testing Plan

### 1.1 Test Pyramid & Coverage Targets

| Layer | Tooling | Coverage target |
|---|---|---|
| Unit — math engine | pytest + numpy.testing | ≥ 95% (the academic core, non-negotiable) |
| Unit — graph/export engines | pytest | ≥ 85% |
| Property-based | Hypothesis | invariants suite green |
| Integration — API | pytest + httpx TestClient | every endpoint, happy + error paths |
| Frontend unit | Vitest + React Testing Library | key components + hooks ≥ 80% |
| E2E | Playwright | 6 critical user journeys |
| Non-functional | pytest-benchmark, Lighthouse CI, axe-core | budgets from Phase 4 §5 |

### 1.2 Math Engine Test Specification (the centerpiece)
- **Golden datasets** (`tests/fixtures/`): textbook problems (Chapra & Canale examples) with hand-verified summations, normal equations, coefficients, R² — asserted digit-by-digit at stated precision
- **Reference cross-checks:** coefficients vs `numpy.polyfit` / linear algebra reference ≥ 10 significant digits on well-conditioned data
- **Hypothesis invariants:** R² ≤ 1; linear residuals sum ≈ 0; fitting exact polynomial data recovers coefficients; solution invariant under data shuffling; exponential fit of `a·e^(bx)` synthetic data recovers a, b
- **Edge cases:** n = 2 linear, n = degree+1 exact fit, all-equal x (singular → correct error + suggestion), all-equal y (SST = 0 guard), y ≤ 0 for exponential (422 with offending indices), huge/tiny magnitudes (1e±8, scaling correctness), 50,000-point stress, duplicates removal on/off
- **Solver tests:** partial pivoting picks correct pivot, recorded elimination steps reproduce the solution when replayed, condition warning triggers

### 1.3 API Integration Tests
Each endpoint: valid request → schema-validated response; every documented 4xx (bad model, degree out of range, oversized file, malformed CSV/JSON, rate limit); export endpoints return correct MIME + non-empty parseable files (open XLSX with openpyxl, PDF header check, DOCX with python-docx); CSV formula-injection escaping verified.

### 1.4 Frontend & E2E
- Vitest: parsers (paste detection), formatters, useFit state machine, EditableGrid keyboard behavior, ExportBar states
- Playwright journeys:
  1. Manual entry → linear fit → results visible
  2. CSV upload → cleaning banner → polynomial fit → residual plot
  3. Paste Excel data → exponential fit → error on y ≤ 0 → fix → success
  4. Prediction incl. extrapolation badge
  5. PDF + XLSX download (file assertions)
  6. Mobile viewport full flow
- Plus: visual snapshots of Landing + Workspace at 3 breakpoints, axe-core scan on all pages, reduced-motion mode smoke test

### 1.5 Gates
CI blocks merge on: lint (ruff, eslint), types (mypy --strict on engines, tsc), all tests, coverage thresholds, Lighthouse budgets, audit findings (high+). Pre-commit hooks mirror lint/format locally.

---

## 2. Documentation Plan

| Doc | Location | Audience | Contents |
|---|---|---|---|
| README | repo root | everyone | Phase 5 §3 blueprint |
| Wiki (8 pages) | GitHub Wiki | users + graders | Phase 5 §2.3 structure |
| API reference | auto `/api/docs` + wiki page | developers | generated from Pydantic schemas + examples |
| Architecture doc | `docs/architecture.md` | engineers | layer diagram, data flow, decision records (FastAPI-vs-Flask, no-DB, own-Gaussian-solver) |
| Math derivations | `docs/mathematics.md` + in-app Methods page | graders | full LSQ derivations for all three models, worked example matching a golden test |
| User guide | wiki + in-app Docs page | end users | annotated screenshots/GIFs of every feature |
| Deployment guide | `docs/deployment.md` | ops | localhost, Docker, Render, Railway, VPS+Nginx+HTTPS, Azure |
| Testing guide | `docs/testing.md` | contributors | how to run each suite, add golden datasets |
| Project report (university) | exported PDF via the app itself | teacher | the app generates its own submission document — a deliberate "wow" moment |
| Inline docs | code | maintainers | docstrings on every engine function with the formula it implements; no noise comments |

Docs are written per-milestone (not at the end) and CI checks for broken links.

---

## 3. Implementation Roadmap (10 milestones)

| # | Milestone | Deliverable | Exit criteria |
|---|---|---|---|
| M1 | Repo & scaffolding | Git init, folder structure, tooling (pyproject, Vite, Tailwind, CI skeleton, Makefile), governance files | `make dev` serves hello-world SPA + `/api/v1/health` |
| M2 | Math engine | summations, normal equations, Gaussian solver + step recorder, 3 models, metrics, predictor | Golden + Hypothesis suites green, ≥ 95% coverage |
| M3 | Data pipeline | parse-file/parse-text services, cleaning + report, samples, validation errors | Integration tests for all input formats |
| M4 | Fit API | `/fit`, `/fit/compare`, `/predict` with full FitResult schema | Swagger docs complete with examples |
| M5 | Workspace UI core | design-system primitives, input panel (manual/paste/upload), fit flow, result cards, equation card, tables | E2E journeys 1–3 pass |
| M6 | Graphs | Plotly themes, main chart + residuals + confidence band, animations, PNG/SVG client export | Journey 4 + visual snapshots |
| M7 | Step-by-step + polish | StepTimeline with KaTeX, skeletons, toasts, micro-interactions, reduced-motion | axe-core clean, Lighthouse ≥ targets |
| M8 | Export engine | CSV/JSON/TXT/XLSX/PDF/DOCX + Kaleido renders + print stylesheet | Journey 5, export file assertions |
| M9 | Landing + Methods pages | hero, counters, feature cards, algorithm tabs, mini-demo, footer, 404 | Full responsive matrix verified |
| M10 | Ship | Docker prod image, Render deploy, VPS+domain+HTTPS guide executed, README screenshots, wiki, CHANGELOG v1.0.0, tag + release | Live URL, all CI gates green |

Order rationale: math first (grades depend on it), UI before graphs (graphs need result plumbing), landing last (marketing after product), deploy continuously from M1 via CI.
