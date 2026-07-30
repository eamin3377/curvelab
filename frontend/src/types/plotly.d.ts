declare module 'plotly.js-basic-dist-min' {
  export type PlotlyData = Record<string, unknown>
  export type PlotlyLayout = Record<string, unknown>
  export type PlotlyConfig = Record<string, unknown>
  export function newPlot(
    el: HTMLElement,
    data: PlotlyData[],
    layout?: PlotlyLayout,
    config?: PlotlyConfig,
  ): Promise<void>
  export function react(
    el: HTMLElement,
    data: PlotlyData[],
    layout?: PlotlyLayout,
    config?: PlotlyConfig,
  ): Promise<void>
  export function purge(el: HTMLElement): void
  export namespace Plots {
    function resize(el: HTMLElement): void
  }
  export function downloadImage(
    el: HTMLElement,
    opts: { format: string; filename: string; width?: number; height?: number; scale?: number },
  ): Promise<string>
  export function toImage(
    el: HTMLElement,
    opts: { format: string; width?: number; height?: number; scale?: number },
  ): Promise<string>
}
