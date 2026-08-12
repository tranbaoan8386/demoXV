interface AlertBannerProps {
  title?: string
  message: string
  type?: 'info' | 'success' | 'error'
  className?: string
}

const variantStyles = {
  info: 'border-indigo-200 bg-indigo-50 text-indigo-700',
  success: 'border-emerald-200 bg-emerald-50 text-emerald-700',
  error: 'border-rose-200 bg-rose-50 text-rose-700',
}

export function AlertBanner({
  title,
  message,
  type = 'info',
  className = '',
}: AlertBannerProps) {
  return (
    <div
      className={`rounded-3xl border px-4 py-3 shadow-sm ${variantStyles[type]} ${className}`}
    >
      {title ? (
        <div className="mb-1 text-sm font-semibold">{title}</div>
      ) : null}
      <p className="text-sm leading-6">{message}</p>
    </div>
  )
}
