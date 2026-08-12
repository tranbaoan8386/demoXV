import { createContext, useCallback, useContext, useState, type ReactNode } from 'react'

type ToastType = 'success' | 'error' | 'info'

interface ToastOptions {
  message: string
  type?: ToastType
  durationMs?: number
}

interface ToastContextValue {
  showToast: (opts: ToastOptions) => void
}

const ToastContext = createContext<ToastContextValue | undefined>(undefined)

export function useToast() {
  const ctx = useContext(ToastContext)
  if (!ctx) throw new Error('useToast must be used within ToastProvider')
  return ctx
}

export function ToastProvider({ children }: { children: ReactNode }) {
  const [toast, setToast] = useState<ToastOptions | null>(null)

  const showToast = useCallback(({ message, type = 'info', durationMs = 3000 }: ToastOptions) => {
    setToast({ message, type, durationMs })

    window.setTimeout(() => {
      setToast(null)
    }, durationMs)
  }, [])

  return (
    <ToastContext.Provider value={{ showToast }}>
      {children}
      {toast ? (
        <div className="fixed right-6 top-6 z-50">
          <div className={`max-w-sm rounded-lg px-4 py-3 shadow-lg ${toast.type === 'success' ? 'bg-emerald-600 text-white' : toast.type === 'error' ? 'bg-rose-600 text-white' : 'bg-slate-800 text-white'}`}>
            {toast.message}
          </div>
        </div>
      ) : null}
    </ToastContext.Provider>
  )
}

export default ToastContext
