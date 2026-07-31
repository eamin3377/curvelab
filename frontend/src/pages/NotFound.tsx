import { LinkButton } from '../components/ui/LinkButton'
import { motion } from 'framer-motion'
import { ArrowLeft } from 'lucide-react'
import { PageTransition } from '../components/layout/PageTransition'

const dots: Array<[number, number, number]> = [
  // 4
  [18, 20, 0], [14, 32, 0.05], [10, 44, 0.1], [26, 20, 0.02], [26, 32, 0.06], [26, 44, 0.12], [10, 44, 0], [26, 44, 0], [18, 44, 0.08],
  // 0
  [48, 20, 0.04], [58, 20, 0.08], [44, 30, 0.1], [62, 30, 0.12], [44, 40, 0.14], [62, 40, 0.16], [48, 50, 0.18], [58, 50, 0.2],
  // 4
  [86, 20, 0.1], [82, 32, 0.14], [78, 44, 0.18], [94, 20, 0.12], [94, 32, 0.16], [94, 44, 0.2], [78, 44, 0], [94, 44, 0], [86, 44, 0.22],
]

export function NotFound() {
  return (
    <PageTransition>
      <div className="bg-hero flex min-h-screen flex-col items-center justify-center px-4 pt-16 text-center">
        <svg viewBox="0 0 110 70" className="w-72 max-w-full" role="img" aria-label="404">
          {dots.map(([x, y, d], i) => (
            <motion.circle
              key={i}
              cx={x}
              cy={y}
              r="3.4"
              fill={i % 3 === 0 ? '#7c3aed' : i % 3 === 1 ? '#4f46e5' : '#0ea5e9'}
              stroke="#eef2ff"
              strokeWidth="1.6"
              initial={{ scale: 0, opacity: 0 }}
              animate={{ scale: 1, opacity: 1 }}
              transition={{ delay: 0.15 + d, type: 'spring', stiffness: 320, damping: 16 }}
            />
          ))}
          <motion.path
            d="M 6 62 Q 36 52 55 60 T 104 56"
            fill="none"
            stroke="#c7d2fe"
            strokeWidth="2.5"
            strokeLinecap="round"
            strokeDasharray="1000"
            initial={{ strokeDashoffset: 1000 }}
            animate={{ strokeDashoffset: 0 }}
            transition={{ duration: 1.4, delay: 0.5, ease: 'easeInOut' }}
          />
        </svg>

        <h1 className="mt-8 text-2xl font-bold tracking-tight text-slate-900">
          This data point doesn't fit the curve
        </h1>
        <p className="mt-3 max-w-sm text-[15px] leading-relaxed text-slate-500">
          The page you're looking for is an outlier — it was moved, renamed, or never existed.
        </p>
        <LinkButton to="/" size="lg" className="mt-8">
            <ArrowLeft className="h-4 w-4" />
            Back to home
        </LinkButton>
      </div>
    </PageTransition>
  )
}
