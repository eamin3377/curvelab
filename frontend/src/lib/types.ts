// Shared types, mirroring the FastAPI contract in backend/app/schemas.
// The frontend renders exactly what the API returns; nothing is recomputed
// client-side except live prediction evaluation from server coefficients.

export type ModelId = 'linear' | 'polynomial' | 'exponential'

export interface Point {
  x: number
  y: number
}

export const MODEL_META: Record<ModelId, { label: string; formula: string }> = {
  linear: { label: 'Linear', formula: 'y = a + bx' },
  polynomial: { label: 'Polynomial', formula: 'y = a_0 + a_1x + a_2x^2' },
  exponential: { label: 'Exponential', formula: 'y = ae^{bx}' },
}

export interface FitRequestPayload {
  x: number[]
  y: number[]
  model: ModelId
  degree: number
  precision: number
  options: { remove_duplicates: boolean; confidence_band: boolean }
}

export interface CleaningReport {
  duplicates_removed: number
  empty_dropped: number
  non_numeric_dropped: number
}

export interface ApiCoefficient {
  name: string
  value: number
}

export interface ApiSummation {
  key: string
  latex: string
  value: number
}

export interface ApiSolverStep {
  kind: string
  description: string
  matrix: number[][]
}

export interface ApiStep {
  index: number
  title: string
  description: string
  latex: string
}

export interface ApiMetrics {
  r2: number
  adj_r2: number | null
  rmse: number
  mse: number
  mae: number
  sse: number
  sst: number
}

export interface ApiCalculationTable {
  columns: string[]
  rows: number[][]
  sums: number[]
  total_rows: number
  truncated: boolean
}

export interface ApiGraph {
  scatter_x: number[]
  scatter_y: number[]
  curve_x: number[]
  curve_y: number[]
  residuals: number[]
  confidence_band: { upper: number[] | null; lower: number[] | null; approximate: boolean } | null
}

export interface ApiFitResult {
  model: ModelId
  degree: number
  n: number
  cleaning_report: CleaningReport
  coefficients: ApiCoefficient[]
  equation: { plain: string; latex: string }
  summations: ApiSummation[]
  normal_equations: {
    matrix: number[][]
    vector: number[]
    latex_symbolic: string
    latex_substituted: string
  }
  solver: {
    method: string
    condition_warning: string | null
    steps: ApiSolverStep[]
  }
  metrics: ApiMetrics
  calculation_table: ApiCalculationTable
  steps: ApiStep[]
  graph: ApiGraph
  notes: string[]
}

export interface ApiProblem {
  type: string
  title: string
  detail: string
  field?: string | null
  offending_indices?: number[]
}

export interface ParsedDatasetResponse {
  x: number[]
  y: number[]
  n: number
  cleaning_report: CleaningReport
}

export interface SampleSummary {
  id: string
  name: string
  description: string
  model: ModelId
  n: number
}

export interface SampleDatasetResponse extends SampleSummary {
  x: number[]
  y: number[]
}

export interface ReportMetaPayload {
  title: string
  author: string
  student_id: string
  course: string
  institution: string
  date: string
}

export type ExportFormat = 'pdf' | 'docx' | 'xlsx' | 'csv' | 'json' | 'txt'

export function evaluateModel(
  model: ModelId,
  coefficients: ApiCoefficient[],
  x: number,
): number {
  // Evaluate the fitted model at x using server-computed coefficients.
  if (model === 'exponential') {
    const [a, b] = coefficients.map((c) => c.value)
    return a * Math.exp(b * x)
  }
  return coefficients.reduce((acc, c, k) => acc + c.value * Math.pow(x, k), 0)
}
