import { useEffect, useRef, useState } from 'react'
import type * as PlotlyType from 'plotly.js-basic-dist-min'

// Lazy-load Plotly so its 1 MB bundle only downloads when a chart is
// actually rendered, not on every page load.
let _plotly: typeof PlotlyType | null = null
async function loadPlotly(): Promise<typeof PlotlyType> {
  if (!_plotly) _plotly = await import('plotly.js-basic-dist-min')
  return _plotly
}

export type { PlotlyData, PlotlyLayout } from 'plotly.js-basic-dist-min'

export function Plot({
  data,
  layout,
  className,
  ariaLabel,
}: {
  data: PlotlyType.PlotlyData[]
  layout: PlotlyType.PlotlyLayout
  className?: string
  ariaLabel?: string
}) {
  const ref = useRef<HTMLDivElement>(null)
  const [ready, setReady] = useState(false)

  useEffect(() => {
    let cancelled = false
    loadPlotly().then((Plotly) => {
      if (cancelled) return
      setReady(true)
      const el = ref.current
      if (!el) return
      void Plotly.react(el, data, layout, {
        responsive: true,
        displaylogo: false,
        scrollZoom: true,
        modeBarButtonsToRemove: ['lasso2d', 'select2d'],
        toImageButtonOptions: { format: 'png', filename: 'curvelab-chart', scale: 2 },
      })
    })
    return () => { cancelled = true }
  }, [data, layout])

  useEffect(() => {
    const el = ref.current
    if (!el || typeof ResizeObserver === 'undefined' || !ready) return
    let raf = 0
    const observer = new ResizeObserver(() => {
      cancelAnimationFrame(raf)
      raf = requestAnimationFrame(() => {
        if (el.isConnected) void loadPlotly().then((P) => P.Plots.resize(el))
      })
    })
    observer.observe(el)
    return () => {
      cancelAnimationFrame(raf)
      observer.disconnect()
    }
  }, [ready])

  useEffect(() => {
    const el = ref.current
    return () => {
      if (el && ready) loadPlotly().then((P) => P.purge(el))
    }
  }, [ready])

  return <div ref={ref} className={`${className ?? ''} min-w-0`} role="img" aria-label={ariaLabel} />
}
