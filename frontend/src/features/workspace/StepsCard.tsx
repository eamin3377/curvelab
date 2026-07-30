import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import { ChevronDown, ListOrdered } from 'lucide-react'
import { Card, CardHeader } from '../../components/ui/Card'
import { Button } from '../../components/ui/Button'
import { Equation } from '../../components/ui/Equation'
import type { ApiFitResult } from '../../lib/types'
import { cn } from '../../lib/utils'

export function StepsCard({ result }: { result: ApiFitResult }) {
  const [open, setOpen] = useState<Set<number>>(new Set([1, 3]))
  const allOpen = open.size === result.steps.length

  const toggle = (i: number) => {
    setOpen((prev) => {
      const next = new Set(prev)
      if (next.has(i)) next.delete(i)
      else next.add(i)
      return next
    })
  }

  return (
    <Card>
      <CardHeader
        title="Step-by-Step Solution"
        subtitle="The full least squares derivation"
        icon={<ListOrdered className="h-4 w-4" />}
        actions={
          <Button
            variant="secondary"
            size="sm"
            onClick={() =>
              setOpen(allOpen ? new Set() : new Set(result.steps.map((s) => s.index)))
            }
          >
            {allOpen ? 'Collapse all' : 'Expand all'}
          </Button>
        }
      />
      <div className="px-6 py-5">
        <ol className="relative space-y-2 before:absolute before:bottom-6 before:left-[15px] before:top-6 before:w-px before:bg-gradient-to-b before:from-indigo-200 before:via-violet-200 before:to-transparent">
          {result.steps.map((step) => {
            const isOpen = open.has(step.index)
            return (
              <li key={step.index} className="relative pl-11">
                <span
                  className={cn(
                    'absolute left-0 top-2 flex h-8 w-8 items-center justify-center rounded-full text-[13px] font-bold ring-4 ring-white transition-colors',
                    isOpen
                      ? 'bg-gradient-to-br from-indigo-500 to-violet-500 text-white shadow-[0_4px_10px_rgb(79_70_229/0.35)]'
                      : 'bg-slate-100 text-slate-500',
                  )}
                >
                  {step.index}
                </span>
                <button
                  onClick={() => toggle(step.index)}
                  aria-expanded={isOpen}
                  className="flex w-full items-center justify-between gap-3 rounded-xl px-3 py-2.5 text-left transition-colors hover:bg-slate-50"
                >
                  <span className="text-[14.5px] font-semibold text-slate-800">{step.title}</span>
                  <ChevronDown
                    className={cn(
                      'h-4 w-4 shrink-0 text-slate-400 transition-transform duration-200',
                      isOpen && 'rotate-180',
                    )}
                  />
                </button>
                <AnimatePresence initial={false}>
                  {isOpen && (
                    <motion.div
                      initial={{ height: 0, opacity: 0 }}
                      animate={{ height: 'auto', opacity: 1 }}
                      exit={{ height: 0, opacity: 0 }}
                      transition={{ duration: 0.22, ease: 'easeOut' }}
                      className="overflow-hidden"
                    >
                      <div className="px-3 pb-4 pt-1">
                        <p className="text-[13.5px] leading-relaxed text-slate-500">
                          {step.description}
                        </p>
                        <div className="mt-3 overflow-x-auto rounded-xl border border-slate-100 bg-slate-50/70 px-4 py-3.5 scrollbar-thin">
                          <Equation latex={step.latex} block className="text-[15px] text-slate-700" />
                        </div>
                        {step.index === 3 && (
                          <div className="mt-3 overflow-x-auto rounded-xl border border-indigo-100/70 bg-indigo-50/40 px-4 py-3.5 scrollbar-thin">
                            <p className="mb-2 text-xs font-semibold uppercase tracking-wide text-indigo-400">
                              With your data substituted
                            </p>
                            <Equation
                              latex={result.normal_equations.latex_substituted}
                              block
                              className="text-[14px] text-slate-700"
                            />
                          </div>
                        )}
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              </li>
            )
          })}
        </ol>
      </div>
    </Card>
  )
}
