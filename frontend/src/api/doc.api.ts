import apiClient from './client'
import type { AxiosProgressEvent } from 'axios'

export interface DocumentItem {
  document_id: string
  filename: string
  content: string
  storage_path: string
  created_by?: string
  created_at?: string
}

export interface UploadDocumentResponse {
  success: boolean
  data: DocumentItem
}

export interface DocumentDetailResponse {
  success: boolean
  data: DocumentItem
}

export interface DocumentListResponse {
  success: boolean
  data: {
    documents: DocumentItem[]
  }
}

export const docApi = {
  uploadDocument(file: File, onUploadProgress?: (progressEvent: AxiosProgressEvent) => void) {
    const formData = new FormData()
    formData.append('file', file)

    return apiClient.post<UploadDocumentResponse>('/api/v1/docs/extract', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    })
  },

  getDocuments() {
    return apiClient.get<DocumentListResponse>('/api/v1/docs')
  },

  listDocuments() {
    return this.getDocuments()
  },

  getDocument(documentId: string) {
    return apiClient.get<DocumentDetailResponse>(`/api/v1/docs/${documentId}`)
  },
}
