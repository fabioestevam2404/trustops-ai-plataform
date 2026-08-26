import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api/client'

export function ProjectListPage() {
  const queryClient = useQueryClient()
  const projectsQuery = useQuery({ queryKey: ['projects'], queryFn: api.listProjects })

  const [name, setName] = useState('')
  const [repositoryUrl, setRepositoryUrl] = useState('')

  const createProject = useMutation({
    mutationFn: () => api.createProject({ name, repository_url: repositoryUrl }),
    onSuccess: () => {
      setName('')
      setRepositoryUrl('')
      queryClient.invalidateQueries({ queryKey: ['projects'] })
    },
  })

  return (
    <div className="mx-auto max-w-4xl space-y-8 p-6">
      <header>
        <h1 className="text-2xl font-bold text-slate-900">TrustOps AI Platform</h1>
        <p className="text-sm text-slate-500">Projetos avaliados e seu nível de confiança.</p>
      </header>

      <form
        onSubmit={(event) => {
          event.preventDefault()
          if (name && repositoryUrl) createProject.mutate()
        }}
        className="flex flex-wrap items-end gap-3 rounded-lg border border-slate-200 bg-white p-4"
      >
        <div className="flex flex-col gap-1">
          <label className="text-xs font-medium text-slate-600" htmlFor="project-name">
            Nome
          </label>
          <input
            id="project-name"
            className="rounded border border-slate-300 px-2 py-1 text-sm"
            value={name}
            onChange={(event) => setName(event.target.value)}
            placeholder="example-api"
            required
          />
        </div>
        <div className="flex flex-1 flex-col gap-1">
          <label className="text-xs font-medium text-slate-600" htmlFor="project-repo">
            Repositório
          </label>
          <input
            id="project-repo"
            className="w-full rounded border border-slate-300 px-2 py-1 text-sm"
            value={repositoryUrl}
            onChange={(event) => setRepositoryUrl(event.target.value)}
            placeholder="https://github.com/org/example-api"
            required
          />
        </div>
        <button
          type="submit"
          disabled={createProject.isPending}
          className="rounded bg-slate-900 px-4 py-1.5 text-sm font-medium text-white disabled:opacity-50"
        >
          {createProject.isPending ? 'Criando…' : 'Adicionar projeto'}
        </button>
      </form>

      {projectsQuery.isLoading && <p className="text-sm text-slate-500">Carregando…</p>}
      {projectsQuery.isError && (
        <p className="text-sm text-red-600">Erro ao carregar projetos.</p>
      )}

      <ul className="divide-y divide-slate-200 rounded-lg border border-slate-200 bg-white">
        {projectsQuery.data?.map((project) => (
          <li key={project.id}>
            <Link
              to={`/projects/${project.id}`}
              className="flex items-center justify-between px-4 py-3 hover:bg-slate-50"
            >
              <div>
                <p className="font-medium text-slate-900">{project.name}</p>
                <p className="text-xs text-slate-500">{project.repository_url}</p>
              </div>
              <span className="text-sm text-slate-400">→</span>
            </Link>
          </li>
        ))}
        {projectsQuery.data?.length === 0 && (
          <li className="px-4 py-6 text-center text-sm text-slate-500">
            Nenhum projeto cadastrado ainda.
          </li>
        )}
      </ul>
    </div>
  )
}
