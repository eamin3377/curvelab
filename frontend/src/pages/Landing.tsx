import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  ArrowRight,
  ChartSpline,
  Download,
  FileText,
  FunctionSquare,
  Gauge,
  Import,
  ListOrdered,
  Play,
  Sigma,
  Sparkles,
} from 'lucide-react'
import { useState } from 'react'
import { PageTransition } from '../components/layout/PageTransition'
import { Button } from '../components/ui/Button'
import { Badge } from '../components/ui/Badge'
import { Card } from '../components/ui/Card'
import { CountUp } from '../components/ui/CountUp'
import { Equation } from '../components/ui/Equation'
import { SegmentedControl } from '../components/ui/SegmentedControl'
import { HeroChart } from '../features/landing/HeroChart'
import { isExponentialFamily, MODEL_META, type ModelId } from '../lib/types'

const rise = {
  hidden: { opacity: 0, y: 22 },
  show: { opacity: 1, y: 0, transition: { type: 'spring' as const, stiffness: 220, damping: 26 } },
}
const stagger = { hidden: {}, show: { transition: { staggerChildren: 0.08 } } }

const features = [
  {
    icon: Sigma,
    title: 'Least Squares Engine',
    body: 'Every summation — Σx, Σy, Σxy, Σx², Σx³, Σx⁴ — computed instantly and shown transparently, exactly as you would on paper.',
    accent: 'from-indigo-500 to-violet-500',
  },
  {
    icon: ListOrdered,
    title: 'Step-by-Step Solutions',
    body: 'From normal equations through Gaussian elimination to the final coefficients, every step is typeset like a textbook.',
    accent: 'from-violet-500 to-fuchsia-500',
  },
  {
    icon: ChartSpline,
    title: 'Interactive Graphs',
    body: 'Zoom, pan, hover and export. Animated regression curves, residual plots and confidence bands on a premium canvas.',
    accent: 'from-sky-500 to-cyan-500',
  },
  {
    icon: Import,
    title: 'Smart Data Import',
    body: 'Type values, paste straight from Excel, or drop CSV, TXT and JSON files. Duplicates and empty rows are cleaned automatically.',
    accent: 'from-emerald-500 to-teal-500',
  },
  {
    icon: FileText,
    title: 'University Reports',
    body: 'One click generates a polished PDF or Word report with cover page, tables, formulas, graphs and conclusions.',
    accent: 'from-amber-500 to-orange-500',
  },
  {
    icon: Gauge,
    title: 'Instant Metrics',
    body: 'R², RMSE, MAE and MSE with residual analysis — know exactly how good your fit is the moment you press solve.',
    accent: 'from-rose-500 to-pink-500',
  },
]

const algoDetail: Record<
  ModelId,
  { blurb: string; normal: string; use: string }
> = {
  linear: {
    blurb:
      'Fits the straight line y = a + bx by minimizing the sum of squared vertical distances. The two normal equations are solved directly for the intercept a and slope b.',
    normal:
      '\\begin{aligned} na + b\\sum x_i &= \\sum y_i \\\\ a\\sum x_i + b\\sum x_i^2 &= \\sum x_i y_i \\end{aligned}',
    use: 'Best when the scatter plot shows a constant-rate trend — spring extension, unit cost, calibration curves.',
  },
  polynomial: {
    blurb:
      'Fits y = a₀ + a₁x + a₂x² by extending the least squares principle to three coefficients, producing a symmetric 3×3 system solved by Gaussian elimination.',
    normal:
      '\\begin{bmatrix} n & \\sum x & \\sum x^2 \\\\ \\sum x & \\sum x^2 & \\sum x^3 \\\\ \\sum x^2 & \\sum x^3 & \\sum x^4 \\end{bmatrix} \\begin{bmatrix} a_0 \\\\ a_1 \\\\ a_2 \\end{bmatrix} = \\begin{bmatrix} \\sum y \\\\ \\sum xy \\\\ \\sum x^2 y \\end{bmatrix}',
    use: 'Best for curved trends with one turning point — projectile motion, efficiency curves, dose response.',
  },
  exponential: {
    blurb:
      'Fits y = aeᵇˣ by taking logarithms: ln y = ln a + bx becomes a linear problem in (x, ln y), solved with the standard linear normal equations.',
    normal:
      '\\begin{aligned} n\\ln a + b\\sum x_i &= \\sum \\ln y_i \\\\ \\ln a \\sum x_i + b\\sum x_i^2 &= \\sum x_i \\ln y_i \\end{aligned}',
    use: 'Best for growth and decay processes — bacterial growth, radioactive decay, compound interest.',
  },
  exponential_abx: {
    blurb:
      'Fits y = abˣ by taking logarithms: ln y = ln a + x·ln b is linear in (x, ln y). The 2×2 system solves for ln a and ln b, then a = e^(ln a) and b = e^(ln b).',
    normal:
      '\\begin{aligned} n\\ln a + \\ln b\\sum x_i &= \\sum \\ln y_i \\\\ \\ln a \\sum x_i + \\ln b \\sum x_i^2 &= \\sum x_i \\ln y_i \\end{aligned}',
    use: 'Best when data grows by a constant factor per step — population doubling, depreciation, interest per period.',
  },
  power: {
    blurb:
      'Fits y = axᵇ with a log-log transform: ln y = ln a + b·ln x is linear in (ln x, ln y). Requires both x > 0 and y > 0.',
    normal:
      '\\begin{aligned} n\\ln a + b\\sum \\ln x_i &= \\sum \\ln y_i \\\\ \\ln a \\sum \\ln x_i + b\\sum (\\ln x_i)^2 &= \\sum \\ln x_i \\ln y_i \\end{aligned}',
    use: 'Best for scaling laws — area vs length, power dissipation vs voltage, allometric growth.',
  },
}

export function Landing() {
  const [algo, setAlgo] = useState<ModelId>('linear')

  return (
    <PageTransition>
      {/* ── Hero ─────────────────────────────────────────── */}
      <section className="bg-hero relative overflow-hidden pt-16">
        <div className="pointer-events-none absolute -left-32 top-16 h-96 w-96 rounded-full bg-indigo-200/40 blur-3xl motion-safe:animate-float-slow" />
        <div className="pointer-events-none absolute -right-24 top-48 h-80 w-80 rounded-full bg-sky-200/40 blur-3xl motion-safe:animate-float-slower" />

        <div className="relative mx-auto grid max-w-7xl 2xl:max-w-[1600px] items-center gap-14 px-4 pb-24 pt-16 sm:px-6 lg:grid-cols-2 lg:px-8 lg:pt-24">
          <motion.div variants={stagger} initial="hidden" animate="show">
            <motion.div variants={rise}>
              <Badge tone="indigo" className="px-3 py-1">
                <Sparkles className="h-3 w-3" />
                Numerical Methods · Least Squares
              </Badge>
            </motion.div>
            <motion.h1
              variants={rise}
              className="mt-5 text-4xl font-extrabold leading-[1.08] tracking-tight text-slate-900 sm:text-5xl lg:text-6xl"
            >
              Curve fitting,
              <br />
              <span className="text-gradient">beautifully solved.</span>
            </motion.h1>
            <motion.p
              variants={rise}
              className="mt-6 max-w-lg text-lg leading-relaxed text-slate-500"
            >
              Enter your data and watch CurveLab compute every summation, solve the normal
              equations, and draw a publication-quality regression graph — instantly.
            </motion.p>
            <motion.div variants={rise} className="mt-8 flex flex-wrap items-center gap-3">
              <Link to="/app">
                <Button size="lg">
                  Start Fitting
                  <ArrowRight className="h-4 w-4" />
                </Button>
              </Link>
              <Link to="/methods">
                <Button variant="secondary" size="lg">
                  <Play className="h-4 w-4" />
                  See how it works
                </Button>
              </Link>
            </motion.div>
            <motion.div variants={rise} className="mt-10 flex items-center gap-6">
              {[
                ['Linear', 'y = a + bx'],
                ['Polynomial', 'y = a₀+a₁x+a₂x²'],
                ['Exponential', 'y = aeᵇˣ'],
              ].map(([name, eq]) => (
                <div key={name}>
                  <p className="text-[13px] font-semibold text-slate-700">{name}</p>
                  <p className="font-mono text-xs text-slate-400">{eq}</p>
                </div>
              ))}
            </motion.div>
          </motion.div>

          <motion.div
            initial={{ opacity: 0, scale: 0.94, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            transition={{ delay: 0.25, type: 'spring', stiffness: 200, damping: 24 }}
            className="relative"
          >
            <div className="glass relative rounded-3xl p-6 shadow-[0_24px_80px_rgb(79_70_229/0.16)]">
              <div className="mb-4 flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="h-2.5 w-2.5 rounded-full bg-red-300" />
                  <span className="h-2.5 w-2.5 rounded-full bg-amber-300" />
                  <span className="h-2.5 w-2.5 rounded-full bg-emerald-300" />
                </div>
                <Badge tone="emerald">Live fit</Badge>
              </div>
              <HeroChart />
            </div>

            <motion.div
              initial={{ opacity: 0, x: -14 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.7 }}
              className="glass absolute -left-4 top-24 hidden rounded-2xl px-4 py-3 shadow-lg sm:block"
            >
              <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">R² Score</p>
              <p className="font-mono text-lg font-bold text-indigo-600">0.9931</p>
            </motion.div>
            <motion.div
              initial={{ opacity: 0, x: 14 }}
              animate={{ opacity: 1, x: 0 }}
              transition={{ delay: 0.85 }}
              className="glass absolute -right-3 bottom-16 hidden rounded-2xl px-4 py-3 shadow-lg sm:block"
            >
              <p className="text-[11px] font-semibold uppercase tracking-wider text-slate-400">Equation</p>
              <p className="font-mono text-sm font-semibold text-slate-700">y = 2.847 + 1.932x</p>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* ── Counters ─────────────────────────────────────── */}
      <section className="border-y border-slate-100 bg-white">
        <div className="mx-auto grid max-w-7xl 2xl:max-w-[1600px] grid-cols-2 gap-8 px-4 py-14 sm:px-6 lg:grid-cols-4 lg:px-8">
          {[
            { value: 3, suffix: '', label: 'Fitting methods', digits: 0 },
            { value: 8, suffix: '', label: 'Export formats', digits: 0 },
            { value: 300, suffix: ' ms', label: 'Typical solve time', digits: 0, prefix: '<' },
            { value: 50000, suffix: '', label: 'Max data points', digits: 0 },
          ].map((s) => (
            <div key={s.label} className="text-center">
              <p className="font-mono text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
                <CountUp value={s.value} digits={s.digits} prefix={s.prefix ?? ''} suffix={s.suffix} duration={1.4} />
              </p>
              <p className="mt-1.5 text-sm font-medium text-slate-400">{s.label}</p>
            </div>
          ))}
        </div>
      </section>

      {/* ── Features ─────────────────────────────────────── */}
      <section className="bg-slate-50/60 py-24">
        <div className="mx-auto max-w-7xl 2xl:max-w-[1600px] px-4 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <Badge tone="violet">Everything included</Badge>
            <h2 className="mt-4 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
              A complete numerical methods lab
            </h2>
            <p className="mt-4 text-lg text-slate-500">
              From raw data to a graded-ready report — every stage of the least squares workflow,
              polished to perfection.
            </p>
          </div>

          <motion.div
            variants={stagger}
            initial="hidden"
            whileInView="show"
            viewport={{ once: true, margin: '-80px' }}
            className="mt-14 grid gap-6 sm:grid-cols-2 lg:grid-cols-3"
          >
            {features.map((f) => (
              <motion.div key={f.title} variants={rise}>
                <Card hover className="group h-full p-6">
                  <span
                    className={`inline-flex h-11 w-11 items-center justify-center rounded-xl bg-gradient-to-br ${f.accent} text-white shadow-[0_6px_16px_rgb(79_70_229/0.25)] transition-transform duration-200 group-hover:scale-110`}
                  >
                    <f.icon className="h-5 w-5" />
                  </span>
                  <h3 className="mt-5 text-[17px] font-bold text-slate-900">{f.title}</h3>
                  <p className="mt-2.5 text-[14.5px] leading-relaxed text-slate-500">{f.body}</p>
                </Card>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </section>

      {/* ── Algorithms ───────────────────────────────────── */}
      <section className="bg-white py-24">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <div className="mx-auto max-w-2xl text-center">
            <Badge tone="sky">The mathematics</Badge>
            <h2 className="mt-4 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
              Three models, one principle
            </h2>
            <p className="mt-4 text-lg text-slate-500">
              Every fit minimizes the sum of squared residuals — only the normal equations change.
            </p>
          </div>

          <div className="mx-auto mt-10 max-w-md space-y-3">
            <SegmentedControl
              id="algo"
              options={[
                { value: 'linear', label: 'Linear' },
                { value: 'polynomial', label: 'Polynomial' },
                { value: 'exponential', label: 'Exponential' },
              ]}
              value={(isExponentialFamily(algo) ? 'exponential' : algo) as 'linear' | 'polynomial' | 'exponential'}
              onChange={(v) => setAlgo(v as ModelId)}
            />
            {isExponentialFamily(algo) && (
              <motion.div
                initial={{ opacity: 0, y: -6 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ duration: 0.2 }}
              >
                <SegmentedControl
                  id="algo-exp"
                  options={[
                    { value: 'exponential', label: 'y = aeᵇˣ' },
                    { value: 'exponential_abx', label: 'y = abˣ' },
                    { value: 'power', label: 'y = axᵇ' },
                  ]}
                  value={algo}
                  onChange={(v) => setAlgo(v as ModelId)}
                />
              </motion.div>
            )}
          </div>

          <motion.div
            key={algo}
            initial={{ opacity: 0, y: 14 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.3, ease: [0.16, 1, 0.3, 1] }}
            className="mt-8"
          >
            <Card className="overflow-hidden">
              <div className="grid lg:grid-cols-[1.1fr_1fr]">
                <div className="p-8 lg:p-10">
                  <div className="flex items-center gap-3">
                    <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-500 to-violet-500 text-white shadow-md">
                      <FunctionSquare className="h-5 w-5" />
                    </span>
                    <h3 className="text-xl font-bold text-slate-900">
                      {MODEL_META[algo].label} fitting
                    </h3>
                  </div>
                  <div className="mt-5 flex items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-50/80 to-sky-50/60 py-5 ring-1 ring-indigo-100/60">
                    <Equation latex={MODEL_META[algo].formula} className="text-xl text-slate-800" />
                  </div>
                  <p className="mt-5 text-[14.5px] leading-relaxed text-slate-500">
                    {algoDetail[algo].blurb}
                  </p>
                  <p className="mt-4 rounded-xl border border-emerald-100 bg-emerald-50/60 px-4 py-3 text-[13.5px] leading-relaxed text-emerald-800">
                    {algoDetail[algo].use}
                  </p>
                </div>
                <div className="border-t border-slate-100 bg-slate-50/60 p-8 lg:border-l lg:border-t-0 lg:p-10">
                  <p className="text-xs font-semibold uppercase tracking-wider text-slate-400">
                    Normal equations
                  </p>
                  <div className="mt-4 overflow-x-auto scrollbar-thin">
                    <Equation latex={algoDetail[algo].normal} block className="text-[15px] text-slate-700" />
                  </div>
                  <Link to="/app" className="mt-8 inline-block">
                    <Button variant="secondary" size="sm">
                      Try it in the workspace
                      <ArrowRight className="h-3.5 w-3.5" />
                    </Button>
                  </Link>
                </div>
              </div>
            </Card>
          </motion.div>
        </div>
      </section>

      {/* ── CTA ──────────────────────────────────────────── */}
      <section className="relative overflow-hidden bg-gradient-to-br from-indigo-600 via-indigo-600 to-violet-600 py-24">
        <div className="pointer-events-none absolute -left-24 -top-24 h-80 w-80 rounded-full bg-white/10 blur-3xl" />
        <div className="pointer-events-none absolute -bottom-32 -right-16 h-96 w-96 rounded-full bg-sky-400/20 blur-3xl" />
        <div className="relative mx-auto max-w-3xl px-4 text-center sm:px-6">
          <h2 className="text-3xl font-bold tracking-tight text-white sm:text-4xl">
            Your data has a story.
            <br />
            Fit the curve that tells it.
          </h2>
          <p className="mx-auto mt-4 max-w-xl text-lg text-indigo-100">
            Open the workspace, load a sample dataset, and get a complete least squares analysis in
            under a second.
          </p>
          <Link to="/app" className="mt-8 inline-block">
            <Button
              size="lg"
              className="bg-white from-white to-white !text-indigo-700 shadow-[0_8px_28px_rgb(0_0_0/0.2)] hover:bg-indigo-50"
            >
              Open Workspace
              <ArrowRight className="h-4 w-4" />
            </Button>
          </Link>
          <p className="mt-6 flex items-center justify-center gap-2 text-sm text-indigo-200">
            <Download className="h-4 w-4" />
            Free · No sign-up · Exports included
          </p>
        </div>
      </section>
    </PageTransition>
  )
}
