import { Link } from 'react-router-dom'
import { motion } from 'framer-motion'
import {
  ArrowRight,
  BookOpen,
  GraduationCap,
  Hash,
  Mail,
  School,
  Sigma,
  Sparkles,
} from 'lucide-react'
import { PageTransition } from '../components/layout/PageTransition'
import { Button } from '../components/ui/Button'
import { Badge } from '../components/ui/Badge'
import { Card } from '../components/ui/Card'

const team = [
  {
    name: 'Eamin Hossain',
    id: '242-15-823',
    email: 'eamin242-15-823@diu.edu.bd',
    initials: 'EH',
    accent: 'from-indigo-500 to-violet-500',
    ring: 'ring-indigo-100',
    chip: 'bg-indigo-50 text-indigo-700 ring-indigo-200/70',
  },
  {
    name: 'Ali Jahan Riashad',
    id: '242-15-846',
    email: 'riashad242-15-846@diu.edu.bd',
    initials: 'AJ',
    accent: 'from-sky-500 to-cyan-500',
    ring: 'ring-sky-100',
    chip: 'bg-sky-50 text-sky-700 ring-sky-200/70',
  },
  {
    name: 'Arafat Islam',
    id: '242-15-388',
    email: 'arafat242-15-388@diu.edu.bd',
    initials: 'AI',
    accent: 'from-violet-500 to-fuchsia-500',
    ring: 'ring-violet-100',
    chip: 'bg-violet-50 text-violet-700 ring-violet-200/70',
  },
  {
    name: 'Lauhe Mahfuz Udoy',
    id: '242-15-395',
    email: 'lauhe242-15-395@diu.edu.bd',
    initials: 'LM',
    accent: 'from-emerald-500 to-teal-500',
    ring: 'ring-emerald-100',
    chip: 'bg-emerald-50 text-emerald-700 ring-emerald-200/70',
  },
]

const DEPT = 'Dept. of Computer Science & Engineering'
const UNI = 'Daffodil International University'

const container = {
  hidden: {},
  show: { transition: { staggerChildren: 0.08 } },
}
const item = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { type: 'spring' as const, stiffness: 240, damping: 24 } },
}

export function About() {
  return (
    <PageTransition>
      <div className="bg-hero min-h-screen pb-24 pt-28">
        <div className="mx-auto max-w-5xl px-4 sm:px-6 lg:px-8">
          <div className="text-center">
            <Badge tone="indigo">
              <Sparkles className="h-3 w-3" />
              Developed by
            </Badge>
            <h1 className="mt-4 text-3xl font-bold tracking-tight text-slate-900 sm:text-4xl">
              The Team Behind <span className="text-gradient">CurveLab</span>
            </h1>
            <p className="mx-auto mt-4 max-w-2xl text-lg leading-relaxed text-slate-500">
              Designed and built as a Numerical Methods project — least squares curve fitting,
              from raw data to university-ready reports.
            </p>
          </div>

          <motion.div
            initial={{ opacity: 0, y: 18 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ type: 'spring', stiffness: 220, damping: 26, delay: 0.1 }}
            className="mt-10"
          >
            <Card className="relative overflow-hidden">
              <div className="pointer-events-none absolute -right-10 -top-10 h-36 w-36 rounded-full bg-gradient-to-br from-indigo-500 to-violet-500 opacity-[0.08]" />
              <div className="flex flex-col items-center gap-4 p-6 text-center sm:flex-row sm:text-left">
                <span className="flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br from-indigo-500 to-violet-500 text-white shadow-lg shadow-indigo-500/25">
                  <GraduationCap className="h-7 w-7" />
                </span>
                <div className="min-w-0">
                  <h2 className="text-lg font-bold text-slate-900">
                    Daffodil International University
                  </h2>
                  <p className="mt-0.5 text-sm text-slate-500">
                    Department of Computer Science and Engineering
                  </p>
                </div>
                <div className="sm:ml-auto">
                  <Badge tone="violet">
                    <Sigma className="h-3 w-3" />
                    Numerical Methods
                  </Badge>
                </div>
              </div>
            </Card>
          </motion.div>

          <motion.div
            variants={container}
            initial="hidden"
            whileInView="show"
            viewport={{ once: true, margin: '-60px' }}
            className="mt-8 grid gap-5 sm:grid-cols-2"
          >
            {team.map((m) => (
              <motion.div key={m.id} variants={item} className="h-full">
                <Card hover className="relative h-full overflow-hidden p-6">
                  <div
                    className={`pointer-events-none absolute -right-8 -top-8 h-28 w-28 rounded-full bg-gradient-to-br ${m.accent} opacity-[0.08]`}
                  />
                  <div className="flex items-center gap-4">
                    <span
                      className={`flex h-14 w-14 shrink-0 items-center justify-center rounded-2xl bg-gradient-to-br ${m.accent} text-lg font-bold text-white shadow-md ring-4 ${m.ring}`}
                    >
                      {m.initials}
                    </span>
                    <div className="min-w-0">
                      <h3 className="truncate text-[16px] font-bold text-slate-900">{m.name}</h3>
                      <span
                        className={`mt-1.5 inline-flex items-center gap-1 rounded-full px-2.5 py-0.5 font-mono text-xs font-semibold ring-1 ${m.chip}`}
                      >
                        <Hash className="h-3 w-3" />
                        {m.id}
                      </span>
                    </div>
                  </div>
                  <div className="mt-5 space-y-2.5 border-t border-slate-100 pt-4">
                    <a
                      href={`mailto:${m.email}`}
                      className="group/mail flex min-w-0 items-center gap-2.5 text-[13px] text-slate-500 transition-colors hover:text-indigo-600"
                    >
                      <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-slate-50 text-slate-400 ring-1 ring-slate-200/70 transition-colors group-hover/mail:bg-indigo-50 group-hover/mail:text-indigo-500">
                        <Mail className="h-3.5 w-3.5" />
                      </span>
                      <span className="truncate font-mono">{m.email}</span>
                    </a>
                    <div className="flex min-w-0 items-center gap-2.5 text-[13px] text-slate-500">
                      <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-slate-50 text-slate-400 ring-1 ring-slate-200/70">
                        <BookOpen className="h-3.5 w-3.5" />
                      </span>
                      <span className="truncate">{DEPT}</span>
                    </div>
                    <div className="flex min-w-0 items-center gap-2.5 text-[13px] text-slate-500">
                      <span className="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg bg-slate-50 text-slate-400 ring-1 ring-slate-200/70">
                        <School className="h-3.5 w-3.5" />
                      </span>
                      <span className="truncate">{UNI}</span>
                    </div>
                  </div>
                </Card>
              </motion.div>
            ))}
          </motion.div>

          <div className="mt-12 text-center">
            <Link to="/app">
              <Button size="lg">
                Try CurveLab
                <ArrowRight className="h-4 w-4" />
              </Button>
            </Link>
          </div>
        </div>
      </div>
    </PageTransition>
  )
}
