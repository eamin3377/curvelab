# Phase 1 — Software Requirement Specification (SRS)

## 1. Project Overview

**Project Name:** CurveLab — Curve Fitting with Graphs (Linear, Polynomial & Exponential via Least Squares)
**Type:** Full-stack Python web application (University Numerical Methods project, portfolio grade)
**Deployment target:** Localhost first, then custom domain with HTTPS

### 1.1 Purpose
A professional web application that performs Least Squares curve fitting (Linear, Polynomial degree 2–6, Exponential y = ae^(bx)) on user-supplied datasets of any size, showing every summation, normal equation, coefficient, step-by-step solution, error metric, interactive animated graph, and exportable report (PDF/DOCX/XLSX/CSV/JSON/TXT/PNG/SVG).

### 1.2 Target Users
| User | Goal |
|---|---|
| Students | Verify hand calculations, learn step-by-step method |
| Teachers/Examiners | Evaluate correctness and presentation quality |
| Engineers/Recruiters | Judge software craftsmanship (portfolio) |

### 1.3 Core Value Proposition
"Enter data → instantly see the full numerical-methods solution, a premium interactive graph, and a university-ready report."

### 1.4 Technology Stack (Decision Record)

| Layer | Choice | Why |
|---|---|---|
| Backend | **FastAPI** (not Flask) | Async, automatic OpenAPI docs (impressive to examiners), Pydantic validation (critical for messy user data), better performance, modern typing. Flask would need 4+ extensions to match this out of the box. |
| Math Engine | **NumPy** (own Gaussian elimination implementation for normal equations, NumPy for vectorized summations) | Shows algorithm mastery (we implement the solver ourselves) while staying fast |
| Frontend | **React + Vite + TypeScript + TailwindCSS** | Only stack that achieves Stripe/Linear-grade UI; served as static build by FastAPI in production (still "one Python app") |
| Charts | **Plotly.js** (primary) with custom light theme | Zoom/pan/hover/PNG-SVG export/animation built in |
| Animations | Framer Motion + Lottie + CSS transitions | Micro-interactions, page transitions, animated counters |
| Exports | ReportLab (PDF), python-docx (DOCX), openpyxl (XLSX), Kaleido (server-side chart images) | All pure Python |
| Data ingest | pandas (CSV/Excel/TXT/JSON parsing, cleaning) | Battle-tested parsing |
| Database | **None required** — stateless compute. Optional SQLite session-history module marked as v2 | Keeps grading simple, zero-config deploys |
| Container | Docker + docker-compose, Nginx reverse proxy in production | |

### 1.5 System Context (High Level)

```
Browser (React SPA)
   │  JSON over HTTPS (REST)
   ▼
FastAPI Application
   ├── API Layer        (routers, request/response schemas)
   ├── Service Layer    (fit orchestration, validation, cleaning)
   ├── Math Engine      (summations, normal equations, Gaussian solver, metrics)
   ├── Graph Data Engine(curve sampling, residuals, confidence bands)
   └── Export Engine    (PDF / DOCX / XLSX / CSV / JSON / TXT / PNG / SVG)
```

### 1.6 Scope
**In scope:** 3 fitting models, any dataset size (soft limit 50,000 points), file upload + paste + manual entry, step-by-step math display, interactive graphs, residual plot, prediction, 8 export formats, full responsive premium UI, Docker deployment.
**Out of scope (v1):** User accounts, saved history DB, multivariate regression, non-least-squares methods.

---

## 2. Functional Requirements (FR)

### FR-1 Data Input
- FR-1.1 Manual X/Y entry via editable paired-input grid (add/remove rows, keyboard navigation)
- FR-1.2 Paste from Excel/CSV/whitespace text — auto-detect delimiter and column mapping
- FR-1.3 Upload CSV, XLSX, XLS, TXT, JSON via button or drag-and-drop (max 10 MB)
- FR-1.4 Auto-clean: strip empty cells, coerce numeric strings, remove duplicate (x,y) pairs (user-toggleable), report every cleaning action to the user
- FR-1.5 Validation: n ≥ 2 (linear), n ≥ degree+1 (polynomial), all y > 0 for exponential (clear error with explanation of ln transform); inline, human-readable error messages
- FR-1.6 Sample datasets loadable with one click (demo mode)

### FR-2 Curve Fitting Engine
- FR-2.1 Linear fit y = a + bx via least squares
- FR-2.2 Polynomial fit degree m (2 ≤ m ≤ 6, user selectable)
- FR-2.3 Exponential fit y = ae^(bx) via linearization (ln y = ln a + bx)
- FR-2.4 Compute and expose ALL summations used: Σx, Σy, Σxy, Σx², Σx³, Σx⁴ … up to Σx^(2m), Σx^k·y, and for exponential Σln y, Σx·ln y
- FR-2.5 Construct and display normal equations symbolically with numbers substituted
- FR-2.6 Solve normal equations with in-house Gaussian elimination (partial pivoting), showing augmented matrix steps
- FR-2.7 Output coefficients (12 sig. figs internally, formatted to user-chosen precision 2–8)
- FR-2.8 Generate final equation string in plain text and LaTeX
- FR-2.9 Predict ŷ for any user-entered x (single or batch), interpolation/extrapolation flagged
- FR-2.10 Compute R², Adjusted R², RMSE, MSE, MAE, SSE, SST, residuals per point
- FR-2.11 Optional "Compare all models" mode: fit all three at once, rank by R²/RMSE
- FR-2.12 All computation completes and renders in < 1 s for n ≤ 10,000 (perceived instant)

### FR-3 Step-by-Step Solution
- FR-3.1 Numbered pedagogical walkthrough: formula → summation table → normal equations → matrix solving steps → coefficients → equation → metrics
- FR-3.2 Rendered with KaTeX; every step collapsible; "Copy step" action

### FR-4 Graphs
- FR-4.1 Main chart: scatter (actual), fitted line/curve (smooth 300-point sampling), prediction points highlighted, legend, equation annotation
- FR-4.2 Residual plot (residual vs x, zero reference line)
- FR-4.3 ~95% confidence band for linear fit (shaded region); documented approximation for others
- FR-4.4 Interactions: zoom, pan, box-select zoom, reset, hover tooltips (x, y, ŷ, residual), legend toggle
- FR-4.5 Animated draw-in of fitted curve on compute; smooth transitions on refit
- FR-4.6 Light/dark graph theme toggle (app stays light; graph canvas may go dark)
- FR-4.7 Export PNG and SVG client-side; fully responsive/resizable

### FR-5 Tables
- FR-5.1 Input data table and full calculation table (x, y, x², x³, x⁴, xy, x²y, ln y, ŷ, residual, residual² — columns adapt to model)
- FR-5.2 Summation footer row (sticky), sticky header, search, per-column sort, filter, pagination (10/25/50/100/All)
- FR-5.3 Copy to clipboard, download table as CSV/XLSX

### FR-6 Exports
- FR-6.1 CSV, JSON, TXT (formatted plain-text report), XLSX (multi-sheet: Input | Calculation | Results | Summary + embedded chart image)
- FR-6.2 PDF report: cover page (university style: project name, course, student fields, date, logo placeholder), input table, formulas, summation table, normal equations, step-by-step solution, chart image, equation, predictions, metrics summary, page numbers + footer
- FR-6.3 DOCX report mirroring PDF structure with proper Word styles
- FR-6.4 Print-optimized browser view (print stylesheet)
- FR-6.5 All exports generated server-side from the exact computed session payload

### FR-7 Application Pages
- FR-7.1 Landing: hero, animated counters, feature cards, "About the Algorithms" educational section, interactive mini-demo, contact/footer
- FR-7.2 Workspace (main app): input panel → results dashboard (result cards, graph, tables, steps, export bar)
- FR-7.3 Docs page: how to use + method theory
- FR-7.4 Sticky responsive navbar, modern footer, 404 page

---

## 3. Non-Functional Requirements (NFR)

| # | Category | Requirement |
|---|---|---|
| NFR-1 | Performance | API fit response < 300 ms for n ≤ 10,000; first contentful paint < 1.5 s; Lighthouse Performance ≥ 90 |
| NFR-2 | Usability | Zero-training usage; every error message states what happened + how to fix; skeleton loaders, never blank screens |
| NFR-3 | Reliability | Graceful handling of singular/ill-conditioned matrices (detect, warn, suggest lower degree); no unhandled 500s |
| NFR-4 | Accuracy | Coefficients match reference (NumPy polyfit / SciPy) to ≥ 10 significant digits on test suite |
| NFR-5 | Security | Strict input validation, file-type + size limits, no file persistence, rate limiting, security headers, HTTPS in production |
| NFR-6 | Accessibility | WCAG 2.1 AA: keyboard navigable, ARIA, contrast ≥ 4.5:1, reduced-motion support |
| NFR-7 | Responsiveness | Pixel-perfect at 360, 768, 1024, 1440, 1920 px + landscape |
| NFR-8 | Maintainability | Layered architecture, typed everywhere (mypy + TS strict), ≥ 85% math-engine test coverage |
| NFR-9 | Portability | Runs via single `docker compose up`; also plain `uvicorn` + `npm run dev` for development |
| NFR-10 | Compatibility | Latest Chrome, Firefox, Edge, Safari (2 versions back) |
| NFR-11 | Observability | Structured logging, request IDs, /health endpoint |
| NFR-12 | Aesthetics | Design-system driven (tokens for color/spacing/type); no default-Bootstrap look; light theme only for app shell |
