import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import { ArrowRight, BookOpen, FunctionSquare, GitBranch, Sigma } from 'lucide-react'
import { PageTransition } from '../components/layout/PageTransition'
import { Button } from '../components/ui/Button'
import { Badge } from '../components/ui/Badge'
import { Card } from '../components/ui/Card'
import { Equation } from '../components/ui/Equation'

const sections = [
  {
    id: 'principle',
    icon: BookOpen,
    badge: 'Foundation' as const,
    title: 'The Least Squares Principle',
    body: [
      'Given n data points (xᵢ, yᵢ), curve fitting asks: which curve of a chosen form passes "closest" to all points? The Method of Least Squares defines closeness as the sum of squared vertical distances between each observation and the curve.',
      'Squaring removes sign, penalizes large errors more heavily, and — crucially — makes S differentiable. Minimizing S means setting its partial derivatives with respect to every unknown coefficient to zero. That system of equations is called the normal equations.',
    ],
    latex: 'S = \\sum_{i=1}^{n} \\left( y_i - \\hat{y}_i \\right)^2 \\quad\\longrightarrow\\quad \\frac{\\partial S}{\\partial a_k} = 0 \\;\\; \\forall k',
  },
  {
    id: 'linear',
    icon: GitBranch,
    badge: 'Model 1' as const,
    title: 'Linear Fitting — y = a + bx',
    body: [
      'For a straight line, the two unknowns produce exactly two normal equations. Solving the 2×2 system gives closed-form formulas for the intercept and slope.',
      'This is the workhorse of numerical methods: fast, stable, and interpretable. The slope b is the best estimate of the constant rate of change.',
    ],
    latex:
      'b = \\frac{n\\sum x_i y_i - \\sum x_i \\sum y_i}{n\\sum x_i^2 - \\left(\\sum x_i\\right)^2}, \\qquad a = \\bar{y} - b\\bar{x}',
  },
  {
    id: 'polynomial',
    icon: Sigma,
    badge: 'Model 2' as const,
    title: 'Polynomial Fitting — y = a₀ + a₁x + a₂x²',
    body: [
      'The quadratic model introduces a third coefficient, and the normal equations become a symmetric 3×3 system built from summations up to Σx⁴. Higher degrees follow the same pattern: degree m needs summations up to Σx²ᵐ.',
      'Because the system is symmetric, it is efficiently and accurately solved by Gaussian elimination with partial pivoting — the algorithm CurveLab shows you step by step.',
    ],
    latex:
      '\\begin{bmatrix} n & \\sum x & \\sum x^2 \\\\ \\sum x & \\sum x^2 & \\sum x^3 \\\\ \\sum x^2 & \\sum x^3 & \\sum x^4 \\end{bmatrix} \\begin{bmatrix} a_0 \\\\ a_1 \\\\ a_2 \\end{bmatrix} = \\begin{bmatrix} \\sum y \\\\ \\sum xy \\\\ \\sum x^2 y \\end{bmatrix}',
  },
  {
    id: 'exponential',
    icon: FunctionSquare,
    badge: 'Model 3' as const,
    title: 'Exponential Fitting — y = aeᵇˣ',
    body: [
      'Exponential models are nonlinear, but a logarithmic transformation linearizes them: taking ln of both sides turns y = aeᵇˣ into ln y = ln a + bx — a straight line in (x, ln y).',
      'We fit the transformed data with the linear normal equations, then recover a = e^(ln a). One requirement: every y must be positive, since ln y is undefined otherwise. CurveLab validates this automatically.',
    ],
    latex:
      'y = ae^{bx} \\;\\;\\xrightarrow{\\;\\ln\\;}\\;\\; \\ln y = \\ln a + bx \\;\\;\\Longrightarrow\\;\\; a = e^{\\,\\frac{\\sum \\ln y_i - b\\sum x_i}{n}}',
  },
]

const badgeTone = { Foundation: 'slate', 'Model 1': 'indigo', 'Model 2': 'violet', 'Model 3': 'sky' } as const

export function Methods() {
  return (
    <PageTransition>
      <div className="bg-hero min-h-screen pb-24 pt-28">
        <div className="mx-auto max-w-4xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <Badge tone="indigo">Theory reference</Badge>
            <h1 className="mt-4 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
              Methods & Mathematics
            </h1>
            <p className="mx-auto mt-4 max-w-2xl text-lg leading-relaxed text-slate-500">
              The complete theory behind every fit CurveLab performs — the same derivation your
              step-by-step solution follows.
            </p>
          </div>

          <div className="mt-14 space-y-6">
            {sections.map((s, i) => (
              <motion.div
                key={s.id}
                initial={{ opacity: 0, y: 22 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true, margin: '-60px' }}
                transition={{ type: 'spring', stiffness: 220, damping: 26, delay: i * 0.04 }}
              >
                <Card hover className="overflow-hidden">
                  <div className="p-8">
                    <div className="flex items-center gap-3">
                      <span className="flex h-10 w-10 items-center justify-center rounded-xl bg-gradient-to-br from-indigo-50 to-violet-50 text-indigo-600 ring-1 ring-indigo-100">
                        <s.icon className="h-5 w-5" />
                      </span>
                      <Badge tone={badgeTone[s.badge]}>{s.badge}</Badge>
                    </div>
                    <h2 className="mt-4 text-xl font-bold text-slate-900">{s.title}</h2>
                    {s.body.map((p) => (
                      <p key={p.slice(0, 24)} className="mt-3 text-[14.5px] leading-relaxed text-slate-500">
                        {p}
                      </p>
                    ))}
                    <div className="mt-5 overflow-x-auto rounded-2xl border border-indigo-100/70 bg-gradient-to-br from-indigo-50/70 to-sky-50/50 px-5 py-4 scrollbar-thin">
                      <Equation latex={s.latex} block className="text-[15px] text-slate-700" />
                    </div>
                  </div>
                </Card>
              </motion.div>
            ))}
          </div>

          <div className="mt-12 text-center">
            <Link to="/app">
              <Button size="lg">
                Apply the theory now
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </PageTransition>
  )
}
