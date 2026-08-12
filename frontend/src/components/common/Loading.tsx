interface LoadingProps {
  message?: string
}

export function Loading({ message = 'Đang tải...' }: LoadingProps) {
  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-50 px-6">
      <div className="rounded-3xl bg-white/90 px-10 py-12 shadow-glow backdrop-blur-sm">
        <div className="mx-auto h-10 w-10 animate-spin rounded-full border-2 border-brand-500 border-t-transparent" />
        <p className="mt-4 text-lg font-semibold text-slate-700">{message}</p>
      </div>
    </div>
  )
}
