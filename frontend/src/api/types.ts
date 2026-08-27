export type AssessmentStatus = 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED'

export type CertificationLevel =
  | 'BLOCKED'
  | 'FOUNDATION'
  | 'TRUSTED'
  | 'HIGH_TRUST'
  | 'ENTERPRISE_TRUST'

export interface Project {
  id: string
  name: string
  repository_url: string
  created_at: string
  latest_trust_score: number | null
  latest_certification_level: CertificationLevel | null
}

export interface Assessment {
  id: string
  project_id: string
  version: string
  status: AssessmentStatus
  quality_score: number | null
  security_score: number | null
  trust_score: number | null
  certification_level: CertificationLevel | null
  created_at: string
}

export type Severity = 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW' | 'INFO'

export interface Finding {
  id: string
  assessment_id: string
  tool: string
  severity: Severity
  category: string
  description: string
}
