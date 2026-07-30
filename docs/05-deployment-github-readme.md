# Phase 5 — Deployment Plan, GitHub Structure & README Plan

## 1. Deployment Plan

### 1.1 Environment Matrix

| Env | Purpose | How it runs |
|---|---|---|
| Local dev | Daily development | `make dev`: uvicorn --reload (:8000) + Vite dev server (:5173, proxy `/api` → 8000) |
| Local prod-sim | Pre-release check | `docker compose -f deploy/docker-compose.prod.yml up` (:80) |
| Cloud PaaS | Free/cheap public demo | Render or Railway (single Docker service) |
| VPS + domain | Final home | Docker + Nginx + Let's Encrypt on your domain |
| Azure (optional) | If required by course | Azure App Service for Containers, same image |

### 1.2 Build & Container Strategy
**Single production image, multi-stage Dockerfile:**
1. Stage `frontend-build`: `node:20-alpine` → `npm ci && npm run build` → `dist/`
2. Stage `backend`: `python:3.12-slim` → install deps from lockfile → copy `app/` → copy `dist/` into `app/static/`
3. Runtime: non-root user, `uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 2`, HEALTHCHECK hits `/api/v1/health`, image target < 400 MB (Kaleido is the heavy part)

`docker-compose.prod.yml`: services `app` + `nginx` (ports 80/443, mounted certs, config from `deploy/nginx/nginx.conf`).

### 1.3 Nginx Configuration (spec)
- Reverse proxy `/` → `app:8000`; GZip + Brotli static assets; cache immutable hashed assets 1 year, `index.html` no-cache
- Security headers (SEC-4), `client_max_body_size 12m`, rate-limit zone as second layer
- HTTP→HTTPS 301; TLS 1.2+; certs via certbot with auto-renew cron/systemd timer

### 1.4 Rollout Sequence
1. **Localhost milestone** — `make dev` documented in README; demo-ready for class presentation offline
2. **Dockerize** — build, smoke test (`curl /api/v1/health`, run one fit + one PDF export)
3. **Render deploy** — `render.yaml` blueprint (Docker web service, free/starter tier, health check path, env vars); note: free tier cold-start ~30 s (acceptable for demo; keep-alive ping optional)
4. **Railway alternative** — `railway.json` documented as fallback (simpler, generous trial)
5. **VPS + domain (production)** — Ubuntu 24.04: create deploy user, UFW (22/80/443 only), install Docker, clone repo, `docker compose up -d`, point DNS A record, certbot issue, verify HTTPS + headers via securityheaders.com
6. **Azure option** — push image to GHCR, App Service for Containers, custom domain + managed cert; documented but optional

### 1.5 CI/CD (GitHub Actions)
- `ci.yml` (every push/PR): ruff + mypy + pytest w/ coverage → eslint + tsc + vitest → frontend build → Docker build → Lighthouse CI on preview build → pip-audit/npm audit
- `deploy.yml` (tag `v*`): build & push image to GHCR → trigger Render deploy hook (or SSH `docker compose pull && up -d` for VPS) → GitHub Release with CHANGELOG excerpt
- Config: `.env.example` documents `APP_ENV, CORS_ORIGINS, MAX_UPLOAD_MB, RATE_LIMIT, LOG_LEVEL`

---

## 2. GitHub Structure

### 2.1 Repository
- Name: `curvelab` (or `curve-fitting-with-graphs`), description + topics (`numerical-methods`, `least-squares`, `fastapi`, `react`, `curve-fitting`), About links to live demo
- Default branch `main` (protected: PR + CI required); working branches `feat/*`, `fix/*`, `docs/*`, `chore/*`
- **Conventional Commits** throughout, e.g.:
  - `feat(math): implement Gaussian elimination with partial pivoting and step recording`
  - `feat(ui): add animated result cards with count-up metrics`
  - `fix(export): escape CSV formula-injection characters`
  - `docs: add deployment guide for VPS with Nginx and certbot`
- Milestone-based commit history that tells a story (repo reviewers read commit logs)

### 2.2 Community/Governance Files (all at root)
| File | Content plan |
|---|---|
| `README.md` | See §3 |
| `LICENSE` | MIT |
| `.gitignore` | Python + Node + env + build artifacts + IDE |
| `CHANGELOG.md` | Keep a Changelog format, SemVer; v0.1.0 → v1.0.0 milestones |
| `CONTRIBUTING.md` | Setup, branch/commit conventions, test requirements, PR checklist |
| `CODE_OF_CONDUCT.md` | Contributor Covenant 2.1 |
| `SECURITY.md` | Supported versions, private disclosure email, response SLA |
| `.github/ISSUE_TEMPLATE/` | bug_report.yml, feature_request.yml |
| `.github/PULL_REQUEST_TEMPLATE.md` | Summary, screenshots, test evidence checklist |
| `.github/workflows/` | ci.yml, deploy.yml |

### 2.3 Project Wiki Structure
```
Home                       # overview + navigation
├── Getting-Started        # install & run (local, Docker)
├── User-Guide             # input, fitting, graphs, exports (with GIFs)
├── Mathematical-Background# derivations: linear, polynomial, exponential LSQ
├── Architecture           # diagrams, layer rules, data flow
├── API-Reference          # endpoint docs + link to /api/docs
├── Deployment-Guide       # Render, Railway, VPS, Azure
├── Testing-Guide          # how to run/extend tests
└── Roadmap                # v2 ideas (history DB, more models, i18n)
```

---

## 3. README Plan (section-by-section blueprint)

1. **Hero block** — centered logo, project name, one-line tagline, badge row (CI status, coverage, Python 3.12, FastAPI, React, License MIT, Live Demo)
2. **Screenshot strip** — placeholders: `docs/screenshots/landing.png`, `workspace.png`, `graph.png`, `report-pdf.png` (with capture checklist so they get made)
3. **Overview** — what it is, course context, live demo link
4. **Features** — grouped bullets: Fitting Engine / Step-by-Step Math / Interactive Graphs / Data Import / Exports & Reports / Premium UI
5. **How It Works** — brief math explainer with the three normal-equation systems (rendered via GitHub LaTeX)
6. **Tech Stack** — table with rationale one-liners
7. **Installation** — prerequisites; Quick Start (Docker one-liner); Manual dev setup (backend + frontend)
8. **Usage** — 5-step walkthrough with mini screenshots/GIF
9. **API** — endpoint table + example curl for `/fit` + link to Swagger
10. **Folder Structure** — condensed tree with one-line notes
11. **Testing** — `make test`, coverage statement
12. **Deployment** — links to wiki guide + Render deploy button
13. **Screenshots gallery** (collapsible `<details>`)
14. **Roadmap / Future Improvements** — session history DB, power/log models, weighted LSQ, PWA offline, i18n, shareable result links
15. **Contributing · License · Acknowledgements** — course/instructor line, library credits
