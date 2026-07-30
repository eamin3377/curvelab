// Registry that lets the ExportBar capture the on-screen Plotly chart as a
// PNG without prop drilling. GraphCard registers its plot container here.

let chartEl: HTMLElement | null = null

export function registerChart(el: HTMLElement | null): void {
  chartEl = el
}

export async function captureChartPng(): Promise<string | null> {
  if (!chartEl || !chartEl.isConnected) return null
  const Plotly = await import('plotly.js-basic-dist-min')
  const dataUrl = await Plotly.toImage(chartEl, {
    format: 'png',
    width: 1280,
    height: 800,
    scale: 2,
  }).catch(() => null)
  if (!dataUrl) return null
  const comma = dataUrl.indexOf(',')
  return comma >= 0 ? dataUrl.slice(comma + 1) : null
}
