import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { fireEvent, render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import { api } from '../api/client'
import type { Project } from '../api/types'
import { ProjectListPage } from './ProjectListPage'

vi.mock('../api/client', () => ({
  api: {
    listProjects: vi.fn(),
    createProject: vi.fn(),
  },
}))

function renderWithProviders() {
  const queryClient = new QueryClient({
    defaultOptions: { queries: { retry: false } },
  })
  return render(
    <QueryClientProvider client={queryClient}>
      <MemoryRouter>
        <ProjectListPage />
      </MemoryRouter>
    </QueryClientProvider>,
  )
}

describe('ProjectListPage', () => {
  it('renders the projects returned by the API', async () => {
    vi.mocked(api.listProjects).mockResolvedValue([
      {
        id: 'p1',
        name: 'example-api',
        repository_url: 'https://github.com/org/example-api',
        created_at: '2026-01-01T00:00:00Z',
        latest_trust_score: null,
        latest_certification_level: null,
      },
    ])

    renderWithProviders()

    await waitFor(() => expect(screen.getByText('example-api')).toBeInTheDocument())
    expect(screen.getByText('https://github.com/org/example-api')).toBeInTheDocument()
  })

  it('shows an empty state when there are no projects', async () => {
    vi.mocked(api.listProjects).mockResolvedValue([])

    renderWithProviders()

    await waitFor(() =>
      expect(screen.getByText('Nenhum projeto cadastrado ainda.')).toBeInTheDocument(),
    )
  })

  it('sorts projects by score, keeping unassessed projects last', async () => {
    const projects: Project[] = [
      {
        id: 'p-low',
        name: 'low-score',
        repository_url: 'https://github.com/org/low',
        created_at: '2026-01-01T00:00:00Z',
        latest_trust_score: 30,
        latest_certification_level: 'FOUNDATION',
      },
      {
        id: 'p-high',
        name: 'high-score',
        repository_url: 'https://github.com/org/high',
        created_at: '2026-01-02T00:00:00Z',
        latest_trust_score: 90,
        latest_certification_level: 'HIGH_TRUST',
      },
      {
        id: 'p-none',
        name: 'never-assessed',
        repository_url: 'https://github.com/org/none',
        created_at: '2026-01-03T00:00:00Z',
        latest_trust_score: null,
        latest_certification_level: null,
      },
    ]
    vi.mocked(api.listProjects).mockResolvedValue(projects)

    renderWithProviders()
    await waitFor(() => expect(screen.getByText('low-score')).toBeInTheDocument())

    const getOrder = () => screen.getAllByRole('link').map((link) => link.textContent)

    fireEvent.change(screen.getByLabelText('Ordenar por'), {
      target: { value: 'score-desc' },
    })
    const descOrder = getOrder()
    expect(descOrder[0]).toContain('high-score')
    expect(descOrder[1]).toContain('low-score')
    expect(descOrder[2]).toContain('never-assessed')

    fireEvent.change(screen.getByLabelText('Ordenar por'), {
      target: { value: 'score-asc' },
    })
    const ascOrder = getOrder()
    expect(ascOrder[0]).toContain('low-score')
    expect(ascOrder[1]).toContain('high-score')
    expect(ascOrder[2]).toContain('never-assessed')
  })
})
