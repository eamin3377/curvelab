// API client for the CurveLab FastAPI backend.

import type {
  ApiFitResult,
  ApiProblem,
  ExportFormat,
  FitRequestPayload,
  ParsedDatasetResponse,
  ReportMetaPayload,
  SampleDatasetResponse,
  SampleSummary,
} from './types'

// GitHub Pages is static-only, so the backend must be hosted elsewhere.
// Set VITE_API_URL to the backend URL (e.g. your Replit/Railway URL).
// Falls back to localhost for dev, and same-origin /api/v1 for single-host.
const BASE_URL =
  import.meta.env.VITE_API_URL ??
  (import.meta.env.PROD ? '/api/v1' : 'http://localhost:8000/api/v1')

export class ApiError extends Error {
  problem: ApiProblem

  constructor(problem: ApiProblem, status: number) {
    super(problem.detail || problem.title)
    this.problem = problem
    this.name = `ApiError(${status})`
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json', ...init?.headers },
    ...init,
  })
  if (!res.ok) {
    let problem: ApiProblem
    try {
      problem = (await res.json()) as ApiProblem
    } catch {
      problem = { type: 'network_error', title: 'Request failed', detail: res.statusText }
    }
    throw new ApiError(problem, res.status)
  }
  return (await res.json()) as T
}

export type RetryNotifier = (attempt: number) => void

// The free Replit backend sleeps when idle; while asleep it returns an HTML
// placeholder page (or the browser blocks it via CORS), surfacing as a
// network_error. Retry for up to 90s so a sleeping backend gets time to wake.
function isRetryable(err: unknown): boolean {
  return (
    err instanceof TypeError ||
    (err instanceof ApiError && err.problem.type === 'network_error')
  )
}

async function requestWithRetry<T>(
  path: string,
  init: RequestInit | undefined,
  onRetrying?: RetryNotifier,
): Promise<T> {
  const deadline = Date.now() + 90_000
  let attempt = 0
  for (;;) {
    try {
      return await request<T>(path, init)
    } catch (err) {
      if (!isRetryable(err) || Date.now() >= deadline) throw err
      attempt += 1
      onRetrying?.(attempt)
      await new Promise((resolve) => setTimeout(resolve, 3000))
    }
  }
}

export function fitCurve(
  payload: FitRequestPayload,
  onRetrying?: RetryNotifier,
): Promise<ApiFitResult> {
  return requestWithRetry<ApiFitResult>(
    '/fit',
    { method: 'POST', body: JSON.stringify(payload) },
    onRetrying,
  )
}

export function parseText(text: string): Promise<ParsedDatasetResponse> {
  return request<ParsedDatasetResponse>('/data/parse-text', {
    method: 'POST',
    body: JSON.stringify({ text }),
  })
}

export async function parseFile(file: File): Promise<ParsedDatasetResponse> {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${BASE_URL}/data/parse-file`, { method: 'POST', body: form })
  if (!res.ok) {
    const problem = (await res.json().catch(() => ({
      type: 'network_error',
      title: 'Upload failed',
      detail: res.statusText,
    }))) as ApiProblem
    throw new ApiError(problem, res.status)
  }
  return (await res.json()) as ParsedDatasetResponse
}

export function fetchSamples(): Promise<SampleSummary[]> {
  return request<SampleSummary[]>('/data/samples')
}

export function fetchSample(id: string): Promise<SampleDatasetResponse> {
  return request<SampleDatasetResponse>(`/data/samples/${encodeURIComponent(id)}`)
}

export interface ExportPayload {
  fit_request: FitRequestPayload
  report_meta: ReportMetaPayload
  chart_png_base64?: string | null
}

export async function exportReport(
  format: ExportFormat,
  payload: ExportPayload,
): Promise<{ blob: Blob; filename: string }> {
  const res = await fetch(`${BASE_URL}/export/${format}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })
  if (!res.ok) {
    const problem = (await res.json().catch(() => ({
      type: 'network_error',
      title: 'Export failed',
      detail: res.statusText,
    }))) as ApiProblem
    throw new ApiError(problem, res.status)
  }
  const disposition = res.headers.get('Content-Disposition') ?? ''
  const match = /filename="([^"]+)"/.exec(disposition)
  return {
    blob: await res.blob(),
    filename: match?.[1] ?? `curvelab-export.${format}`,
  }
}

export function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob)
  const anchor = document.createElement('a')
  anchor.href = url
  anchor.download = filename
  document.body.appendChild(anchor)
  anchor.click()
  anchor.remove()
  URL.revokeObjectURL(url)
}
