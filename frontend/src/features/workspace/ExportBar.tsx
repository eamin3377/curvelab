import { useState } from 'react'
import { AnimatePresence, motion } from 'framer-motion'
import {
  Braces,
  Check,
  Download,
  FileSpreadsheet,
  FileText,
  FileType,
  Loader2,
  Printer,
  X,
} from 'lucide-react'
import { Tooltip } from '../../components/ui/Tooltip'
import { Button } from '../../components/ui/Button'
import { cn } from '../../lib/utils'
import { downloadBlob, exportReport, ApiError } from '../../lib/api'
import { captureChartPng } from '../../lib/chartCapture'
import type { ExportFormat, FitRequestPayload, ReportMetaPayload } from '../../lib/types'

const FORMATS: Array<{ id: ExportFormat | 'print'; label: string; icon: typeof FileText; withMeta: boolean; withChart: boolean }> = [
  { id: 'pdf', label: 'PDF report', icon: FileText, withMeta: true, withChart: true },
  { id: 'docx', label: 'Word report', icon: FileType, withMeta: true, withChart: true },
  { id: 'xlsx', label: 'Excel workbook', icon: FileSpreadsheet, withMeta: true, withChart: true },
  { id: 'csv', label: 'CSV data', icon: Download, withMeta: false, withChart: false },
  { id: 'json', label: 'JSON result', icon: Braces, withMeta: false, withChart: false },
  { id: 'txt', label: 'Plain-text report', icon: FileText, withMeta: false, withChart: false },
  { id: 'print', label: 'Print report', icon: Printer, withMeta: false, withChart: false },
]

const DEFAULT_META: ReportMetaPayload = {
  title: 'Least Squares Curve Fitting Report',
  author: '',
  student_id: '',
  course: 'Numerical Methods',
  institution: '',
  date: new Date().toISOString().slice(0, 10),
}

export function ExportBar({ lastRequest }: { lastRequest: FitRequestPayload | null }) {
  const [busy, setBusy] = useState<string | null>(null)
  const [done, setDone] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [pending, setPending] = useState<(typeof FORMATS)[number] | null>(null)
  const [meta, setMeta] = useState<ReportMetaPayload>(DEFAULT_META)

  const runExport = async (fmt: (typeof FORMATS)[number], reportMeta: ReportMetaPayload) => {
    if (!lastRequest) return
    setBusy(fmt.id)
    setError(null)
    try {
      const chart = fmt.withChart ? await captureChartPng() : null
      const { blob, filename } = await exportReport(fmt.id as ExportFormat, {
        fit_request: lastRequest,
        report_meta: reportMeta,
        chart_png_base64: chart,
      })
      downloadBlob(blob, filename)
      setDone(fmt.id)
      window.setTimeout(() => setDone(null), 1800)
    } catch (err) {
      setError(err instanceof ApiError ? err.problem.detail : 'Export failed.')
    } finally {
      setBusy(null)
    }
  }

  const trigger = (fmt: (typeof FORMATS)[number]) => {
    if (fmt.id === 'print') {
      window.print()
      return
    }
    if (fmt.withMeta) {
      setPending(fmt)
      return
    }
    void runExport(fmt, DEFAULT_META)
  }

  return (
    <>
      <motion.div
        initial={{ opacity: 0, y: 24 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.4, type: 'spring', stiffness: 260, damping: 26 }}
        className="fixed bottom-5 left-1/2 z-40 -translate-x-1/2 print:hidden"
      >
        <div className="glass flex items-center gap-1 rounded-2xl p-1.5 shadow-[0_12px_40px_rgb(15_23_42/0.14)]">
          <span className="hidden select-none pl-2.5 pr-1 text-xs font-semibold uppercase tracking-wider text-slate-400 sm:block">
            Export
          </span>
          {FORMATS.map((f) => (
            <Tooltip key={f.id} label={f.label}>
              <button
                onClick={() => trigger(f)}
                disabled={busy !== null || !lastRequest}
                aria-label={f.label}
                className={cn(
                  'flex h-10 w-10 items-center justify-center rounded-xl text-slate-500 transition-all duration-150 hover:-translate-y-0.5 hover:bg-white hover:text-indigo-600 hover:shadow-md disabled:pointer-events-none disabled:opacity-40',
                  done === f.id && 'bg-emerald-50 text-emerald-600',
                )}
              >
                {busy === f.id ? (
                  <Loader2 className="h-[18px] w-[18px] animate-spin text-indigo-500" />
                ) : done === f.id ? (
                  <Check className="h-[18px] w-[18px]" />
                ) : (
                  <f.icon className="h-[18px] w-[18px]" />
                )}
              </button>
            </Tooltip>
          ))}
        </div>
        {error && (
          <motion.p
            initial={{ opacity: 0, y: 6 }}
            animate={{ opacity: 1, y: 0 }}
            className="mx-auto mt-2 w-max max-w-xs rounded-xl border border-red-200 bg-red-50 px-3.5 py-2 text-center text-xs font-medium text-red-700 shadow-lg"
          >
            {error}
          </motion.p>
        )}
      </motion.div>

      <AnimatePresence>
        {pending && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-50 flex items-center justify-center bg-slate-900/40 p-4 backdrop-blur-sm print:hidden"
            onClick={() => setPending(null)}
          >
            <motion.div
              initial={{ opacity: 0, scale: 0.94, y: 16 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.96, y: 10 }}
              transition={{ type: 'spring', stiffness: 320, damping: 28 }}
              onClick={(e) => e.stopPropagation()}
              role="dialog"
              aria-modal="true"
              aria-label="Report details"
              className="w-full max-w-md rounded-2xl bg-white p-6 shadow-2xl"
            >
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-lg font-bold text-slate-900">Report details</h3>
                  <p className="mt-0.5 text-sm text-slate-500">
                    Shown on the {pending.label.toLowerCase()} cover page.
                  </p>
                </div>
                <button
                  onClick={() => setPending(null)}
                  aria-label="Close dialog"
                  className="rounded-lg p-1.5 text-slate-400 transition-colors hover:bg-slate-100 hover:text-slate-600"
                >
                  <X className="h-4.5 w-4.5" />
                </button>
              </div>

              <div className="mt-5 space-y-3.5">
                {(
                  [
                    ['title', 'Report title'],
                    ['author', 'Author'],
                    ['student_id', 'Student ID'],
                    ['institution', 'Institution'],
                    ['course', 'Course'],
                    ['date', 'Date'],
                  ] as const
                ).map(([key, label]) => (
                  <div key={key}>
                    <label htmlFor={`meta-${key}`} className="mb-1 block text-xs font-semibold uppercase tracking-wide text-slate-400">
                      {label}
                    </label>
                    <input
                      id={`meta-${key}`}
                      type={key === 'date' ? 'date' : 'text'}
                      value={meta[key]}
                      onChange={(e) => setMeta((m) => ({ ...m, [key]: e.target.value }))}
                      className="h-10 w-full rounded-xl border border-slate-200 bg-slate-50/60 px-3.5 text-[14px] text-slate-800 transition-colors hover:border-slate-300 focus:border-indigo-400 focus:bg-white"
                    />
                  </div>
                ))}
              </div>

              <div className="mt-6 flex justify-end gap-2.5">
                <Button variant="secondary" onClick={() => setPending(null)}>
                  Cancel
                </Button>
                <Button
                  onClick={() => {
                    const fmt = pending
                    setPending(null)
                    void runExport(fmt, meta)
                  }}
                >
                  <Download className="h-4 w-4" />
                  Export {pending.id.toUpperCase()}
                </Button>
              </div>
            </motion.div>
          </motion.div>
        )}
      </AnimatePresence>
    </>
  )
}
