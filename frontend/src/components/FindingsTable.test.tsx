import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import type { Finding } from '../api/types'
import { FindingsTable } from './FindingsTable'

const finding = (severity: Finding['severity'], id: string): Finding => ({
  id,
  assessment_id: 'a1',
  tool: 'test-tool',
  severity,
  category: 'security',
  description: `${severity} finding`,
})

describe('FindingsTable', () => {
  it('shows a message when there are no findings', () => {
    render(<FindingsTable findings={[]} />)
    expect(screen.getByText('Nenhum finding registrado.')).toBeInTheDocument()
  })

  it('sorts findings by severity, most severe first', () => {
    render(
      <FindingsTable
        findings={[finding('LOW', '1'), finding('CRITICAL', '2'), finding('MEDIUM', '3')]}
      />,
    )
    const rows = screen.getAllByRole('row').slice(1) // skip header row
    expect(rows[0]).toHaveTextContent('CRITICAL')
    expect(rows[1]).toHaveTextContent('MEDIUM')
    expect(rows[2]).toHaveTextContent('LOW')
  })
})
