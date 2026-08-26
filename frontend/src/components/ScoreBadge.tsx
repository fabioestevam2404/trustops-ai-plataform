function colorFor(score: number | null): string {
  if (score === null) return 'text-slate-400'
  if (score >= 85) return 'text-emerald-600'
  if (score >= 75) return 'text-blue-600'
  if (score >= 50) return 'text-amber-600'
  return 'text-red-600'
}

export function ScoreBadge({ label, score }: { label: string; score: number | null }) {
  return (
    <div className="flex flex-col items-center rounded-lg border border-slate-200 bg-white px-4 py-3">
      <span className={`text-2xl font-bold ${colorFor(score)}`}>{score ?? '—'}</span>
      <span className="text-xs uppercase tracking-wide text-slate-500">{label}</span>
    </div>
  )
}
