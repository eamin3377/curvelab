import { useEffect, useMemo, useRef } from 'react'
import { Plot } from './Plot'
import { baseLayout, SERIES, type ChartTheme } from './theme'
import type { ApiFitResult } from '../../lib/types'
import { registerChart } from '../../lib/chartCapture'

export function ResidualChart({
  result,
  theme,
}: {
  result: ApiFitResult
  theme: ChartTheme
}) {
  const containerRef = useRef<HTMLDivElement>(null)
  const residuals = result.graph.residuals

  useEffect(() => {
    const el = containerRef.current?.firstElementChild as HTMLElement | null
    registerChart(el)
    return () => registerChart(null)
  }, [result, theme])

  const data = useMemo(
    () => [
      {
        x: result.graph.scatter_x,
        y: residuals,
        type: 'scatter',
        mode: 'markers',
        name: 'Residuals',
        marker: {
          color: SERIES.residual,
          size: 9,
          line: { color: theme === 'dark' ? '#1e293b' : '#f5f3ff', width: 2 },
        },
        hovertemplate: 'x = %{x:.3f}<br>residual = %{y:.4f}<extra></extra>',
      },
    ],
    [result, residuals, theme],
  )

  const maxAbs = Math.max(...residuals.map((r) => Math.abs(r)), 1e-6) * 1.4

  const layout = useMemo(
    () => ({
      ...baseLayout(theme),
      xaxis: { ...baseLayout(theme).xaxis, title: { text: 'x' } },
      yaxis: {
        ...baseLayout(theme).yaxis,
        title: { text: 'residual (y − ŷ)' },
        range: [-maxAbs, maxAbs],
        zerolinecolor: theme === 'dark' ? 'rgba(148,163,184,0.5)' : '#cbd5e1',
        zerolinewidth: 2,
      },
      showlegend: false,
    }),
    [theme, maxAbs],
  )

  return (
    <div ref={containerRef}>
      <Plot
        data={data}
        layout={layout}
        className="h-[380px] w-full sm:h-[440px]"
        ariaLabel="Residual plot showing the error of each data point relative to the fitted curve"
      />
    </div>
  )
}
