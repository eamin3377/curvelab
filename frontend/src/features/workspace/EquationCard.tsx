import { useState } from 'react'
import { Check, Copy, FunctionSquare } from 'lucide-react'
import { Card, CardHeader } from '../../components/ui/Card'
import { Badge } from '../../components/ui/Badge'
import { Button } from '../../components/ui/Button'
import { Equation } from '../../components/ui/Equation'
import { MODEL_META, type ApiFitResult } from '../../lib/types'
import { formatNumber } from '../../lib/utils'

export function EquationCard({ result }: { result: ApiFitResult }) {
  const [copied, setCopied] = useState<'plain' | 'latex' | null>(null)

  const copy = (kind: 'plain' | 'latex') => {
    void navigator.clipboard.writeText(kind === 'plain' ? result.equation.plain : result.equation.latex)
    setCopied(kind)
    window.setTimeout(() => setCopied(null), 1600)
  }

  return (
    <Card>
      <CardHeader
        title="Fitted Equation"
        subtitle="Least squares solution"
        icon={<FunctionSquare className="h-4 w-4" />}
        actions={
          <>
            <Button variant="secondary" size="sm" onClick={() => copy('plain')}>
              {copied === 'plain' ? <Check className="h-3.5 w-3.5 text-emerald-500" /> : <Copy className="h-3.5 w-3.5" />}
              Copy
            </Button>
            <Button variant="secondary" size="sm" onClick={() => copy('latex')}>
              {copied === 'latex' ? <Check className="h-3.5 w-3.5 text-emerald-500" /> : <Copy className="h-3.5 w-3.5" />}
              LaTeX
            </Button>
          </>
        }
      />
      <div className="px-6 py-6">
        <div className="flex items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-50/80 via-white to-sky-50/80 px-6 py-8 ring-1 ring-indigo-100/60">
          <Equation latex={result.equation.latex} block className="text-xl text-slate-800 sm:text-2xl" />
        </div>
        <div className="mt-5 flex flex-wrap items-center gap-2.5">
          <Badge tone="indigo">{MODEL_META[result.model].label} model</Badge>
          {result.coefficients.map((c) => (
            <span
              key={c.name}
              className="inline-flex items-center gap-1.5 rounded-lg border border-slate-200 bg-slate-50/70 px-2.5 py-1 font-mono text-[13px] text-slate-700"
            >
              <span className="text-slate-400">{c.name} =</span>
              <span className="font-semibold text-slate-900">{formatNumber(c.value)}</span>
            </span>
          ))}
        </div>
      </div>
    </Card>
  )
}
