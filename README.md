# CurveLab

**Curve fitting, beautifully solved.** CurveLab is a least squares curve fitting
web app: enter your data points, pick a model, and it computes every summation,
solves the normal equations step by step, draws an interactive regression graph,
and exports a university-ready report.

Live app: **https://eamin3377.github.io/curvelab/**

## What it does

- **Five fitting models** — Linear `y = a + bx`, Polynomial (degrees 2–6), and the
  exponential family: `y = aeᵇˣ`, `y = abˣ`, `y = axᵇ` (power law)
- **Step-by-step solutions** — normal equations, summation table
  (Σx, Σy, Σxy, Σx², …), Gaussian elimination, final coefficients
- **Interactive graph** — scatter points, fitted curve, confidence band, residuals;
  zoom, pan, hover, export as image
- **Metrics** — R², RMSE, MAE, MSE
- **Prediction** — type any x, get the predicted y with a chart marker
- **Data input 4 ways** — manual grid, paste from Excel, file upload
  (CSV / TXT / JSON), or built-in sample datasets (bundled, work offline)
- **Exports** — PDF report, Word report, Excel workbook, CSV, JSON, plain text, print

## Tech stack

| Part      | Technology                                              |
| --------- | ------------------------------------------------------- |
| Frontend  | React 19, TypeScript, Vite, Tailwind CSS 4, Framer Motion, Plotly, KaTeX |
| Backend   | Python 3.12, FastAPI, NumPy (least squares engine), report generators (ReportLab, python-docx, openpyxl) |
| Hosting   | Frontend: GitHub Pages · Backend: Replit                |

## Project layout

```
frontend/          React app (Vite)
  src/pages/       Landing, Workspace, Methods, About, NotFound
  src/features/    Workspace components (input panel, graph, steps, export bar…)
  src/lib/         API client, types, bundled sample datasets
backend/           FastAPI app
  app/api/routers/ REST endpoints under /api/v1 (fit, data, export, meta)
  app/engines/     Least squares math engines
  app/core/        Config, error types, sample datasets
  tests/           88 unit + integration tests
docs/              Design docs (SRS, UI system, backend notes, deployment)
.github/workflows/ GitHub Actions: auto-deploy frontend to GitHub Pages
.replit            Replit run config (single-process full-stack mode)
```

## Run it locally (development)

You need **Node.js 20+** and **Python 3.12+**.

**Terminal 1 — backend:**

```powershell
cd backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
uvicorn app.main:app --reload --port 8000
```

**Terminal 2 — frontend:**

```powershell
cd frontend
npm install
npm run dev
```

Open http://localhost:5173. The frontend talks to the backend at
`http://localhost:8000/api/v1` automatically in dev mode.

**Tests and checks:**

```powershell
cd backend;  pytest -q          # 88 tests
cd frontend; npm run build      # typecheck + production build
cd frontend; npm run lint       # oxlint
```

## How the current hosting works (your setup)

The app is split across two free hosts:

1. **Frontend → GitHub Pages** (static site, always on, free)
   - Every push to `main` runs `.github/workflows/deploy.yml`, which builds the
     frontend and publishes it to https://eamin3377.github.io/curvelab/
   - The build reads a **repository secret** named `VITE_API_URL` that tells the
     frontend where the backend lives. It is currently set to your Replit URL:
     `https://<your-repl-url>/api/v1`
   - To view or change it: GitHub repo → **Settings → Secrets and variables →
     Actions → VITE_API_URL**

2. **Backend → Replit** (runs the Python API)
   - The repo is imported as a Repl. The `.replit` file builds the frontend and
     serves everything with one command: `uvicorn app.main:app --port 3000`
   - **Important:** the free Replit tier **sleeps when idle**. The first Fit
     Curve click after a break wakes it up automatically (the app retries for
     90 seconds and shows "Waking up the compute server"). If the Repl has fully
     stopped, open the project in Replit and press **Run**, wait ~30 seconds,
     then use the site normally.

### CORS (required whenever the backend URL changes)

The backend only accepts requests from allowed origins. It reads them from the
environment variable `CURVELAB_CORS_ORIGINS`. Set it as a **Replit Secret**:

```json
CURVELAB_CORS_ORIGINS=["https://eamin3377.github.io", "http://localhost:5173"]
```

If you ever change domains, update this secret and restart the Repl.

## Host it yourself (all options)

### Option A — Everything on Replit (simplest, one process)

The backend can serve the frontend itself — no GitHub Pages needed:

1. Import this repo into Replit (the included `.replit` + `replit.nix` are ready).
2. Press **Run**. That's it — the Repl builds the frontend, copies it into
   `backend/static/`, and serves the whole app on one URL.
3. Your app is live at the Replit-provided URL. (Free tier sleeps when idle;
   Replit "Always On" or a Reserved VM removes that.)

### Option B — GitHub Pages + Replit (your current setup)

1. **Backend:** import the repo to Replit and press Run. Copy your Repl URL.
2. **GitHub secret:** repo → Settings → Secrets and variables → Actions → new
   secret `VITE_API_URL` = `https://<your-repl-url>/api/v1`
3. **Enable Pages:** repo → Settings → Pages → Source: **GitHub Actions**
4. Push to `main` (or run the "Deploy to GitHub Pages" workflow manually).
   Your site appears at `https://<username>.github.io/<repo>/`.
5. Set the `CURVELAB_CORS_ORIGINS` Replit secret to include your Pages origin
   (see the CORS section above).

### Option C — Any static host + any Python host

The same split works anywhere:

- **Frontend:** run `npm ci && npm run build` in `frontend/` with the env var
  `VITE_API_URL=https://<your-backend>/api/v1`, then upload `frontend/dist/`
  to Netlify / Vercel / Cloudflare Pages / any web server. If your host serves
  the site at a subpath, also set `VITE_BASE_URL=/your-subpath/` (defaults to
  `/curvelab/`).
- **Backend:** run `uvicorn app.main:app --host 0.0.0.0 --port $PORT` from
  `backend/` on Render / Railway / Fly.io / a VPS. Set `CURVELAB_CORS_ORIGINS`
  to your frontend's origin.

## Environment variables reference

| Variable                | Where    | Purpose                                        | Default                |
| ----------------------- | -------- | ---------------------------------------------- | ---------------------- |
| `VITE_API_URL`          | Frontend build (GitHub secret) | Full backend URL incl. `/api/v1` | `http://localhost:8000/api/v1` (dev) |
| `VITE_BASE_URL`         | Frontend build | Site base path (e.g. `/curvelab/`)            | `/curvelab/`           |
| `CURVELAB_CORS_ORIGINS` | Backend runtime | JSON list of allowed frontend origins      | `["http://localhost:5173", "http://127.0.0.1:5173"]` |
| `CURVELAB_MAX_UPLOAD_MB`| Backend runtime | Upload size cap                              | `10`                   |

## API quick reference

Interactive docs: `<backend-url>/api/docs` (Swagger UI).

| Endpoint                      | Method | Purpose                              |
| ----------------------------- | ------ | ------------------------------------ |
| `/api/v1/health`              | GET    | Health check (`{"status":"ok"}`)     |
| `/api/v1/fit`                 | POST   | Run a least squares fit              |
| `/api/v1/data/parse-text`     | POST   | Parse pasted text into a dataset     |
| `/api/v1/data/parse-file`     | POST   | Parse an uploaded file               |
| `/api/v1/data/samples`        | GET    | List sample datasets                 |
| `/api/v1/export/{format}`     | POST   | Export report (`pdf` `docx` `xlsx` `csv` `json` `txt`) |

## Troubleshooting

- **"Backend unreachable" / first fit is slow** → the Replit backend is asleep.
  The app retries automatically for 90s. If it still fails, open the Repl and
  press **Run**.
- **Buttons or pages look broken after an update** → hard refresh with
  **Ctrl+Shift+R** to clear the cached old JavaScript.
- **CORS error in browser console** → add your frontend's origin to the
  `CURVELAB_CORS_ORIGINS` Replit secret and restart the Repl.
- **Frontend deployed but API calls 404** → the `VITE_API_URL` GitHub secret is
  missing or wrong; update it and re-run the deploy workflow.

## Credits

Numerical Methods course project — Daffodil International University, Dept. of CSE.
MIT License.
