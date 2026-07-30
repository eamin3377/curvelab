import { useEffect, useRef } from 'react'
import * as Plotly from 'plotly.js-basic-dist-min'

export type { PlotlyData, PlotlyLayout } from 'plotly.js-basic-dist-min'

export function Plot({
  data,
  layout,
  className,
  ariaLabel,
}: {
  data: Plotly.PlotlyData[]
  layout: Plotly.PlotlyLayout
  className?: string
  ariaLabel?: string
}) {
  const ref = useRef<HTMLDivElement>(null)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    void Plotly.react(el, data, layout, {
      responsive: true,
      displaylogo: false,
      scrollZoom: true,
      modeBarButtonsToRemove: ['lasso2d', 'select2d'],
      toImageButtonOptions: { format: 'png', filename: 'curvelab-chart', scale: 2 },
    })
  }, [data, layout])

  // Redraw whenever the container actually changes size. Plotly's own
  // `responsive` mode only listens to window resize and can miss layout
  // reflows (breakpoint stacking, sidebar toggle, zoom). ResizeObserver
  // catches every case in both directions.
  useEffect(() => {
    const el = ref.current
    if (!el || typeof ResizeObserver === 'undefined') return
    let raf = 0
    const observer = new ResizeObserver(() => {
      cancelAnimationFrame(raf)
      raf = requestAnimationFrame(() => {
        if (el.isConnected) void Plotly.Plots.resize(el)
      })
    })
    observer.observe(el)
    return () => {
      cancelAnimationFrame(raf)
      observer.disconnect()
    }
  }, [])

  useEffect(() => {
    const el = ref.current
    return () => {
      if (el) Plotly.purge(el)
    }
  }, [])

  return <div ref={ref} className={`${className ?? ''} min-w-0`} role="img" aria-label={ariaLabel} />
}
