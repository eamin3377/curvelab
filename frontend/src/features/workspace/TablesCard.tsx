import { useMemo, useState } from 'react'
import { ArrowDown, ArrowUp, ArrowUpDown, Check, Copy, Search, Sigma, Table2 } from 'lucide-react'
import { Card, CardHeader } from '../../components/ui/Card'
import { Button } from '../../components/ui/Button'
import { Equation } from '../../components/ui/Equation'
import type { ApiFitResult } from '../../lib/types'
import { cn, formatNumber } from '../../lib/utils'

const PAGE_SIZE = 8

// Human-readable headers for the server's calculation-table column keys.
const COLUMN_LABELS: Record<string, string> = {
  x: 'x',
  y: 'y',
  ln_y: 'ln y',
  x2: 'x²',
  x3: 'x³',
  x4: 'x⁴',
  x5: 'x⁵',
  x6: 'x⁶',
  x7: 'x⁷',
  x8: 'x⁸',
  x9: 'x⁹',
  x10: 'x¹⁰',
  x11: 'x¹¹',
  x12: 'x¹²',
  xy: 'x·y',
  x2y: 'x²·y',
  x3y: 'x³·y',
  x4y: 'x⁴·y',
  x5y: 'x⁵·y',
  x6y: 'x⁶·y',
  x_ln_y: 'x·ln y',
  ln_x: 'ln x',
  ln_x2: '(ln x)²',
  ln_x_ln_y: 'ln x·ln y',
  y_hat: 'ŷ',
  residual: 'y − ŷ',
  residual2: '(y − ŷ)²',
}

export function TablesCard({ result }: { result: ApiFitResult }) {
  const [tab, setTab] = useState<'calc' | 'sums'>('calc')
  const [query, setQuery] = useState('')
  const [sort, setSort] = useState<{ col: number; dir: 1 | -1 } | null>(null)
  const [page, setPage] = useState(0)
  const [copied, setCopied] = useState(false)

  const table = result.calculation_table
  const residualCol = table.columns.indexOf('residual')

  const rows = useMemo(() => {
    let data = table.rows.map((row, i) => ({ i, row }))
    if (query.trim()) {
      const q = query.trim()
      data = data.filter(({ row }) => row.some((v) => String(v).includes(q)))
    }
    if (sort) {
      data = [...data].sort((a, b) => (a.row[sort.col] - b.row[sort.col]) * sort.dir)
    }
    return data
  }, [table, query, sort])

  const totalPages = Math.max(1, Math.ceil(rows.length / PAGE_SIZE))
  const pageRows = rows.slice(page * PAGE_SIZE, (page + 1) * PAGE_SIZE)

  const toggleSort = (col: number) => {
    setPage(0)
    setSort((prev) =>
      !prev || prev.col !== col ? { col, dir: 1 } : prev.dir === 1 ? { col, dir: -1 } : null,
    )
  }

  const copyTable = () => {
    const header = table.columns.map((c) => COLUMN_LABELS[c] ?? c).join('\t')
    const body = rows.map(({ row }) => row.map((v) => formatNumber(v)).join('\t')).join('\n')
    void navigator.clipboard.writeText(`${header}\n${body}`)
    setCopied(true)
    window.setTimeout(() => setCopied(false), 1600)
  }

  return (
    <Card className="overflow-hidden">
      <CardHeader
        title="Calculation Table"
        subtitle={`Every value used by the normal equations · ${table.total_rows} rows${table.truncated ? ' (first 1000 shown)' : ''}`}
        icon={<Table2 className="h-4 w-4" />}
        actions={
          <div className="flex flex-wrap items-center gap-2">
            <div className="relative hidden sm:block">
              <Search className="pointer-events-none absolute left-3 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-slate-400" />
              <input
                value={query}
                onChange={(e) => {
                  setQuery(e.target.value)
                  setPage(0)
                }}
                placeholder="Search values…"
                aria-label="Search table"
                className="h-9 w-44 rounded-lg border border-slate-200 bg-slate-50/60 pl-9 pr-3 text-[13px] text-slate-700 placeholder:text-slate-300 transition-colors focus:border-indigo-400 focus:bg-white"
              />
            </div>
            <Button variant="secondary" size="sm" onClick={copyTable}>
              {copied ? <Check className="h-3.5 w-3.5 text-emerald-500" /> : <Copy className="h-3.5 w-3.5" />}
              Copy
            </Button>
          </div>
        }
      />

      <div className="flex items-center gap-1 border-b border-slate-100 px-6 pt-3">
        {(['calc', 'sums'] as const).map((t) => (
          <button
            key={t}
            onClick={() => setTab(t)}
            className={cn(
              'relative rounded-t-lg px-3.5 pb-2.5 pt-1.5 text-[13px] font-semibold transition-colors',
              tab === t ? 'text-indigo-700' : 'text-slate-400 hover:text-slate-600',
            )}
          >
            {t === 'calc' ? 'Data & products' : 'Summations'}
            {tab === t && (
              <span className="absolute inset-x-2 -bottom-px h-0.5 rounded-full bg-gradient-to-r from-indigo-500 to-violet-500" />
            )}
          </button>
        ))}
      </div>

      {tab === 'calc' ? (
        <>
          <div className="overflow-x-auto scrollbar-thin">
            <table className="w-full text-right text-[13px]">
              <thead className="sticky top-0">
                <tr className="border-b border-slate-100 bg-slate-50/80 text-xs uppercase tracking-wide text-slate-400">
                  <th scope="col" className="px-4 py-3 text-left font-semibold">#</th>
                  {table.columns.map((c, ci) => (
                    <th key={c} scope="col" className="px-4 py-3 font-semibold">
                      <button
                        onClick={() => toggleSort(ci)}
                        className="inline-flex items-center gap-1 rounded transition-colors hover:text-indigo-600"
                        aria-label={`Sort by ${COLUMN_LABELS[c] ?? c}`}
                      >
                        {COLUMN_LABELS[c] ?? c}
                        {sort?.col === ci ? (
                          sort.dir === 1 ? <ArrowUp className="h-3 w-3" /> : <ArrowDown className="h-3 w-3" />
                        ) : (
                          <ArrowUpDown className="h-3 w-3 opacity-40" />
                        )}
                      </button>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="font-mono">
                {pageRows.map(({ i, row }) => (
                  <tr
                    key={i}
                    className="border-b border-slate-50 transition-colors odd:bg-white even:bg-slate-50/40 hover:bg-indigo-50/40"
                  >
                    <td className="px-4 py-2.5 text-left font-sans text-slate-400">{i + 1}</td>
                    {row.map((v, ci) => (
                      <td
                        key={ci}
                        className={cn(
                          'px-4 py-2.5 text-slate-700',
                          ci === residualCol && (v >= 0 ? 'text-emerald-600' : 'text-red-500'),
                        )}
                      >
                        {formatNumber(v)}
                      </td>
                    ))}
                  </tr>
                ))}
              </tbody>
              <tfoot>
                <tr className="border-t-2 border-indigo-100 bg-indigo-50/50 font-semibold">
                  <td className="px-4 py-3 text-left font-sans text-indigo-500">Σ</td>
                  {table.sums.map((s, ci) => (
                    <td key={ci} className="px-4 py-3 font-mono text-indigo-700">
                      {formatNumber(s)}
                    </td>
                  ))}
                </tr>
              </tfoot>
            </table>
          </div>
          <div className="flex items-center justify-between border-t border-slate-100 px-6 py-3">
            <p className="text-xs text-slate-400">
              {rows.length} rows · page {page + 1} of {totalPages}
            </p>
            <div className="flex gap-1.5">
              <Button
                variant="secondary"
                size="sm"
                disabled={page === 0}
                onClick={() => setPage((p) => p - 1)}
              >
                Previous
              </Button>
              <Button
                variant="secondary"
                size="sm"
                disabled={page >= totalPages - 1}
                onClick={() => setPage((p) => p + 1)}
              >
                Next
              </Button>
            </div>
          </div>
        </>
      ) : (
        <div className="grid gap-3 p-6 sm:grid-cols-2 lg:grid-cols-3">
          {result.summations.map((s) => (
            <div
              key={s.key}
              className="flex items-center justify-between rounded-xl border border-slate-100 bg-slate-50/60 px-4 py-3.5 transition-colors hover:border-indigo-100 hover:bg-indigo-50/40"
            >
              <span className="flex items-center gap-2 text-slate-500">
                <Sigma className="h-3.5 w-3.5 text-indigo-400" />
                <Equation latex={s.latex} className="text-[14px]" />
              </span>
              <span className="font-mono text-[14px] font-semibold text-slate-900">
                {formatNumber(s.value)}
              </span>
            </div>
          ))}
        </div>
      )}
    </Card>
  )
}
