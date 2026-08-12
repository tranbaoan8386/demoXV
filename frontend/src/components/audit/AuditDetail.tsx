import { RiskBadge } from './RiskBadge'
import type { AuditDetail as AuditDetailType } from '../../types/audit.types'

interface AuditDetailProps {
  detail: AuditDetailType
}

function getOverallRiskLevel(score?: number) {
  if (score == null) {
    return 'unknown'
  }

  if (score >= 4.0) {
    return 'high'
  }

  if (score >= 2.0) {
    return 'medium'
  }

  return 'low'
}

export function AuditDetail({ detail }: AuditDetailProps) {
  const overallRiskLevel = getOverallRiskLevel(detail.overall_risk_score)

  return (
    <div className="bg-white rounded-lg shadow-md p-8 mb-8">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between mb-8">
        <div>
          <h2 className="text-3xl font-semibold">{detail.file_name}</h2>
          <p className="text-sm text-gray-500 mt-2">Document ID: {detail.document_id}</p>
        </div>
        <div className="flex flex-col sm:items-end gap-2">
          <span className="text-sm text-gray-600">Overall risk score</span>
          <div className="inline-flex items-center gap-3">
            <span className="rounded-full bg-brand-50 px-4 py-2 text-sm font-semibold text-brand-700">
              {detail.overall_risk_score != null ? detail.overall_risk_score.toFixed(1) : '-'}
            </span>
            <RiskBadge riskLevel={overallRiskLevel} />
          </div>
        </div>
      </div>

      <section className="mb-8">
        <h3 className="text-xl font-semibold mb-3">Tổng quan</h3>
        <p className="text-gray-700 leading-relaxed">{detail.summary ?? 'Không có tóm tắt cho báo cáo này.'}</p>
      </section>

      <section>
        <h3 className="text-xl font-semibold mb-4">Các điều khoản rủi ro</h3>
        {detail.clauses && detail.clauses.length > 0 ? (
          <div className="space-y-6">
            {detail.clauses.map((clause, index) => (
              <div key={`${clause.title}-${index}`} className="rounded-xl border border-gray-200 bg-gray-50 p-6">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <h4 className="text-lg font-semibold">{clause.title}</h4>
                    <p className="mt-1 text-sm text-gray-600">{clause.content}</p>
                  </div>
                  <RiskBadge riskLevel={clause.risk_level ?? 'unknown'} />
                </div>

                <div className="mt-4 grid gap-4 sm:grid-cols-2">
                  <div className="rounded-lg border border-gray-200 bg-white p-4">
                    <p className="text-sm font-semibold text-gray-700">Mô tả rủi ro</p>
                    <p className="mt-2 text-gray-700">{clause.risk_description ?? 'Không có mô tả rủi ro.'}</p>
                  </div>
                  <div className="rounded-lg border border-gray-200 bg-white p-4">
                    <p className="text-sm font-semibold text-gray-700">Đề xuất</p>
                    <p className="mt-2 text-gray-700">{clause.recommendation ?? 'Không có đề xuất.'}</p>
                  </div>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="text-gray-600">Không có điều khoản rủi ro nào được tìm thấy.</p>
        )}
      </section>
    </div>
  )
}
