import { useCallback, useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { docApi } from '../api/doc.api'
import { FileUploader } from '../components/docs/FileUploader'
import { Navbar } from '../components/common/Navbar'
import { Sidebar } from '../components/common/Sidebar'
import { Loading } from '../components/common/Loading'
import { formatDate } from '../utils/formatters'
import type { DocumentItem } from '../types'
import { useAuth } from '../hooks/useAuth'

function formatFileSize(content?: string): string {
  if (!content) {
    return '0 KB'
  }

  const bytes = new TextEncoder().encode(content).length
  if (bytes < 1024) {
    return `${bytes} B`
  }

  const kb = bytes / 1024
  if (kb < 1024) {
    return `${kb.toFixed(1)} KB`
  }

  return `${(kb / 1024).toFixed(1)} MB`
}

export function DashboardPage() {
  const navigate = useNavigate()
  const { user } = useAuth()
  const [documents, setDocuments] = useState<DocumentItem[]>([])
  const [loading, setLoading] = useState(true)

  const loadDocuments = useCallback(async () => {
    try {
      setLoading(true)
      const response = await docApi.getDocuments()
      const nextDocuments = response.data?.data?.documents ?? []
      setDocuments(nextDocuments)
    } catch {
      setDocuments([])
    } finally {
      setLoading(false)
    }
  }, [])

  useEffect(() => {
    void loadDocuments()
  }, [loadDocuments])

  const userDisplayName = user?.full_name ?? user?.email ?? 'Người dùng'

  const handleOpenAudit = (documentId: string) => {
    if (!documentId) {
      return
    }

    navigate(`/audit/${documentId}`)
  }

  if (loading) {
    return <Loading />
  }

  return (
    <div className="min-h-screen bg-slate-100">
      <div className="lg:flex lg:min-h-screen">
        <Sidebar />
        <div className="flex-1">
          <Navbar />
          <main className="mx-auto max-w-7xl px-4 py-8 sm:px-6 lg:px-8">
            <div className="mb-6 rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
              <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.28em] text-brand-600">Dashboard</p>
                  <h1 className="mt-2 text-3xl font-semibold text-slate-900">Xin chào, {userDisplayName}</h1>
                  <p className="mt-2 text-sm text-slate-500">Theo dõi và xem lại các tài liệu đã tải lên trên hệ thống.</p>
                </div>
              </div>
            </div>

            <section className="mb-6 rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
              <div className="mb-5">
                <p className="text-xs font-semibold uppercase tracking-[0.28em] text-brand-600">Upload</p>
                <h2 className="mt-2 text-xl font-semibold text-slate-900">Tải lên tài liệu mới</h2>
              </div>
              <FileUploader onUploadSuccess={loadDocuments} />
            </section>

            <section className="rounded-[28px] border border-slate-200 bg-white p-6 shadow-sm">
              <div className="mb-4 flex items-center justify-between gap-3">
                <div>
                  <p className="text-xs font-semibold uppercase tracking-[0.28em] text-brand-600">Documents</p>
                  <h2 className="mt-2 text-xl font-semibold text-slate-900">Danh sách tài liệu</h2>
                </div>
                <span className="rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-sm font-medium text-slate-700">
                  {documents.length} tài liệu
                </span>
              </div>

              {documents.length === 0 ? (
                <div className="rounded-[20px] border border-dashed border-slate-300 bg-slate-50 p-8 text-center text-sm text-slate-500">
                  Chưa có tài liệu nào được tải lên.
                </div>
              ) : (
                <div className="overflow-hidden rounded-[20px] border border-slate-200">
                  <div className="overflow-x-auto">
                    <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
                      <thead className="bg-slate-50 text-slate-600">
                        <tr>
                          <th className="px-5 py-4 font-semibold">Tài liệu</th>
                          <th className="px-5 py-4 font-semibold">Dung lượng</th>
                          <th className="px-5 py-4 font-semibold">Ngày tải lên</th>
                          <th className="px-5 py-4 font-semibold">Trạng thái</th>
                          <th className="px-5 py-4 font-semibold text-right">Hành động</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-200 bg-white">
                        {documents.map((document) => {
                          const isAudited = Boolean(document.content && document.content.trim().length > 0)

                          return (
                            <tr key={document.document_id} className="transition hover:bg-slate-50">
                              <td className="px-5 py-4">
                                <button
                                  type="button"
                                  onClick={() => handleOpenAudit(document.document_id)}
                                  className="flex items-center gap-3 text-left"
                                >
                                  <div className="flex h-10 w-10 items-center justify-center rounded-xl bg-brand-50 text-brand-600">
                                    <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="h-5 w-5">
                                      <path d="M7 2.75A2.75 2.75 0 004.25 5.5v13A2.75 2.75 0 007 21.25h10A2.75 2.75 0 0019.75 18.5V7.07a2.75 2.75 0 00-.8-1.94l-2.33-2.33A2.75 2.75 0 0014.93 2.25H7zm8.7 1.88l2.67 2.67h-2.17a.5.5 0 01-.5-.5V4.63zM7 4.25h6.75v3.25a2.25 2.25 0 002.25 2.25h3.25v8.75a1.25 1.25 0 01-1.25 1.25H7a1.25 1.25 0 01-1.25-1.25V5.5A1.25 1.25 0 017 4.25z" />
                                    </svg>
                                  </div>
                                  <div>
                                    <p className="font-medium text-slate-900">{document.filename}</p>
                                    <p className="mt-1 text-xs text-slate-500">{document.storage_path ?? 'Storage internal'}</p>
                                  </div>
                                </button>
                              </td>
                              <td className="px-5 py-4 text-slate-600">{formatFileSize(document.content)}</td>
                              <td className="px-5 py-4 text-slate-600">{formatDate(document.created_at)}</td>
                              <td className="px-5 py-4">
                                <span className={`inline-flex rounded-full px-2.5 py-1 text-xs font-semibold ${isAudited ? 'bg-emerald-100 text-emerald-700' : 'bg-amber-100 text-amber-700'}`}>
                                  {isAudited ? 'Đã Audit' : 'Chờ Audit'}
                                </span>
                              </td>
                              <td className="px-5 py-4 text-right">
                                <button
                                  type="button"
                                  onClick={() => handleOpenAudit(document.document_id)}
                                  className="rounded-full border border-brand-500 px-3 py-2 text-xs font-semibold text-brand-700 transition hover:bg-brand-50"
                                >
                                  Xem Audit
                                </button>
                              </td>
                            </tr>
                          )
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}
            </section>
          </main>
        </div>
      </div>
    </div>
  )
}
