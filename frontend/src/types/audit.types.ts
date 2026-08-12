export interface AuditClause {
  title: string
  content: string
  risk_level: string
  risk_description?: string
  recommendation?: string
}

export interface AuditReport {
  id?: string
  document_id: string
  contract_id?: string
  contract_name?: string
  status?: string
  risk_level?: string
  overall_risk?: number | string
  summary?: string
  findings?: string[]
  recommendations?: string[]
  created_at?: string
  updated_at?: string
}

export interface AuditDetail {
  document_id: string
  file_name: string
  overall_risk_score?: number
  summary?: string
  clauses?: AuditClause[]
}

export interface AuditContractRequest {
  document_id: string
}

export interface AuditResponse {
  success: boolean
  data: AuditReport
}

export interface AuditHistoryResponse {
  success: boolean
  data: AuditReport[]
}
