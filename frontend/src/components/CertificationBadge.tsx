import type { CertificationLevel } from '../api/types'

const STYLES: Record<CertificationLevel, string> = {
  BLOCKED: 'bg-red-100 text-red-800 border-red-300',
  FOUNDATION: 'bg-slate-100 text-slate-800 border-slate-300',
  TRUSTED: 'bg-blue-100 text-blue-800 border-blue-300',
  HIGH_TRUST: 'bg-emerald-100 text-emerald-800 border-emerald-300',
  ENTERPRISE_TRUST: 'bg-purple-100 text-purple-800 border-purple-300',
}

const LABELS: Record<CertificationLevel, string> = {
  BLOCKED: 'Blocked',
  FOUNDATION: 'Foundation',
  TRUSTED: 'Trusted',
  HIGH_TRUST: 'High Trust',
  ENTERPRISE_TRUST: 'Enterprise Trust',
}

export function CertificationBadge({ level }: { level: CertificationLevel | null }) {
  if (level === null) {
    return (
      <span className="inline-flex items-center rounded-full border border-slate-200 bg-slate-50 px-2.5 py-0.5 text-xs font-medium text-slate-500">
        Pending
      </span>
    )
  }
  return (
    <span
      className={`inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold ${STYLES[level]}`}
    >
      {LABELS[level]}
    </span>
  )
}
