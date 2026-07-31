import { motion } from 'framer-motion'
import { FlaskConical } from 'lucide-react'
import { cn } from '../../lib/utils'
import { SAMPLE_DATASETS } from '../../lib/samples'
import type { ModelId, Point } from '../../lib/types'

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
  const pick = (id: string) => {
    const sample = SAMPLE_DATASETS.find((s) => s.id === id)
    if (!sample) return
    onLoad(
      sample.x.map((x, i) => ({ x, y: sample.y[i] })),
      sample.model,
    )
  }

  return (
    <div>
      <div className="grid grid-cols-1 gap-3">
        {SAMPLE_DATASETS.map((s) => {
          const tone = TONES[s.model]
          return (
            <motion.button
              key={s.id}
              type="button"
              whileHover={{ y: -3 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => pick(s.id)}
              className="group flex w-full items-start gap-3 rounded-xl border border-slate-200/70 bg-white p-4 text-left transition-shadow hover:shadow-lg hover:shadow-slate-200/60"
            >
              <span className={cn('flex h-10 w-10 shrink-0 items-center justify-center rounded-xl transition-transform group-hover:scale-110', tone.icon)}>
                <FlaskConical className="h-5 w-5" />
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
