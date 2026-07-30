import { useMemo } from 'react'
import katex from 'katex'
import 'katex/dist/katex.min.css'
import { cn } from '../../lib/utils'

export function Equation({
  latex,
  block = false,
  className,
}: {
  latex: string
  block?: boolean
  className?: string
}) {
  const html = useMemo(() => {
    try {
      return katex.renderToString(latex, {
        displayMode: block,
        throwOnError: false,
        output: 'htmlAndMathml',
      })
    } catch {
      return latex
    }
  }, [latex, block])

  return (
    <span
      className={cn(block ? 'block overflow-x-auto py-1 scrollbar-thin' : 'inline-block', className)}
      dangerouslySetInnerHTML={{ __html: html }}
    />
  )
}
