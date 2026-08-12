import { useNavigate } from 'react-router-dom'

import { useAuth } from '../../hooks/useAuth'

export function Navbar() {
  const navigate = useNavigate()
  const { user, logout } = useAuth()

  const handleLogout = () => {
    logout()
    navigate('/login', { replace: true })
  }

  return (
    <header className="border-b border-slate-200 bg-white/90 backdrop-blur-sm">
      <div className="mx-auto flex max-w-7xl items-center justify-between gap-4 px-4 py-4 sm:px-6">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-brand-500 text-white shadow-brand-500/20">
            DX
          </div>
          <div>
            <p className="text-sm font-semibold text-slate-900">DemoXV</p>
            <p className="text-xs text-slate-500">AI Document Audit</p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          {user && (
            <div className="flex items-center gap-3 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-2">
              <div className="flex h-10 w-10 items-center justify-center rounded-full bg-brand-100 text-brand-700">
                {user.email?.charAt(0).toUpperCase()}
              </div>
              <div className="text-sm text-slate-700">
                <p className="font-semibold">{user.email}</p>
                <p className="text-xs text-slate-500">Tài khoản</p>
              </div>
            </div>
          )}
          <button
            onClick={handleLogout}
            className="rounded-2xl bg-slate-900 px-4 py-2 text-sm font-semibold text-white transition hover:bg-slate-800"
          >
            Logout
          </button>
        </div>
      </div>
    </header>
  )
}
