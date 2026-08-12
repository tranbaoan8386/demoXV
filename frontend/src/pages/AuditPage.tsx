import { useEffect, useState } from 'react'
import { useParams } from 'react-router-dom'

import { auditApi } from '../api/audit.api'
import { Navbar } from '../components/common/Navbar'
import { Sidebar } from '../components/common/Sidebar'
import { Loading } from '../components/common/Loading'
import { AuditReport } from '../components/audit/AuditReport'
import { AuditDetail } from '../components/audit/AuditDetail'
import type { AuditReport as AuditReportType, AuditDetail as AuditDetailType } from '../types'

export function AuditPage() {
  const { documentId } = useParams<{ documentId: string }>()
  const [audits, setAudits] = useState<AuditReportType[]>([])
  const [auditDetail, setAuditDetail] = useState<AuditDetailType | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    if (documentId) {
      loadAuditForDocument(documentId)
    } else {
      loadAudits()
    }
  }, [documentId])

  const loadAudits = async () => {
    try {
      setLoading(true)
      setError('')
      const response = await auditApi.getAuditHistory()
      const items = response.data.data || []
      items.forEach((item) => {
        console.log('[Audit Item Data]:', item)
      })
      setAudits(items)
      setAuditDetail(null)
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load audits')
      setAudits([])
      setAuditDetail(null)
    } finally {
      setLoading(false)
    }
  }

  const loadAuditForDocument = async (id: string) => {
    try {
      setLoading(true)
      setError('')
      const detail = await auditApi.getAuditByDocument(id)
      console.log('[Audit Data Response]:', detail)
      setAuditDetail(detail)
      setAudits([])
    } catch (err) {
      // If 404, no audit exists yet; otherwise surface error
      // eslint-disable-next-line @typescript-eslint/no-explicit-any
      const e: any = err
      if (e && e.response && e.response.status === 404) {
        setAuditDetail(null)
      } else {
        setError(err instanceof Error ? err.message : 'Failed to audit document')
        setAuditDetail(null)
      }
    } finally {
      setLoading(false)
    }
  }

  // AuditPage is read-only: audits are triggered on upload. No manual POST handlers here.

  if (loading) {
    return <Loading message={documentId ? 'Đang tải báo cáo Audit...' : 'Đang phân tích tài liệu bằng AI...'} />
  }

  return (
    <div className="flex h-screen">
      <Sidebar />
      <div className="flex-1 flex flex-col">
        <Navbar />
        <main className="flex-1 overflow-auto bg-gray-50 p-8">
          <div className="max-w-6xl mx-auto">
            <h1 className="text-3xl font-bold mb-8">
              {documentId ? 'Audit tài liệu' : 'Audit History'}
            </h1>

            {error && (
              <div className="bg-red-100 text-red-800 p-4 rounded mb-4">
                {error}
              </div>
            )}

            {documentId ? (
              auditDetail ? (
                <AuditDetail detail={auditDetail} />
              ) : (
                <div>
                  <p className="text-gray-600 mb-4">Báo cáo Audit đang được xử lý hoặc không tồn tại.</p>
                </div>
              )
            ) : audits.length === 0 ? (
              <p className="text-gray-600">No audit reports available</p>
            ) : (
              <div className="space-y-4">
                {audits.map((audit) => (
                  <AuditReport key={audit.id} report={audit} />
                ))}
              </div>
            )}
          </div>
        </main>
      </div>
    </div>
  )
}
