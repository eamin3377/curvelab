import { useEffect, useState } from 'react'
import { motion } from 'framer-motion'
import { FlaskConical, Loader2 } from 'lucide-react'
import { cn } from '../../lib/utils'
import { ApiError, fetchSample, fetchSamples } from '../../lib/api'
import type { ModelId, Point, SampleSummary } from '../../lib/types'

const TONES: Record<ModelId, { icon: string; ring: string }> = {
  linear: { icon: 'bg-indigo-50 text-indigo-600', ring: 'ring-indigo-500/70' },
  polynomial: { icon: 'bg-violet-50 text-violet-600', ring: 'ring-violet-500/70' },
  exponential: { icon: 'bg-cyan-50 text-cyan-600', ring: 'ring-cyan-500/70' },
  exponential_abx: { icon: 'bg-teal-50 text-teal-600', ring: 'ring-teal-500/70' },
  power: { icon: 'bg-amber-50 text-amber-600', ring: 'ring-amber-500/70' },
}

export function SamplesPanel({
  onLoad,
}: {
  onLoad: (pts: Point[], model: ModelId) => void
}) {
  const [samples, setSamples] = useState<SampleSummary[] | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [busyId, setBusyId] = useState<string | null>(null)

  useEffect(() => {
    let cancelled = false
    fetchSamples()
      .then((list) => {
        if (!cancelled) setSamples(list)
      })
      .catch((err) => {
        if (!cancelled)
          setError(err instanceof ApiError ? err.problem.detail : 'Samples unavailable.')
      })
    return () => {
      cancelled = true
    }
  }, [])

  const pick = async (id: string) => {
    setBusyId(id)
    setError(null)
    try {
      const sample = await fetchSample(id)
      onLoad(
        sample.x.map((x, i) => ({ x, y: sample.y[i] })),
        sample.model,
      )
    } catch (err) {
      setError(err instanceof ApiError ? err.problem.detail : 'Could not load sample.')
    } finally {
      setBusyId(null)
    }
  }

  if (samples === null && !error) {
    return (
      <div className="flex items-center justify-center gap-2 py-10 text-sm text-slate-400">
        <Loader2 className="h-4 w-4 animate-spin" />
        Loading sample datasets…
      </div>
    )
  }

  return (
    <div>
      {error && <p className="mb-3 text-sm text-red-600">{error}</p>}
      <div className="grid grid-cols-1 gap-3">
        {samples?.map((s) => {
          const tone = TONES[s.model]
          return (
            <motion.button
              key={s.id}
              type="button"
              whileHover={{ y: -3 }}
              whileTap={{ scale: 0.98 }}
              disabled={busyId !== null}
              onClick={() => void pick(s.id)}
              className="group flex w-full items-start gap-3 rounded-xl border border-slate-200/70 bg-white p-4 text-left transition-shadow hover:shadow-lg hover:shadow-slate-200/60 disabled:opacity-60"
            >
              <span className={cn('flex h-10 w-10 shrink-0 items-center justify-center rounded-xl transition-transform group-hover:scale-110', tone.icon)}>
                {busyId === s.id ? <Loader2 className="h-5 w-5 animate-spin" /> : <FlaskConical className="h-5 w-5" />}
              </span>
              <span className="min-w-0 flex-1">
                <span className="block text-sm font-semibold text-slate-900">{s.name}</span>
                <span className="mt-0.5 block text-xs leading-relaxed text-slate-500">{s.description}</span>
                <span className="mt-1.5 block text-[11px] font-semibold uppercase tracking-wide text-slate-400">
                  {s.model} · {s.n} points
                </span>
              </span>
            </motion.button>
          )
        })}
      </div>
    </div>
  )
}
