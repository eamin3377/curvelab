import { motion } from 'framer-motion'
import { Activity, Crosshair, Gauge, Target } from 'lucide-react'
import { Card } from '../../components/ui/Card'
import { CountUp } from '../../components/ui/CountUp'
import { Tooltip } from '../../components/ui/Tooltip'
import type { ApiFitResult } from '../../lib/types'

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.06 } },
}
const item = {
  hidden: { opacity: 0, y: 14 },
  show: { opacity: 1, y: 0, transition: { type: 'spring' as const, stiffness: 260, damping: 24 } },
}

export function MetricCards({ result }: { result: ApiFitResult }) {
  const metrics = [
    {
      label: 'R² Score',
      name: 'Coefficient of determination',
      hint: 'Proportion of variance explained by the fit. Closer to 1 is better.',
      value: result.metrics.r2,
      digits: 4,
      icon: Gauge,
      accent: 'from-indigo-500 to-violet-500',
      good: result.metrics.r2 > 0.95,
    },
    {
      label: 'RMSE',
      name: 'Root Mean Square Error',
      hint: 'Typical size of the residuals, in y units.',
      value: result.metrics.rmse,
      digits: 4,
      icon: Target,
      accent: 'from-sky-500 to-cyan-500',
    },
    {
      label: 'MAE',
      name: 'Mean Absolute Error',
      hint: 'Average absolute deviation of predictions.',
      value: result.metrics.mae,
      digits: 4,
      icon: Crosshair,
      accent: 'from-violet-500 to-fuchsia-500',
    },
    {
      label: 'MSE',
      name: 'Mean Squared Error',
      hint: 'Average of squared residuals. Penalizes large errors.',
      value: result.metrics.mse,
      digits: 4,
      icon: Activity,
      accent: 'from-emerald-500 to-teal-500',
    },
  ]

  return (
    <motion.div
      variants={container}
      initial="hidden"
      animate="show"
      className="grid grid-cols-2 gap-4 xl:grid-cols-4"
    >
      {metrics.map((m) => (
        <motion.div key={m.label} variants={item} className="h-full">
          <Card hover className="relative flex h-full flex-col p-5">
            <div className="pointer-events-none absolute inset-0 overflow-hidden rounded-2xl">
              <div
                className={`absolute -right-6 -top-6 h-20 w-20 rounded-full bg-gradient-to-br ${m.accent} opacity-[0.07]`}
              />
            </div>
            <div className="flex items-center justify-between">
              <Tooltip label={m.hint}>
                <span className="cursor-help text-xs font-semibold uppercase tracking-wider text-slate-400 underline decoration-dotted decoration-slate-300 underline-offset-4">
                  {m.label}
                </span>
              </Tooltip>
              <span
                className={`flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br ${m.accent} text-white shadow-sm`}
              >
                <m.icon className="h-4 w-4" />
              </span>
            </div>
            <p className="mt-3 font-mono text-2xl font-semibold tracking-tight text-slate-900">
              <CountUp value={m.value} digits={m.digits} />
            </p>
            <p className="mt-1 text-xs font-medium text-slate-400">{m.name}</p>
            <p
              className={`mt-1 min-h-4 text-xs font-medium ${
                m.good === undefined ? 'invisible' : 'text-emerald-600'
              }`}
              aria-hidden={m.good === undefined}
            >
              {m.good === undefined ? 'placeholder' : m.good ? 'Excellent fit' : 'Acceptable fit'}
            </p>
          </Card>
        </motion.div>
      ))}
    </motion.div>
  )
}
