import { Plus, Trash2 } from 'lucide-react'
import type { Point } from '../../lib/types'
import { Button } from '../../components/ui/Button'

export function ManualGrid({
  points,
  onChange,
}: {
  points: Point[]
  onChange: (pts: Point[]) => void
}) {
  const update = (i: number, key: 'x' | 'y', value: string) => {
    const next = points.map((p, idx) => (idx === i ? { ...p, [key]: Number(value) } : p))
    onChange(next)
  }

  return (
    <div>
      <div className="mb-2 grid grid-cols-[1fr_1fr_36px] gap-2 px-1 text-xs font-semibold uppercase tracking-wide text-slate-400">
        <span>X value</span>
        <span>Y value</span>
        <span className="sr-only">Remove</span>
      </div>
      <div className="max-h-72 space-y-1.5 overflow-y-auto pr-1 scrollbar-thin">
        {points.map((p, i) => (
          <div key={i} className="grid grid-cols-[1fr_1fr_36px] items-center gap-2">
            <input
              type="number"
              value={Number.isFinite(p.x) ? p.x : ''}
              onChange={(e) => update(i, 'x', e.target.value)}
              aria-label={`X value for row ${i + 1}`}
              className="h-9 w-full min-w-0 rounded-lg border border-slate-200 bg-slate-50/60 px-3 font-mono text-[13px] text-slate-800 transition-colors hover:border-slate-300 focus:border-indigo-400 focus:bg-white"
            />
            <input
              type="number"
              value={Number.isFinite(p.y) ? p.y : ''}
              onChange={(e) => update(i, 'y', e.target.value)}
              aria-label={`Y value for row ${i + 1}`}
              className="h-9 w-full min-w-0 rounded-lg border border-slate-200 bg-slate-50/60 px-3 font-mono text-[13px] text-slate-800 transition-colors hover:border-slate-300 focus:border-indigo-400 focus:bg-white"
            />
            <button
              onClick={() => onChange(points.filter((_, idx) => idx !== i))}
              aria-label={`Remove row ${i + 1}`}
              className="flex h-9 w-9 items-center justify-center rounded-lg text-slate-300 transition-colors hover:bg-red-50 hover:text-red-500"
            >
              <Trash2 className="h-4 w-4" />
            </button>
          </div>
        ))}
      </div>
      <Button
        variant="secondary"
        size="sm"
        className="mt-3 w-full"
        onClick={() => onChange([...points, { x: 0, y: 0 }])}
      >
        <Plus className="h-3.5 w-3.5" />
        Add row
      </Button>
    </div>
  )
}
