import {
  CartesianGrid,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts'
import type { Assessment } from '../api/types'

export function TrustScoreChart({ assessments }: { assessments: Assessment[] }) {
  const data = assessments
    .filter((assessment) => assessment.trust_score !== null)
    .map((assessment) => ({
      label: assessment.version,
      trust_score: assessment.trust_score,
      date: new Date(assessment.created_at).toLocaleDateString(),
    }))

  if (data.length === 0) {
    return (
      <p className="text-sm text-slate-500">
        Nenhuma avaliação concluída ainda para exibir o histórico.
      </p>
    )
  }

  return (
    <div className="h-64 w-full">
      <ResponsiveContainer width="100%" height="100%">
        <LineChart data={data}>
          <CartesianGrid strokeDasharray="3 3" stroke="#e2e8f0" />
          <XAxis dataKey="date" tick={{ fontSize: 12 }} />
          <YAxis domain={[0, 100]} tick={{ fontSize: 12 }} />
          <Tooltip />
          <Line type="monotone" dataKey="trust_score" stroke="#7c3aed" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}
