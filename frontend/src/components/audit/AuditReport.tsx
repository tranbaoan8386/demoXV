import { useMemo } from 'react'
import { useNavigate } from 'react-router-dom'
import { formatDate } from '../../utils/formatters'
import type { AuditReport } from '../../types'
import { RiskBadge } from './RiskBadge'

interface AuditReportProps {
  report: AuditReport
}

export function AuditReport({ report }: AuditReportProps) {
  const navigate = useNavigate()

  const documentId = useMemo(
    () => report.document_id ?? report.contract_id ?? report.id,
    [report.document_id, report.contract_id, report.id],
  )

  const riskLevel = useMemo(
    () => String(report.risk_level ?? report.overall_risk ?? report.status ?? 'unknown'),
    [report.risk_level, report.overall_risk, report.status],
  )

  const handleNavigate = () => {
    if (!documentId) return
    navigate(`/audit/${documentId}`)
  }

  return (
    <div className="bg-white rounded-lg shadow-md p-6 mb-4">
      <div className="flex justify-between items-start mb-4">
        <div>
          <h3 className="text-lg font-semibold">
            {report.contract_name ?? 'Audit Report'}
          </h3>
          <p className="text-sm text-gray-600">
            ID: {documentId ?? report.id ?? 'Unknown'}
          </p>
        </div>
        <RiskBadge riskLevel={riskLevel} />
      </div>

      <div className="grid grid-cols-2 gap-4 mb-4">
        <div>
          <label className="text-sm text-gray-600">Created</label>
          <p>{formatDate(report.created_at)}</p>
        </div>
        <div>
          <label className="text-sm text-gray-600">Updated</label>
          <p>{formatDate(report.updated_at)}</p>
        </div>
      </div>

      {report.findings && report.findings.length > 0 && (
        <div>
          <h4 className="font-semibold mb-2">Findings</h4>
          <ul className="space-y-2">
            {report.findings.map((finding, idx) => (
              <li key={idx} className="text-sm text-gray-700 list-disc ml-5">
                {finding}
              </li>
            ))}
          </ul>
        </div>
      )}

      {documentId && (
        <div className="mt-6 flex justify-end">
          <button
            type="button"
            onClick={handleNavigate}
            className="inline-flex items-center rounded-md bg-brand-600 px-4 py-2 text-sm font-semibold text-white hover:bg-brand-700 focus:outline-none focus:ring-2 focus:ring-brand-500"
          >
            Xem chi tiết
          </button>
        </div>
      )}
    </div>
  )
}
