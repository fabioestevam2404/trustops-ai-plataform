import { useQuery } from '@tanstack/react-query'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api/client'
import { CertificationBadge } from '../components/CertificationBadge'
import { FindingsTable } from '../components/FindingsTable'
import { ScoreBadge } from '../components/ScoreBadge'

export function AssessmentDetailPage() {
  const { assessmentId } = useParams<{ assessmentId: string }>()

  const assessmentQuery = useQuery({
    queryKey: ['assessment', assessmentId],
    queryFn: () => api.getAssessment(assessmentId!),
    enabled: !!assessmentId,
    refetchInterval: (query) =>
      query.state.data?.status === 'RUNNING' || query.state.data?.status === 'PENDING'
        ? 3000
        : false,
  })

  const findingsQuery = useQuery({
    queryKey: ['findings', assessmentId],
    queryFn: () => api.listFindings(assessmentId!),
    enabled: !!assessmentId,
  })

  if (assessmentQuery.isLoading) return <p className="p-6 text-sm text-slate-500">Carregando…</p>
  if (assessmentQuery.isError || !assessmentQuery.data)
    return <p className="p-6 text-sm text-red-600">Avaliação não encontrada.</p>

  const assessment = assessmentQuery.data
  const criticalFindings = (findingsQuery.data ?? []).filter(
    (finding) => finding.severity === 'CRITICAL' || finding.severity === 'HIGH',
  )

  return (
    <div className="mx-auto max-w-4xl space-y-8 p-6">
      <div>
        <Link to={`/projects/${assessment.project_id}`} className="text-sm text-slate-500 hover:underline">
          ← Projeto
        </Link>
        <div className="mt-1 flex items-center gap-3">
          <h1 className="font-mono text-xl font-bold text-slate-900">{assessment.version}</h1>
          <CertificationBadge level={assessment.certification_level} />
        </div>
        <p className="text-sm text-slate-500">
          {new Date(assessment.created_at).toLocaleString()} · status: {assessment.status}
        </p>
      </div>

      <section className="flex gap-4">
        <ScoreBadge label="Trust Score" score={assessment.trust_score} />
        <ScoreBadge label="Quality Score" score={assessment.quality_score} />
        <ScoreBadge label="Security Score" score={assessment.security_score} />
      </section>

      {criticalFindings.length > 0 && (
        <section className="rounded-lg border border-red-200 bg-red-50 p-4">
          <h2 className="mb-2 text-sm font-semibold text-red-800">
            Riscos críticos ({criticalFindings.length})
          </h2>
          <FindingsTable findings={criticalFindings} />
        </section>
      )}

      <section className="rounded-lg border border-slate-200 bg-white p-4">
        <h2 className="mb-3 text-sm font-semibold text-slate-700">Todos os findings</h2>
        <FindingsTable findings={findingsQuery.data ?? []} />
      </section>
    </div>
  )
}
