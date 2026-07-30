import { useState } from 'react'
import { ChartSpline, Moon, Sun } from 'lucide-react'
import { Card, CardHeader } from '../../components/ui/Card'
import { SegmentedControl } from '../../components/ui/SegmentedControl'
import { MainChart } from '../../components/charts/MainChart'
import { ResidualChart } from '../../components/charts/ResidualChart'
import type { ChartTheme } from '../../components/charts/theme'
import type { ApiFitResult } from '../../lib/types'
import { cn } from '../../lib/utils'

export function GraphCard({
  result,
  prediction,
}: {
  result: ApiFitResult
  prediction?: { x: number; y: number } | null
}) {
  const [view, setView] = useState<'fit' | 'residuals'>('fit')
  const [theme, setTheme] = useState<ChartTheme>('light')

  return (
    <Card className="overflow-hidden">
      <CardHeader
        title="Regression Graph"
        subtitle="Zoom, pan and hover — export from the toolbar"
        icon={<ChartSpline className="h-4 w-4" />}
        actions={
          <>
            <SegmentedControl
              id="graph-view"
              className="w-full min-[420px]:w-52"
              options={[
                { value: 'fit', label: 'Curve fit' },
                { value: 'residuals', label: 'Residuals' },
              ]}
              value={view}
              onChange={setView}
            />
            <button
              onClick={() => setTheme(theme === 'light' ? 'dark' : 'light')}
              aria-label={`Switch chart to ${theme === 'light' ? 'dark' : 'light'} theme`}
              className="flex h-9 w-9 items-center justify-center rounded-lg border border-slate-200 bg-white text-slate-500 transition-colors hover:border-indigo-200 hover:text-indigo-600"
            >
              {theme === 'light' ? <Moon className="h-4 w-4" /> : <Sun className="h-4 w-4" />}
            </button>
          </>
        }
      />
      <div
        className={cn(
          'p-2 transition-colors duration-300 sm:p-4',
          theme === 'dark' ? 'bg-slate-900' : 'bg-white',
        )}
      >
        {view === 'fit' ? (
          <MainChart result={result} theme={theme} prediction={prediction} />
        ) : (
          <ResidualChart result={result} theme={theme} />
        )}
      </div>
    </Card>
  )
}
