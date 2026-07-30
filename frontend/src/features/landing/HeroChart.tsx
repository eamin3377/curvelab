import { useEffect, useMemo, useState } from 'react'
import { motion } from 'framer-motion'

function generate(seed: number) {
  const pts: Array<{ x: number; y: number }> = []
  const a = 40 + (seed % 3) * 18
  const b = 0.55 + (seed % 5) * 0.06
  for (let i = 0; i <= 10; i++) {
    const x = 30 + i * 40
    const noise = Math.sin(seed * 7.3 + i * 2.1) * 16
    pts.push({ x, y: 260 - (a + b * i * 26) + noise })
  }
  return { pts, a, b }
}

export function HeroChart() {
  const [seed, setSeed] = useState(1)

  useEffect(() => {
    const id = window.setInterval(() => setSeed((s) => s + 1), 4200)
    return () => window.clearInterval(id)
  }, [])

  const { pts } = useMemo(() => generate(seed), [seed])

  const linePath = useMemo(() => {
    const first = pts[0]
    const last = pts[pts.length - 1]
    const meanShift = 8
    return `M ${first.x} ${first.y + meanShift} L ${last.x} ${last.y - meanShift}`
  }, [pts])

  return (
    <svg
      viewBox="0 0 470 300"
      className="w-full"
      role="img"
      aria-label="Animated preview of a regression line fitted through scattered data points"
    >
      {[60, 120, 180, 240].map((y) => (
        <line key={y} x1="20" y1={y} x2="450" y2={y} stroke="#e8edf5" strokeWidth="1" />
      ))}
      {[110, 190, 270, 350].map((x) => (
        <line key={x} x1={x} y1="20" x2={x} y2="280" stroke="#eef2f8" strokeWidth="1" />
      ))}

      <motion.path
        key={`line-${seed}`}
        d={linePath}
        fill="none"
        stroke="url(#heroGrad)"
        strokeWidth="3.5"
        strokeLinecap="round"
        initial={{ pathLength: 0, opacity: 0 }}
        animate={{ pathLength: 1, opacity: 1 }}
        transition={{ duration: 1.1, ease: 'easeInOut', delay: 0.35 }}
      />

      {pts.map((p, i) => (
        <motion.circle
          key={`${seed}-${i}`}
          cx={p.x}
          cy={p.y}
          r="6"
          fill="#4f46e5"
          stroke="#eef2ff"
          strokeWidth="2.5"
          initial={{ scale: 0, opacity: 0 }}
          animate={{ scale: 1, opacity: 1 }}
          transition={{ delay: i * 0.05, type: 'spring', stiffness: 380, damping: 18 }}
        />
      ))}

      <defs>
        <linearGradient id="heroGrad" x1="0" y1="0" x2="1" y2="0">
          <stop offset="0" stopColor="#4f46e5" />
          <stop offset="1" stopColor="#0ea5e9" />
        </linearGradient>
      </defs>
    </svg>
  )
}
