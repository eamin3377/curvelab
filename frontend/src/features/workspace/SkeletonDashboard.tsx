export function SkeletonDashboard() {
  return (
    <div className="space-y-6" aria-hidden="true">
      <div className="grid grid-cols-2 gap-4 xl:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="rounded-2xl border border-slate-200/80 bg-white p-5">
            <div className="skeleton h-3 w-16" />
            <div className="skeleton mt-4 h-7 w-24" />
            <div className="skeleton mt-2 h-3 w-20" />
          </div>
        ))}
      </div>
      <div className="rounded-2xl border border-slate-200/80 bg-white p-6">
        <div className="skeleton h-4 w-40" />
        <div className="skeleton mt-5 h-24 w-full rounded-2xl" />
        <div className="mt-4 flex gap-2">
          <div className="skeleton h-6 w-24 rounded-full" />
          <div className="skeleton h-6 w-28 rounded-full" />
        </div>
      </div>
      <div className="rounded-2xl border border-slate-200/80 bg-white p-6">
        <div className="flex items-center justify-between">
          <div className="skeleton h-4 w-36" />
          <div className="skeleton h-8 w-48 rounded-xl" />
        </div>
        <div className="skeleton mt-5 h-[380px] w-full rounded-2xl" />
      </div>
      <div className="rounded-2xl border border-slate-200/80 bg-white p-6">
        <div className="skeleton h-4 w-44" />
        <div className="mt-5 space-y-2.5">
          {Array.from({ length: 6 }).map((_, i) => (
            <div key={i} className="skeleton h-9 w-full" />
          ))}
        </div>
      </div>
    </div>
  )
}
