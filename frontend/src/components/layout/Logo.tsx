import { hardHref } from '../../lib/hardNav'

export function Logo() {
  return (
    <a href={hardHref('/')} data-hardnav className="flex items-center gap-2.5" aria-label="CurveLab home">
      <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-indigo-600 to-violet-600 shadow-[0_4px_12px_rgb(79_70_229/0.35)]">
        <svg viewBox="0 0 32 32" className="h-5 w-5" aria-hidden="true">
          <path
            d="M6 23 C 11 23, 12 9, 17 9 S 24 20, 26 8"
            fill="none"
            stroke="#fff"
            strokeWidth="2.6"
            strokeLinecap="round"
          />
          <circle cx="9" cy="19" r="1.7" fill="#C7D2FE" />
          <circle cx="16" cy="12" r="1.7" fill="#C7D2FE" />
          <circle cx="23" cy="16" r="1.7" fill="#C7D2FE" />
        </svg>
      </span>
      <span className="text-[17px] font-bold tracking-tight text-slate-900">
        Curve<span className="text-gradient">Lab</span>
      </span>
    </a>
  )
}
