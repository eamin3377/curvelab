import { useCallback, useRef, useState } from 'react'
import { ApiError, fitCurve } from '../../lib/api'
import type {
  ApiFitResult,
  ApiProblem,
  FitRequestPayload,
  ModelId,
  Point,
} from '../../lib/types'

export type FitStatus = 'idle' | 'fitting' | 'ready'

export interface CleaningNote {
  removedDuplicates: number
  droppedEmpty: number
}

// Manual entry starts with blank rows (NaN renders as an empty input);
// sample datasets are loaded explicitly via the Samples tab.
const BLANK_ROWS: Point[] = [
  { x: NaN, y: NaN },
  { x: NaN, y: NaN },
  { x: NaN, y: NaN },
]

export function validPoints(pts: Point[]): Point[] {
  return pts.filter((p) => Number.isFinite(p.x) && Number.isFinite(p.y))
}

export function buildFitRequest(
  points: Point[],
  model: ModelId,
  degree: number,
): FitRequestPayload {
  return {
    x: points.map((p) => p.x),
    y: points.map((p) => p.y),
    model,
    degree,
    precision: 4,
    options: { remove_duplicates: true, confidence_band: true },
  }
}

export function useWorkspace() {
  const [points, setPoints] = useState<Point[]>(BLANK_ROWS)
  const [model, setModel] = useState<ModelId>('linear')
  const [degree, setDegree] = useState(2)
  const [status, setStatus] = useState<FitStatus>('idle')
  const [result, setResult] = useState<ApiFitResult | null>(null)
  const [cleaning, setCleaning] = useState<CleaningNote | null>(null)
  const [problem, setProblem] = useState<ApiProblem | null>(null)
  const requestRef = useRef<FitRequestPayload | null>(null)
  const runId = useRef(0)

  const fit = useCallback(
    async (pts: Point[] = points, m: ModelId = model, deg: number = degree) => {
      const valid = validPoints(pts)
      if (valid.length < 2) return
      const id = ++runId.current
      setStatus('fitting')
      setProblem(null)
      const payload = buildFitRequest(valid, m, deg)
      try {
        const res = await fitCurve(payload)
        if (id !== runId.current) return // a newer fit superseded this one
        requestRef.current = payload
        setResult(res)
        const r = res.cleaning_report
        setCleaning(
          r.duplicates_removed + r.empty_dropped + r.non_numeric_dropped > 0
            ? { removedDuplicates: r.duplicates_removed, droppedEmpty: r.empty_dropped + r.non_numeric_dropped }
            : null,
        )
        setStatus('ready')
      } catch (err) {
        if (id !== runId.current) return
        setProblem(
          err instanceof ApiError
            ? err.problem
            : { type: 'network_error', title: 'Backend unreachable', detail: 'Could not reach the API. Is the server running on port 8000?' },
        )
        setStatus(points.length >= 2 ? 'idle' : 'idle')
      }
    },
    [points, model, degree],
  )

  const loadPoints = useCallback(
    (pts: Point[], note?: CleaningNote, nextModel?: ModelId) => {
      runId.current++ // cancel any in-flight fit for the previous dataset
      setPoints(pts)
      setCleaning(note && (note.removedDuplicates > 0 || note.droppedEmpty > 0) ? note : null)
      setProblem(null)
      setResult(null)
      setStatus('idle')
      if (nextModel) setModel(nextModel)
    },
    [],
  )

  const clearProblem = useCallback(() => setProblem(null), [])

  return {
    points,
    setPoints,
    model,
    setModel,
    degree,
    setDegree,
    status,
    result,
    cleaning,
    setCleaning,
    problem,
    clearProblem,
    fit,
    loadPoints,
    lastRequest: requestRef,
  }
}
