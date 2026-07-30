export function cn(...classes: Array<string | false | null | undefined>) {
  return classes.filter(Boolean).join(' ')
}

export function formatNumber(value: number, digits = 4): string {
  if (!Number.isFinite(value)) return '—'
  if (value !== 0 && (Math.abs(value) >= 1e7 || Math.abs(value) < 1e-4)) {
    return value.toExponential(digits)
  }
  return value.toLocaleString('en-US', {
    minimumFractionDigits: 0,
    maximumFractionDigits: digits,
  })
}
