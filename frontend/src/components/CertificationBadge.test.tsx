import { render, screen } from '@testing-library/react'
import { describe, expect, it } from 'vitest'
import { CertificationBadge } from './CertificationBadge'

describe('CertificationBadge', () => {
  it('renders Blocked with the red style for BLOCKED', () => {
    render(<CertificationBadge level="BLOCKED" />)
    const badge = screen.getByText('Blocked')
    expect(badge).toBeInTheDocument()
    expect(badge.className).toContain('bg-red-100')
  })

  it('renders Enterprise Trust for ENTERPRISE_TRUST', () => {
    render(<CertificationBadge level="ENTERPRISE_TRUST" />)
    expect(screen.getByText('Enterprise Trust')).toBeInTheDocument()
  })

  it('renders Pending when the level is null', () => {
    render(<CertificationBadge level={null} />)
    expect(screen.getByText('Pending')).toBeInTheDocument()
  })
})
