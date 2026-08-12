import { formatRiskLabel } from '../../utils/formatters'

interface RiskBadgeProps {
  riskLevel: string
}

export function RiskBadge({ riskLevel }: RiskBadgeProps) {
  const colors: Record<string, string> = {
    low: 'bg-green-100 text-green-800',
    medium: 'bg-yellow-100 text-yellow-800',
    high: 'bg-red-100 text-red-800',
  }

  const color = colors[riskLevel.toLowerCase()] || 'bg-gray-100 text-gray-800'

  return (
    <span className={`px-3 py-1 rounded-full text-sm font-medium ${color}`}>
      {formatRiskLabel(riskLevel)}
    </span>
  )
}
