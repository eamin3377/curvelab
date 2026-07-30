import type { ReactNode } from 'react'

export function Tooltip({ label, children }: { label: string; children: ReactNode }) {
  return (
    <span className="group/tt relative inline-flex">
      {children}
      <span
        role="tooltip"
        className="pointer-events-none absolute -top-2 left-1/2 z-50 w-max max-w-56 -translate-x-1/2 -translate-y-full scale-95 rounded-lg bg-slate-900 px-2.5 py-1.5 text-xs font-medium text-white opacity-0 shadow-lg transition-all duration-150 group-hover/tt:scale-100 group-hover/tt:opacity-100 group-focus-within/tt:scale-100 group-focus-within/tt:opacity-100"
      >
        {label}
        <span className="absolute left-1/2 top-full -ml-1 border-4 border-transparent border-t-slate-900" />
      </span>
    </span>
  )
}
