import apiClient from './client'
import type { AuditDetail } from '../types'

export interface AuditReport {
  id?: string
  document_id: string
  status?: string
  risk_level?: string
  summary?: string
  recommendations?: string[]
  created_at?: string
  updated_at?: string
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

export const auditApi = {
  createAudit(payload: AuditContractRequest) {
    return apiClient.post<AuditReport>('/api/v1/audit/contract', payload)
  },

  getAuditHistory() {
    return apiClient.get<AuditHistoryResponse>('/api/v1/audit/history')
  },

  async getAuditByDocument(documentId: string) {
    const response = await apiClient.get<AuditDetail>(`/api/v1/audit/contract/${documentId}`)
    return response.data
  },
}
