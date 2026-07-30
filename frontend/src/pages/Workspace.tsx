import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { AlertCircle, LineChart, X } from 'lucide-react'
import { PageTransition } from '../components/layout/PageTransition'
import { InputPanel } from '../features/workspace/InputPanel'
import { MetricCards } from '../features/workspace/MetricCards'
import { EquationCard } from '../features/workspace/EquationCard'
import { GraphCard } from '../features/workspace/GraphCard'
import { PredictionCard } from '../features/workspace/PredictionCard'
import { TablesCard } from '../features/workspace/TablesCard'
import { StepsCard } from '../features/workspace/StepsCard'
import { ExportBar } from '../features/workspace/ExportBar'
import { SkeletonDashboard } from '../features/workspace/SkeletonDashboard'
import { useWorkspace } from '../features/workspace/useWorkspace'
import type { Point } from '../lib/types'

const stagger = {
  hidden: {},
  show: { transition: { staggerChildren: 0.07 } },
}
const rise = {
  hidden: { opacity: 0, y: 18 },
  show: { opacity: 1, y: 0, transition: { type: 'spring' as const, stiffness: 240, damping: 26 } },
}

export function Workspace() {
  const ws = useWorkspace()
  const [prediction, setPrediction] = useState<Point | null>(null)

  return (
    <PageTransition>
      <div className="bg-hero min-h-screen pb-28 pt-24">
        <div className="mx-auto max-w-7xl px-4 sm:px-6 lg:px-8 2xl:max-w-[1600px]">
          <div className="mb-8">
            <h1 className="text-2xl font-bold tracking-tight text-slate-900 sm:text-3xl">
              Workspace
            </h1>
            <p className="mt-1.5 text-[15px] text-slate-500">
              Load a dataset, choose a model, and solve the least squares fit instantly.
            </p>
          </div>

          <div className="grid min-w-0 gap-6 lg:grid-cols-[380px_1fr] lg:items-start 2xl:grid-cols-[440px_1fr] 2xl:gap-8">
            <div className="min-w-0">
              <InputPanel
                points={ws.points}
                onPointsChange={(pts) => {
                  ws.setPoints(pts)
                }}
                onLoad={(pts, note, model) => {
                  ws.loadPoints(pts, note, model)
                  setPrediction(null)
                }}
                model={ws.model}
                onModelChange={(m) => {
                  ws.setModel(m)
                  setPrediction(null)
                }}
                status={ws.status}
                cleaning={ws.cleaning}
                onDismissCleaning={() => ws.setCleaning(null)}
                onFit={() => void ws.fit()}
              />
            </div>

            <div className="min-w-0 overflow-x-hidden">
              <AnimatePresence>
                {ws.problem && (
                  <motion.div
                    initial={{ opacity: 0, y: -8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -8 }}
                    role="alert"
                    className="mb-6 flex items-start gap-3 rounded-2xl border border-red-200/70 bg-red-50/80 px-5 py-4 shadow-sm"
                  >
                    <AlertCircle className="mt-0.5 h-5 w-5 shrink-0 text-red-500" />
                    <div className="min-w-0">
                      <p className="text-sm font-bold text-red-800">{ws.problem.title}</p>
                      <p className="mt-0.5 text-[13px] leading-snug text-red-700">
                        {ws.problem.detail}
                        {ws.problem.offending_indices && ws.problem.offending_indices.length > 0 && (
                          <span className="font-mono">
                            {' '}(rows: {ws.problem.offending_indices.map((i) => i + 1).join(', ')})
                          </span>
                        )}
                      </p>
                    </div>
                    <button
                      onClick={ws.clearProblem}
                      aria-label="Dismiss error"
                      className="ml-auto text-red-400 transition-colors hover:text-red-600"
                    >
                      <X className="h-4 w-4" />
                    </button>
                  </motion.div>
                )}
              </AnimatePresence>

              <AnimatePresence mode="wait">
                {ws.status === 'fitting' && (
                  <motion.div key="skeleton" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
                    <SkeletonDashboard />
                  </motion.div>
                )}

                {ws.status === 'ready' && ws.result && (
                  <motion.div
                    key="results"
                    variants={stagger}
                    initial="hidden"
                    animate="show"
                    className="space-y-6"
                  >
                    <MetricCards result={ws.result} />
                    <motion.div variants={rise}>
                      <EquationCard result={ws.result} />
                    </motion.div>
                    <motion.div variants={rise}>
                      <GraphCard result={ws.result} prediction={prediction} />
                    </motion.div>
                    <motion.div variants={rise} className="grid gap-6 xl:grid-cols-[1fr_340px] 2xl:grid-cols-[1fr_360px]">
                      <TablesCard result={ws.result} />
                      <PredictionCard result={ws.result} onPredict={setPrediction} />
                    </motion.div>
                    <motion.div variants={rise}>
                      <StepsCard result={ws.result} />
                    </motion.div>
                  </motion.div>
                )}

                {ws.status === 'idle' && (
                  <motion.div
                    key="empty"
                    initial={{ opacity: 0, y: 14 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0 }}
                    className="flex min-h-[520px] flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-200 bg-white/60 px-6 text-center"
                  >
                    <div className="relative">
                      <div className="absolute -inset-6 rounded-full bg-gradient-to-br from-indigo-100 to-sky-100 opacity-60 blur-2xl" />
                      <div className="relative flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-500 text-white shadow-[0_10px_30px_rgb(79_70_229/0.35)]">
                        <LineChart className="h-7 w-7" />
                      </div>
                    </div>
                    <h2 className="mt-6 text-xl font-bold text-slate-900">Ready when you are</h2>
                    <p className="mt-2 max-w-sm text-[14.5px] leading-relaxed text-slate-500">
                      Your dataset is loaded. Press{' '}
                      <span className="font-semibold text-indigo-600">Fit Curve</span> to solve the
                      normal equations and reveal the full analysis.
                    </p>
                  </motion.div>
                )}
              </AnimatePresence>
            </div>
          </div>
        </div>

        {ws.status === 'ready' && <ExportBar lastRequest={ws.lastRequest.current} />}
      </div>
    </PageTransition>
  )
}
