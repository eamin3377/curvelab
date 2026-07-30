export type ChartTheme = 'light' | 'dark'

export function baseLayout(theme: ChartTheme) {
  const dark = theme === 'dark'
  return {
    paper_bgcolor: dark ? '#0f172a' : 'rgba(0,0,0,0)',
    plot_bgcolor: dark ? '#0f172a' : 'rgba(0,0,0,0)',
    font: {
      family: 'Inter, ui-sans-serif, system-ui, sans-serif',
      size: 12.5,
      color: dark ? '#cbd5e1' : '#475569',
    },
    margin: { l: 52, r: 20, t: 24, b: 44 },
    xaxis: {
      gridcolor: dark ? 'rgba(148,163,184,0.15)' : '#eef2f7',
      zerolinecolor: dark ? 'rgba(148,163,184,0.3)' : '#e2e8f0',
      linecolor: dark ? 'rgba(148,163,184,0.25)' : '#e2e8f0',
      tickfont: { size: 11.5 },
      title: { font: { size: 12.5, color: dark ? '#94a3b8' : '#64748b' } },
    },
    yaxis: {
      gridcolor: dark ? 'rgba(148,163,184,0.15)' : '#eef2f7',
      zerolinecolor: dark ? 'rgba(148,163,184,0.3)' : '#e2e8f0',
      linecolor: dark ? 'rgba(148,163,184,0.25)' : '#e2e8f0',
      tickfont: { size: 11.5 },
      title: { font: { size: 12.5, color: dark ? '#94a3b8' : '#64748b' } },
    },
    legend: {
      orientation: 'h',
      x: 0,
      y: 1.12,
      font: { size: 12, color: dark ? '#cbd5e1' : '#64748b' },
      bgcolor: 'rgba(0,0,0,0)',
    },
    hoverlabel: {
      bgcolor: dark ? '#1e293b' : '#0f172a',
      bordercolor: 'rgba(0,0,0,0)',
      font: { family: 'Inter, sans-serif', size: 12.5, color: '#f8fafc' },
    },
    dragmode: 'zoom',
  }
}

export const SERIES = {
  points: '#4f46e5',
  pointsOutline: '#eef2ff',
  curve: '#0ea5e9',
  band: 'rgba(14,165,233,0.09)',
  residual: '#7c3aed',
}
