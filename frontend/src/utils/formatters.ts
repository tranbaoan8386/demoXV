export function formatDate(value?: string | Date | null): string {
  if (!value) {
    return '-'
  }

  const date = typeof value === 'string' ? new Date(value) : value

  if (Number.isNaN(date.getTime())) {
    return '-'
  }

  return new Intl.DateTimeFormat('vi-VN', {
    dateStyle: 'medium',
    timeStyle: 'short',
  }).format(date)
}

export function formatRiskLabel(riskLevel?: string | null): string {
  if (!riskLevel) {
    return 'Unknown'
  }

  return riskLevel
    .replace(/_/g, ' ')
    .replace(/\b\w/g, (character) => character.toUpperCase())
}

export function truncateText(value: string, maxLength = 120): string {
  if (value.length <= maxLength) {
    return value
  }

  return `${value.slice(0, maxLength).trimEnd()}...`
}
