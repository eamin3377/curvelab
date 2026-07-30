# CurveLab — Architecture Documentation

Complete software architecture for **Curve Fitting with Graphs** (Linear, Polynomial & Exponential via Least Squares), a university Numerical Methods project built as a full-stack Python web application (FastAPI + React).

## Document Index

| # | Document | Covers |
|---|---|---|
| 1 | [SRS & Requirements](01-srs-and-requirements.md) | Project overview, tech stack decisions, Functional & Non-Functional Requirements |
| 2 | [UI & Design System](02-ui-design-system.md) | UI requirements, color palette, typography, page specs, Animation, Responsive, Accessibility |
| 3 | [Backend & Engines](03-backend-and-engines.md) | Backend architecture, Mathematical Engine, Graph Engine, Export Engine |
| 4 | [Structure, API, Security, Performance](04-structure-api-security-performance.md) | Folder structure, API design, Database decision, Security, Performance budgets |
| 5 | [Deployment, GitHub, README](05-deployment-github-readme.md) | Deployment plan (Docker/Render/VPS/Azure), GitHub structure, Wiki, README blueprint |
| 6 | [Testing, Docs, Roadmap](06-testing-docs-roadmap.md) | Testing plan, Documentation plan, 10-milestone implementation roadmap |

## Quick Facts

- **Backend:** Python 3.12, FastAPI, NumPy (own Gaussian elimination solver), pandas, ReportLab, python-docx, openpyxl, Kaleido
- **Frontend:** React + Vite + TypeScript + TailwindCSS, Plotly.js, Framer Motion, KaTeX
- **Database:** None in v1 (stateless compute); SQLite history documented as v2
- **Deployment:** Localhost → Docker → Render/Railway → VPS + Nginx + HTTPS on custom domain
- **Implementation starts at:** Milestone M1 (see document 6, section 3)
