import type { ReactNode } from 'react'
import { hardHref } from '../../lib/hardNav'
import { cn } from '../../lib/utils'

type Variant = 'primary' | 'secondary' | 'ghost' | 'danger'
type Size = 'sm' | 'md' | 'lg'

const variants: Record<Variant, string> = {
  primary:
    'bg-gradient-to-br from-indigo-600 to-violet-600 text-white shadow-[0_4px_14px_rgb(79_70_229/0.35)] hover:from-indigo-500 hover:to-violet-500 hover:shadow-[0_6px_20px_rgb(79_70_229/0.45)] hover:-translate-y-px active:translate-y-0 active:scale-[0.98]',
  secondary:
    'border border-slate-200 bg-white text-slate-700 shadow-sm hover:border-indigo-200 hover:bg-indigo-50/50 hover:text-indigo-700 hover:-translate-y-px active:translate-y-0 active:scale-[0.98]',
  ghost:
    'text-slate-600 hover:bg-slate-100 hover:text-slate-900 active:scale-[0.98]',
  danger:
    'border border-red-200 bg-white text-red-600 shadow-sm hover:bg-red-50 active:scale-[0.98]',
}

const sizes: Record<Size, string> = {
  sm: 'h-8 gap-1.5 rounded-lg px-3 text-[13px]',
  md: 'h-10 gap-2 rounded-xl px-4 text-sm',
  lg: 'h-12 gap-2 rounded-xl px-6 text-[15px]',
}

export function LinkButton({
  to,
  variant = 'primary',
  size = 'md',
  className,
  children,
}: {
  to: string
  variant?: Variant
  size?: Size
  className?: string
  children: ReactNode
}) {
  return (
    <a
      href={hardHref(to)}
      data-hardnav
      className={cn(
        'inline-flex select-none items-center justify-center font-semibold transition-all duration-150',
        variants[variant],
        sizes[size],
        className,
      )}
    >
      {children}
    </a>
  )
}
