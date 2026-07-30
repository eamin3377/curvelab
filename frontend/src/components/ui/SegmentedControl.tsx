import { motion } from 'framer-motion'
import { cn } from '../../lib/utils'

interface Option<T extends string> {
  value: T
  label: string
}

export function SegmentedControl<T extends string>({
  options,
  value,
  onChange,
  className,
  id,
}: {
  options: Option<T>[]
  value: T
  onChange: (v: T) => void
  className?: string
  id?: string
}) {
  return (
    <div
      role="tablist"
      aria-label="Options"
      className={cn('flex rounded-xl bg-slate-100 p-1', className)}
    >
      {options.map((opt) => {
        const active = opt.value === value
        return (
          <button
            key={opt.value}
            role="tab"
            aria-selected={active}
            onClick={() => onChange(opt.value)}
            className={cn(
              'relative flex-1 rounded-lg px-3 py-1.5 text-[13px] font-semibold transition-colors duration-150',
              active ? 'text-indigo-700' : 'text-slate-500 hover:text-slate-800',
            )}
          >
            {active && (
              <motion.span
                layoutId={`seg-${id ?? 'default'}`}
                className="absolute inset-0 rounded-lg bg-white shadow-sm ring-1 ring-slate-200/80"
                transition={{ type: 'spring', stiffness: 400, damping: 32 }}
              />
            )}
            <span className="relative">{opt.label}</span>
          </button>
        )
      })}
    </div>
  )
}
