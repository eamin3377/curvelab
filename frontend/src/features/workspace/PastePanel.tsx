import { useState } from 'react'
import { ClipboardPaste, Check, Loader2 } from 'lucide-react'
import { Button } from '../../components/ui/Button'
import { Badge } from '../../components/ui/Badge'
import { ApiError, parseText } from '../../lib/api'
import type { Point } from '../../lib/types'
import type { CleaningNote } from './useWorkspace'

export function PastePanel({
  onLoad,
}: {
  onLoad: (pts: Point[], note: CleaningNote) => void
}) {
  const [text, setText] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [ok, setOk] = useState<number | null>(null)

  const apply = async () => {
    setBusy(true)
    setError(null)
    try {
      const parsed = await parseText(text)
      const pts = parsed.x.map((x, i) => ({ x, y: parsed.y[i] }))
      onLoad(pts, {
        removedDuplicates: parsed.cleaning_report.duplicates_removed,
        droppedEmpty: parsed.cleaning_report.empty_dropped + parsed.cleaning_report.non_numeric_dropped,
      })
      setOk(parsed.n)
    } catch (err) {
      setOk(null)
      setError(err instanceof ApiError ? err.problem.detail : 'Could not parse the pasted data.')
    } finally {
      setBusy(false)
    }
  }

  return (
    <div>
      <label htmlFor="paste-area" className="mb-2 block text-xs font-semibold uppercase tracking-wide text-slate-400">
        Paste from Excel, CSV or plain text
      </label>
      <textarea
        id="paste-area"
        value={text}
        onChange={(e) => {
          setText(e.target.value)
          setOk(null)
          setError(null)
        }}
        placeholder={'1\t2.9\n2\t5.1\n3\t6.8\n…'}
        rows={8}
        className="w-full resize-none rounded-xl border border-slate-200 bg-slate-50/60 p-3.5 font-mono text-[13px] leading-relaxed text-slate-800 placeholder:text-slate-300 transition-colors hover:border-slate-300 focus:border-indigo-400 focus:bg-white"
      />
      <div className="mt-3 flex items-center justify-between gap-3">
        {error ? (
          <Badge tone="red">{error}</Badge>
        ) : ok !== null ? (
          <Badge tone="emerald">
            <Check className="h-3 w-3" />
            {ok} points loaded
          </Badge>
        ) : (
          <span className="text-xs text-slate-400">Tab, comma and space delimiters auto-detected by the server</span>
        )}
        <Button size="sm" disabled={!text.trim() || busy} onClick={apply}>
          {busy ? <Loader2 className="h-3.5 w-3.5 animate-spin" /> : <ClipboardPaste className="h-3.5 w-3.5" />}
          Use data
        </Button>
      </div>
    </div>
  )
}
