import { useRef, useState } from 'react'
import { motion } from 'framer-motion'
import { AlertCircle, CheckCircle2, FileUp, Loader2, UploadCloud } from 'lucide-react'
import { cn } from '../../lib/utils'
import { ApiError, parseFile } from '../../lib/api'
import type { Point } from '../../lib/types'
import type { CleaningNote } from './useWorkspace'

type UploadState =
  | { kind: 'idle' }
  | { kind: 'busy'; name: string }
  | { kind: 'done'; name: string; n: number }
  | { kind: 'error'; name: string; message: string }

export function UploadZone({
  onLoad,
}: {
  onLoad: (pts: Point[], note: CleaningNote) => void
}) {
  const [dragging, setDragging] = useState(false)
  const [state, setState] = useState<UploadState>({ kind: 'idle' })
  const inputRef = useRef<HTMLInputElement>(null)

  const readFile = async (file: File) => {
    setState({ kind: 'busy', name: file.name })
    try {
      const parsed = await parseFile(file)
      const pts: Point[] = parsed.x.map((x, i) => ({ x, y: parsed.y[i] }))
      onLoad(pts, {
        removedDuplicates: parsed.cleaning_report.duplicates_removed,
        droppedEmpty: parsed.cleaning_report.empty_dropped + parsed.cleaning_report.non_numeric_dropped,
      })
      setState({ kind: 'done', name: file.name, n: parsed.n })
    } catch (err) {
      setState({
        kind: 'error',
        name: file.name,
        message: err instanceof ApiError ? err.problem.detail : 'Upload failed.',
      })
    }
  }

  return (
    <div>
      <button
        type="button"
        onClick={() => inputRef.current?.click()}
        onDragOver={(e) => {
          e.preventDefault()
          setDragging(true)
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault()
          setDragging(false)
          const file = e.dataTransfer.files[0]
          if (file) void readFile(file)
        }}
        aria-label="Upload a data file"
        className={cn(
          'group flex w-full flex-col items-center justify-center gap-3 rounded-2xl border-2 border-dashed px-6 py-10 transition-all duration-200',
          dragging
            ? 'border-indigo-400 bg-indigo-50/70 scale-[1.01]'
            : 'border-slate-200 bg-slate-50/50 hover:border-indigo-300 hover:bg-indigo-50/40',
        )}
      >
        <motion.div
          animate={dragging ? { y: [-2, -8, -2] } : {}}
          transition={{ repeat: Infinity, duration: 0.9 }}
          className={cn(
            'flex h-12 w-12 items-center justify-center rounded-2xl transition-colors',
            dragging ? 'bg-indigo-100 text-indigo-600' : 'bg-white text-slate-400 shadow-sm ring-1 ring-slate-200 group-hover:text-indigo-500',
          )}
        >
          <UploadCloud className="h-6 w-6" />
        </motion.div>
        <div className="text-center">
          <p className="text-sm font-semibold text-slate-700">
            {dragging ? 'Drop it here' : 'Drag & drop or click to browse'}
          </p>
          <p className="mt-1 text-xs text-slate-400">CSV · TXT · JSON — up to 10 MB</p>
        </div>
      </button>
      <input
        ref={inputRef}
        type="file"
        accept=".csv,.txt,.json"
        className="hidden"
        onChange={(e) => {
          const file = e.target.files?.[0]
          if (file) void readFile(file)
          e.target.value = ''
        }}
      />
      {state.kind !== 'idle' && (
        <motion.div
          initial={{ opacity: 0, y: 6 }}
          animate={{ opacity: 1, y: 0 }}
          className={cn(
            'mt-3 flex items-center gap-2.5 rounded-xl border px-3.5 py-2.5',
            state.kind === 'done' && 'border-emerald-200/70 bg-emerald-50/70',
            state.kind === 'busy' && 'border-indigo-200/70 bg-indigo-50/70',
            state.kind === 'error' && 'border-red-200/70 bg-red-50/70',
          )}
        >
          {state.kind === 'busy' && <Loader2 className="h-4 w-4 shrink-0 animate-spin text-indigo-500" />}
          {state.kind === 'done' && <CheckCircle2 className="h-4 w-4 shrink-0 text-emerald-500" />}
          {state.kind === 'error' && <AlertCircle className="h-4 w-4 shrink-0 text-red-500" />}
          <span
            className={cn(
              'truncate text-[13px] font-medium',
              state.kind === 'done' && 'text-emerald-800',
              state.kind === 'busy' && 'text-indigo-800',
              state.kind === 'error' && 'text-red-800',
            )}
          >
            {state.kind === 'done' && `${state.name} — ${state.n} points loaded`}
            {state.kind === 'busy' && `${state.name} — parsing…`}
            {state.kind === 'error' && `${state.name} — ${state.message}`}
          </span>
          <FileUp className="ml-auto h-3.5 w-3.5 shrink-0 text-slate-300" />
        </motion.div>
      )}
    </div>
  )
}
