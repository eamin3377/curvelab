import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { AlertTriangle, Loader2, Sparkles, X } from 'lucide-react'
import { Card, CardHeader } from '../../components/ui/Card'
import { Button } from '../../components/ui/Button'
import { SegmentedControl } from '../../components/ui/SegmentedControl'
import { Equation } from '../../components/ui/Equation'
import { ManualGrid } from './ManualGrid'
import { PastePanel } from './PastePanel'
import { UploadZone } from './UploadZone'
import { SamplesPanel } from './SamplesPanel'
import { isExponentialFamily, MODEL_META, type ModelId, type Point } from '../../lib/types'
import type { CleaningNote, FitStatus } from './useWorkspace'
import { cn } from '../../lib/utils'

type InputTab = 'manual' | 'paste' | 'upload' | 'samples'

const tabs: Array<{ id: InputTab; label: string }> = [
  { id: 'manual', label: 'Manual' },
  { id: 'paste', label: 'Paste' },
  { id: 'upload', label: 'Upload' },
  { id: 'samples', label: 'Samples' },
]

export function InputPanel({
  points,
  onPointsChange,
  onLoad,
  model,
  onModelChange,
  status,
  cleaning,
  onDismissCleaning,
  onFit,
}: {
  points: Point[]
  onPointsChange: (pts: Point[]) => void
  onLoad: (pts: Point[], note?: CleaningNote, model?: ModelId) => void
  model: ModelId
  onModelChange: (m: ModelId) => void
  status: FitStatus
  cleaning: CleaningNote | null
  onDismissCleaning: () => void
  onFit: () => void
}) {
  const [tab, setTab] = useState<InputTab>('manual')

  return (
    <>
    <Card className="overflow-hidden">
      <CardHeader
        title="Dataset"
        subtitle={`${points.length} points loaded`}
        icon={<Sparkles className="h-4 w-4" />}
      />

      <div className="p-5">
        <div className="flex min-w-0 gap-1 rounded-xl bg-slate-100 p-1" role="tablist" aria-label="Data input method">
          {tabs.map((t) => (
            <button
              key={t.id}
              role="tab"
              aria-selected={tab === t.id}
              onClick={() => setTab(t.id)}
              className={cn(
                'relative min-w-0 flex-1 truncate rounded-lg py-1.5 text-[13px] font-semibold transition-colors',
                tab === t.id ? 'text-indigo-700' : 'text-slate-500 hover:text-slate-800',
              )}
            >
              {tab === t.id && (
                <motion.span
                  layoutId="input-tab"
                  className="absolute inset-0 rounded-lg bg-white shadow-sm ring-1 ring-slate-200/80"
                  transition={{ type: 'spring', stiffness: 400, damping: 32 }}
                />
              )}
              <span className="relative">{t.label}</span>
            </button>
          ))}
        </div>

        <AnimatePresence>
          {cleaning && (
            <motion.div
              initial={{ opacity: 0, height: 0 }}
              animate={{ opacity: 1, height: 'auto' }}
              exit={{ opacity: 0, height: 0 }}
              className="overflow-hidden"
            >
              <div className="mt-4 flex items-start gap-2.5 rounded-xl border border-amber-200/70 bg-amber-50/70 px-3.5 py-2.5">
                <AlertTriangle className="mt-0.5 h-4 w-4 shrink-0 text-amber-500" />
                <p className="text-[13px] leading-snug text-amber-800">
                  Data cleaned automatically:{' '}
                  {cleaning.removedDuplicates > 0 && `${cleaning.removedDuplicates} duplicate${cleaning.removedDuplicates > 1 ? 's' : ''} removed`}
                  {cleaning.removedDuplicates > 0 && cleaning.droppedEmpty > 0 && ' · '}
                  {cleaning.droppedEmpty > 0 && `${cleaning.droppedEmpty} invalid row${cleaning.droppedEmpty > 1 ? 's' : ''} dropped`}
                </p>
                <button
                  onClick={onDismissCleaning}
                  aria-label="Dismiss cleaning report"
                  className="ml-auto text-amber-400 transition-colors hover:text-amber-600"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        <div className="mt-5">
          <AnimatePresence mode="wait">
            <motion.div
              key={tab}
              initial={{ opacity: 0, y: 6 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -6 }}
              transition={{ duration: 0.18 }}
            >
              {tab === 'manual' && <ManualGrid points={points} onChange={onPointsChange} />}
              {tab === 'paste' && <PastePanel onLoad={(pts, note) => onLoad(pts, note)} />}
              {tab === 'upload' && <UploadZone onLoad={(pts, note) => onLoad(pts, note)} />}
              {tab === 'samples' && (
                <SamplesPanel
                  onLoad={(pts, m) => {
                    onLoad(pts, undefined, m)
                    setTab('manual')
                  }}
                />
              )}
            </motion.div>
          </AnimatePresence>
        </div>

        <div className="mt-6 border-t border-slate-100 pt-5">
          <label className="mb-2 block text-xs font-semibold uppercase tracking-wide text-slate-400">
            Fitting model
          </label>
          <SegmentedControl
            id="model"
            options={[
              { value: 'linear', label: 'Linear' },
              { value: 'polynomial', label: 'Polynomial' },
              { value: 'exponential', label: 'Exponential' },
            ]}
            value={(isExponentialFamily(model) ? 'exponential' : model) as 'linear' | 'polynomial' | 'exponential'}
            onChange={(m) => onModelChange(m as ModelId)}
          />
          <AnimatePresence initial={false}>
            {isExponentialFamily(model) && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: 'auto' }}
                exit={{ opacity: 0, height: 0 }}
                transition={{ duration: 0.2 }}
                className="overflow-hidden"
              >
                <div className="mt-3">
                  <SegmentedControl
                    id="exp-form"
                    options={[
                      { value: 'exponential', label: 'y = aeᵇˣ' },
                      { value: 'exponential_abx', label: 'y = abˣ' },
                      { value: 'power', label: 'y = axᵇ' },
                    ]}
                    value={model}
                    onChange={(m) => onModelChange(m as ModelId)}
                  />
                </div>
              </motion.div>
            )}
          </AnimatePresence>
          <div className="mt-3 flex items-center justify-center rounded-xl border border-slate-100 bg-slate-50/70 py-2.5">
            <Equation latex={MODEL_META[model].formula} className="text-[15px] text-slate-700" />
          </div>
        </div>
      </div>
    </Card>

    {/* Sticky Fit Curve button — always visible at bottom of viewport on desktop */}
    <div className="sticky bottom-4 z-20 mt-4 lg:bottom-6">
      <Button
        size="lg"
        className="w-full shadow-lg shadow-indigo-500/30"
        onClick={onFit}
        disabled={status === 'fitting' || points.length < 2}
      >
        {status === 'fitting' ? (
          <>
            <Loader2 className="h-4 w-4 animate-spin" />
            Solving least squares…
          </>
        ) : (
          <>
            <Sparkles className="h-4 w-4" />
            Fit Curve
          </>
        )}
      </Button>
    </div>
    </>
  )
}
