import type { Finding, Severity } from '../api/types'

const SEVERITY_ORDER: Severity[] = ['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFO']

const SEVERITY_STYLES: Record<Severity, string> = {
  CRITICAL: 'bg-red-100 text-red-800',
  HIGH: 'bg-orange-100 text-orange-800',
  MEDIUM: 'bg-amber-100 text-amber-800',
  LOW: 'bg-blue-100 text-blue-800',
  INFO: 'bg-slate-100 text-slate-600',
}

export function FindingsTable({ findings }: { findings: Finding[] }) {
  const sorted = [...findings].sort(
    (a, b) => SEVERITY_ORDER.indexOf(a.severity) - SEVERITY_ORDER.indexOf(b.severity),
  )

  if (sorted.length === 0) {
    return <p className="text-sm text-slate-500">Nenhum finding registrado.</p>
  }

  return (
    <table className="w-full border-collapse text-sm">
      <thead>
        <tr className="border-b border-slate-200 text-left text-xs uppercase text-slate-500">
          <th className="py-2 pr-4">Severidade</th>
          <th className="py-2 pr-4">Ferramenta</th>
          <th className="py-2 pr-4">Categoria</th>
          <th className="py-2">Descrição</th>
        </tr>
      </thead>
      <tbody>
        {sorted.map((finding) => (
          <tr key={finding.id} className="border-b border-slate-100 align-top">
            <td className="py-2 pr-4">
              <span
                className={`inline-flex rounded px-2 py-0.5 text-xs font-semibold ${SEVERITY_STYLES[finding.severity]}`}
              >
                {finding.severity}
              </span>
            </td>
            <td className="py-2 pr-4 font-mono text-xs text-slate-600">{finding.tool}</td>
            <td className="py-2 pr-4 text-slate-600">{finding.category}</td>
            <td className="py-2 text-slate-800">{finding.description}</td>
          </tr>
        ))}
      </tbody>
    </table>
  )
}
