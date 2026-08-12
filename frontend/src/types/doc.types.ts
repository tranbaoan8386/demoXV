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
