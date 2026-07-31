import { GraduationCap, Mail } from 'lucide-react'
import { Logo } from './Logo'
import { GithubIcon } from '../ui/GithubIcon'
import { hardHref } from '../../lib/hardNav'

const columns = [
  {
    title: 'Product',
    links: [
      { label: 'Workspace', to: '/app' },
      { label: 'Methods', to: '/methods' },
      { label: 'About', to: '/about' },
    ],
  },
  {
    title: 'Methods',
    links: [
      { label: 'Linear regression', to: '/methods' },
      { label: 'Polynomial fitting', to: '/methods' },
      { label: 'Exponential fitting', to: '/methods' },
    ],
  },
  {
    title: 'Resources',
    links: [
      { label: 'Documentation', to: '/methods' },
      { label: 'API reference', to: '/methods' },
      { label: 'Changelog', to: '/methods' },
    ],
  },
]

export function Footer() {
  return (
    <footer className="border-t border-slate-200/80 bg-slate-50/60">
      <div className="mx-auto max-w-7xl 2xl:max-w-[1600px] px-4 py-14 sm:px-6 lg:px-8">
        <div className="grid gap-10 md:grid-cols-[1.4fr_repeat(3,1fr)]">
          <div>
            <Logo />
            <p className="mt-4 max-w-xs text-sm leading-relaxed text-slate-500">
              Least squares curve fitting with interactive graphs, step-by-step solutions and
              university-ready reports.
            </p>
            <div className="mt-5 flex items-center gap-2">
              <a
                href="https://github.com"
                target="_blank"
                rel="noreferrer"
                aria-label="GitHub"
                className="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-500 transition-colors hover:border-indigo-200 hover:text-indigo-600"
              >
                <GithubIcon className="h-4 w-4" />
              </a>
              <a
                href="mailto:hello@curvelab.app"
                aria-label="Email"
                className="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-500 transition-colors hover:border-indigo-200 hover:text-indigo-600"
              >
                <Mail className="h-4 w-4" />
              </a>
            </div>
          </div>

          {columns.map((col) => (
            <div key={col.title}>
              <h4 className="text-sm font-semibold text-slate-900">{col.title}</h4>
              <ul className="mt-4 space-y-2.5">
                {col.links.map((l) => (
                  <li key={l.label}>
                    <a
                      href={hardHref(l.to)}
                      data-hardnav
                      className="text-sm text-slate-500 transition-colors hover:text-indigo-600"
                    >
                      {l.label}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          ))}
        </div>

        <div className="mt-12 flex flex-col items-center justify-between gap-4 border-t border-slate-200/80 pt-6 sm:flex-row">
          <p className="flex items-center gap-2 text-[13px] text-slate-400">
            <GraduationCap className="h-4 w-4" />
            Numerical Methods · Daffodil International University, Dept. of CSE
          </p>
          <p className="text-[13px] text-slate-400">
            © {new Date().getFullYear()} CurveLab. MIT License.
          </p>
        </div>
      </div>
    </footer>
  )
}
