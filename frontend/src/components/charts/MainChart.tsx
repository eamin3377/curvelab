import { useEffect, useMemo, useRef } from 'react'
import { Plot } from './Plot'
import { baseLayout, SERIES, type ChartTheme } from './theme'
import type { ApiFitResult } from '../../lib/types'
import { registerChart } from '../../lib/chartCapture'

export function MainChart({
  result,
  theme,
  prediction,
}: {
  result: ApiFitResult
  theme: ChartTheme
  prediction?: { x: number; y: number } | null
}) {
  const containerRef = useRef<HTMLDivElement>(null)
  const graph = result.graph

  // Expose the rendered plot so exports can capture it as PNG.
  useEffect(() => {
    const el = containerRef.current?.firstElementChild as HTMLElement | null
    registerChart(el)
    return () => registerChart(null)
  }, [result, theme])

  const data = useMemo(() => {
    const traces: Record<string, unknown>[] = []
    const band = graph.confidence_band

    if (band?.upper && band.lower) {
      traces.push(
        {
          x: graph.curve_x,
          y: band.upper,
          type: 'scatter',
          mode: 'lines',
          line: { width: 0 },
          hoverinfo: 'skip',
          showlegend: false,
        },
        {
          x: graph.curve_x,
          y: band.lower,
          type: 'scatter',
          mode: 'lines',
          line: { width: 0 },
          fill: 'tonexty',
          fillcolor: SERIES.band,
          name: band.approximate ? '95% band (approx.)' : '95% confidence',
          hoverinfo: 'skip',
        },
      )
    }

    traces.push({
      x: graph.curve_x,
      y: graph.curve_y,
      type: 'scatter',
      mode: 'lines',
      name: 'Fitted curve',
      line: { color: SERIES.curve, width: 3, shape: 'spline', smoothing: 0.8 },
      hovertemplate: 'x = %{x:.3f}<br>ŷ = %{y:.3f}<extra>Fitted</extra>',
    })

    traces.push({
      x: graph.scatter_x,
      y: graph.scatter_y,
      type: 'scatter',
      mode: 'markers',
      name: 'Data points',
      marker: {
        color: SERIES.points,
        size: 9,
        line: { color: theme === 'dark' ? '#1e293b' : SERIES.pointsOutline, width: 2 },
      },
      hovertemplate: 'x = %{x:.3f}<br>y = %{y:.3f}<extra>Observed</extra>',
    })

    if (prediction) {
      traces.push({
        x: [prediction.x],
        y: [prediction.y],
        type: 'scatter',
        mode: 'markers',
        name: 'Prediction',
        marker: {
          color: '#f59e0b',
          size: 13,
          symbol: 'diamond',
          line: { color: '#fff', width: 2 },
        },
        hovertemplate: 'x = %{x:.3f}<br>ŷ = %{y:.3f}<extra>Prediction</extra>',
      })
    }

    return traces
  }, [graph, prediction, theme])

  const layout = useMemo(
    () => ({
      ...baseLayout(theme),
      xaxis: { ...baseLayout(theme).xaxis, title: { text: 'x' } },
      yaxis: { ...baseLayout(theme).yaxis, title: { text: 'y' } },
      annotations: [
        {
          text: `${result.equation.plain}   ·   R² = ${result.metrics.r2.toFixed(4)}`,
          xref: 'paper',
          yref: 'paper',
          x: 0.02,
          y: 0.03,
          showarrow: false,
          font: {
            family: 'JetBrains Mono, monospace',
            size: 11.5,
            color: theme === 'dark' ? '#94a3b8' : '#64748b',
          },
          bgcolor: theme === 'dark' ? 'rgba(30,41,59,0.85)' : 'rgba(255,255,255,0.85)',
          bordercolor: theme === 'dark' ? 'rgba(148,163,184,0.25)' : '#e2e8f0',
          borderwidth: 1,
          borderpad: 6,
        },
      ],
    }),
    [theme, result],
  )

  return (
    <div ref={containerRef}>
      <Plot
        data={data}
        layout={layout}
        className="h-[380px] w-full sm:h-[440px]"
        ariaLabel={`Scatter plot of ${result.n} data points with fitted equation ${result.equation.plain} and R squared ${result.metrics.r2.toFixed(4)}`}
      />
    </div>
  )
}
