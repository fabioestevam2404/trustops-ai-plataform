import type { Assessment, Finding, Project } from './types'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8001'

class ApiError extends Error {
  status: number

  constructor(status: number, message: string) {
    super(message)
    this.name = 'ApiError'
    this.status = status
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  })
  if (!response.ok) {
    const body = await response.text()
    throw new ApiError(response.status, body || response.statusText)
  }
  if (response.status === 204) {
    return undefined as T
  }
  return (await response.json()) as T
}

export const api = {
  listProjects: () => request<Project[]>('/projects'),
  getProject: (id: string) => request<Project>(`/projects/${id}`),
  createProject: (data: { name: string; repository_url: string }) =>
    request<Project>('/projects', { method: 'POST', body: JSON.stringify(data) }),

  listAssessments: (projectId: string) =>
    request<Assessment[]>(`/projects/${projectId}/assessments`),
  getAssessment: (id: string) => request<Assessment>(`/assessments/${id}`),
  createAssessment: (projectId: string, version?: string) =>
    request<Assessment>(`/projects/${projectId}/assessments`, {
      method: 'POST',
      body: JSON.stringify({ version: version || null }),
    }),

  listFindings: (assessmentId: string) =>
    request<Finding[]>(`/assessments/${assessmentId}/findings`),
}

export { ApiError }
