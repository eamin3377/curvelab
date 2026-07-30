import { useMemo, useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { ArrowRight, Wand2 } from 'lucide-react'
import { Card, CardHeader } from '../../components/ui/Card'
import { Badge } from '../../components/ui/Badge'
import { evaluateModel, type ApiFitResult, type Point } from '../../lib/types'
import { formatNumber } from '../../lib/utils'

export function PredictionCard({
  result,
  onPredict,
}: {
  result: ApiFitResult
  onPredict: (p: Point | null) => void
}) {
  const [input, setInput] = useState('')
  const x = Number(input)
  const valid = input.trim() !== '' && Number.isFinite(x)
  const yHat = valid ? evaluateModel(result.model, result.coefficients, x) : null

  const { min, max } = useMemo(() => {
    const xs = result.graph.scatter_x
    return { min: Math.min(...xs), max: Math.max(...xs) }
  }, [result])
  const extrapolated = valid && (x < min || x > max)

  return (
    <Card className="flex h-full flex-col">
      <CardHeader
        title="Predict"
        subtitle="Evaluate ŷ at any x"
        icon={<Wand2 className="h-4 w-4" />}
      />
      <div className="flex flex-1 flex-col px-6 py-5">
        <label htmlFor="predict-x" className="mb-2 text-xs font-semibold uppercase tracking-wide text-slate-400">
          x value
        </label>
        <div className="flex items-center gap-3">
          <input
            id="predict-x"
            type="number"
            value={input}
            onChange={(e) => {
              setInput(e.target.value)
              const v = Number(e.target.value)
              onPredict(
                e.target.value.trim() !== '' && Number.isFinite(v)
                  ? { x: v, y: evaluateModel(result.model, result.coefficients, v) }
                  : null,
              )
            }}
            placeholder={`e.g. ${formatNumber((min + max) / 2, 1)}`}
            className="h-11 w-full rounded-xl border border-slate-200 bg-slate-50/60 px-4 font-mono text-[15px] text-slate-800 placeholder:text-slate-300 transition-colors hover:border-slate-300 focus:border-indigo-400 focus:bg-white"
          />
          <ArrowRight className="h-4 w-4 shrink-0 text-slate-300" />
        </div>

        <div className="mt-4 flex flex-1 flex-col items-center justify-center rounded-2xl bg-gradient-to-br from-slate-50 to-indigo-50/40 px-4 py-6 ring-1 ring-slate-100">
          <AnimatePresence mode="wait">
            {yHat !== null ? (
              <motion.div
                key={yHat}
                initial={{ opacity: 0, y: 10, scale: 0.96 }}
                animate={{ opacity: 1, y: 0, scale: 1 }}
                exit={{ opacity: 0, y: -8 }}
                transition={{ type: 'spring', stiffness: 300, damping: 26 }}
                className="text-center"
              >
                <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">Predicted ŷ</p>
                <p className="mt-1 font-mono text-3xl font-bold tracking-tight text-indigo-600">
                  {formatNumber(yHat)}
                </p>
                {extrapolated && (
                  <Badge tone="amber" className="mt-3">
                    Extrapolation — outside [{formatNumber(min, 1)}, {formatNumber(max, 1)}]
                  </Badge>
                )}
              </motion.div>
            ) : (
              <motion.p
                key="placeholder"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="text-center text-sm text-slate-400"
              >
                Enter an x value to evaluate
                <br />
                the fitted equation
              </motion.p>
            )}
          </AnimatePresence>
        </div>
      </div>
    </Card>
  )
}
