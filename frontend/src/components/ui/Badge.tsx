import type { HTMLAttributes } from 'react'
import { cn } from '../../lib/utils'

type Tone = 'indigo' | 'sky' | 'violet' | 'emerald' | 'amber' | 'slate' | 'red'

const tones: Record<Tone, string> = {
  indigo: 'bg-indigo-50 text-indigo-700 ring-indigo-200/70',
  sky: 'bg-sky-50 text-sky-700 ring-sky-200/70',
  violet: 'bg-violet-50 text-violet-700 ring-violet-200/70',
  emerald: 'bg-emerald-50 text-emerald-700 ring-emerald-200/70',
  amber: 'bg-amber-50 text-amber-700 ring-amber-200/70',
  slate: 'bg-slate-100 text-slate-600 ring-slate-200/70',
  red: 'bg-red-50 text-red-700 ring-red-200/70',
}

export function Badge({
  tone = 'indigo',
  className,
  ...props
}: HTMLAttributes<HTMLSpanElement> & { tone?: Tone }) {
  return (
    <span
      className={cn(
        'inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 text-xs font-semibold ring-1',
        tones[tone],
        className,
      )}
      {...props}
    />
  )
}
