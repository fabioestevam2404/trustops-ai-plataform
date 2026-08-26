import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api/client'
import { CertificationBadge } from '../components/CertificationBadge'
import { TrustScoreChart } from '../components/TrustScoreChart'

export function ProjectDetailPage() {
  const { projectId } = useParams<{ projectId: string }>()
  const queryClient = useQueryClient()
  const [version, setVersion] = useState('')

  const projectQuery = useQuery({
    queryKey: ['project', projectId],
    queryFn: () => api.getProject(projectId!),
    enabled: !!projectId,
  })

  const assessmentsQuery = useQuery({
    queryKey: ['assessments', projectId],
    queryFn: () => api.listAssessments(projectId!),
    enabled: !!projectId,
  })

  const runAssessment = useMutation({
    mutationFn: () => api.createAssessment(projectId!, version || undefined),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['assessments', projectId] })
    },
  })

  if (projectQuery.isLoading) return <p className="p-6 text-sm text-slate-500">Carregando…</p>
  if (projectQuery.isError || !projectQuery.data)
    return <p className="p-6 text-sm text-red-600">Projeto não encontrado.</p>

  const project = projectQuery.data
  const history = [...(assessmentsQuery.data ?? [])].reverse()

  return (
    <div className="mx-auto max-w-4xl space-y-8 p-6">
      <div>
        <Link to="/" className="text-sm text-slate-500 hover:underline">
          ← Projetos
        </Link>
        <h1 className="mt-1 text-2xl font-bold text-slate-900">{project.name}</h1>
        <p className="text-sm text-slate-500">{project.repository_url}</p>
      </div>

      <section className="rounded-lg border border-slate-200 bg-white p-4">
        <h2 className="mb-3 text-sm font-semibold text-slate-700">Rodar nova avaliação</h2>
        <form
          onSubmit={(event) => {
            event.preventDefault()
            runAssessment.mutate()
          }}
          className="flex flex-wrap items-end gap-3"
        >
          <div className="flex flex-col gap-1">
            <label className="text-xs font-medium text-slate-600" htmlFor="version">
              Versão / ref (opcional)
            </label>
            <input
              id="version"
              className="rounded border border-slate-300 px-2 py-1 text-sm"
              value={version}
              onChange={(event) => setVersion(event.target.value)}
              placeholder="main"
            />
          </div>
          <button
            type="submit"
            disabled={runAssessment.isPending}
            className="rounded bg-slate-900 px-4 py-1.5 text-sm font-medium text-white disabled:opacity-50"
          >
            {runAssessment.isPending ? 'Rodando avaliação…' : 'Rodar avaliação'}
          </button>
        </form>
        {runAssessment.isPending && (
          <p className="mt-2 text-xs text-slate-500">
            A avaliação roda de forma síncrona e pode levar de alguns segundos a
            poucos minutos, dependendo do repositório.
          </p>
        )}
        {runAssessment.isError && (
          <p className="mt-2 text-xs text-red-600">Erro ao criar a avaliação.</p>
        )}
      </section>

      <section className="rounded-lg border border-slate-200 bg-white p-4">
        <h2 className="mb-3 text-sm font-semibold text-slate-700">Trust Score — histórico</h2>
        <TrustScoreChart assessments={assessmentsQuery.data ?? []} />
      </section>

      <section>
        <h2 className="mb-3 text-sm font-semibold text-slate-700">Avaliações</h2>
        <ul className="divide-y divide-slate-200 rounded-lg border border-slate-200 bg-white">
          {history.map((assessment) => (
            <li key={assessment.id}>
              <Link
                to={`/assessments/${assessment.id}`}
                className="flex items-center justify-between px-4 py-3 hover:bg-slate-50"
              >
                <div>
                  <p className="font-mono text-sm text-slate-900">{assessment.version}</p>
                  <p className="text-xs text-slate-500">
                    {new Date(assessment.created_at).toLocaleString()} · {assessment.status}
                  </p>
                </div>
                <div className="flex items-center gap-3">
                  <span className="text-sm text-slate-600">
                    trust: {assessment.trust_score ?? '—'}
                  </span>
                  <CertificationBadge level={assessment.certification_level} />
                </div>
              </Link>
            </li>
          ))}
          {history.length === 0 && (
            <li className="px-4 py-6 text-center text-sm text-slate-500">
              Nenhuma avaliação rodada ainda.
            </li>
          )}
        </ul>
      </section>
    </div>
  )
}
