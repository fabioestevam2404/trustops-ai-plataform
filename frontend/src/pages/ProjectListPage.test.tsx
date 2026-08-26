import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { render, screen, waitFor } from '@testing-library/react'
import { MemoryRouter } from 'react-router-dom'
import { describe, expect, it, vi } from 'vitest'
import { api } from '../api/client'
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
})
