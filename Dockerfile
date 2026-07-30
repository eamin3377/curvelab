# syntax=docker/dockerfile:1

# ── Stage 1: build the React frontend ──────────────────────────────
FROM node:22-alpine AS frontend
WORKDIR /build

# Install deps first for better layer caching.
COPY frontend/package.json frontend/package-lock.json ./
RUN npm ci

# Same-origin API: the backend serves the built app, so calls go to /api/v1.
COPY frontend/ ./
ENV VITE_API_URL=/api/v1
RUN npm run build

# ── Stage 2: FastAPI backend + built frontend ──────────────────────
FROM python:3.12-slim AS runtime
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
WORKDIR /app

COPY backend/requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/app ./app
COPY --from=frontend /build/dist ./static

# Pre-compress static assets with gzip so the server sends ~360 KB
# instead of ~1.1 MB over the wire. Caddy/FastAPI don't re-compress
# FileResponse, so we serve .gz files directly with correct headers.
RUN find ./static -type f \( -name '*.js' -o -name '*.css' -o -name '*.svg' -o -name '*.woff2' -o -name '*.html' \) -exec gzip -kf {} \;

EXPOSE 8000
# Railway injects $PORT; default to 8000 locally.
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
