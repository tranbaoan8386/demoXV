import { Link, useLocation } from 'react-router-dom'

import { useAuth } from '../../hooks/useAuth'

export function Sidebar() {
  const location = useLocation()
  const { user } = useAuth()
  const isActive = (path: string) => location.pathname === path

  return (
    <aside className="hidden w-80 shrink-0 border-r border-slate-200 bg-slate-950 text-slate-100 lg:flex lg:flex-col">
      <div className="flex flex-col justify-between h-full px-6 py-8">
        <div>
          <div className="mb-8 flex items-center gap-3">
            <div className="flex h-12 w-12 items-center justify-center rounded-3xl bg-brand-500 text-white shadow-glow">
              DX
            </div>
            <div>
              <p className="text-lg font-semibold">DemoXV</p>
              <p className="text-sm text-slate-400">Audit Platform</p>
            </div>
          </div>

          <nav className="space-y-2">
            {[
              { label: 'Dashboard', to: '/dashboard' },
            ].map((item) => (
              <Link
                key={item.to}
                to={item.to}
                className={`block rounded-3xl px-4 py-3 text-sm font-medium transition ${
                  isActive(item.to)
                    ? 'bg-brand-600 text-white shadow-lg shadow-brand-500/20'
                    : 'text-slate-300 hover:bg-slate-800 hover:text-white'
                }`}
              >
                {item.label}
              </Link>
            ))}
          </nav>
        </div>

        <div className="mt-8 rounded-3xl border border-white/10 bg-white/5 p-4 backdrop-blur-sm">
          <p className="text-xs uppercase tracking-[0.24em] text-slate-500">Account</p>
          <div className="mt-4 flex items-center gap-3">
            <div className="flex h-11 w-11 items-center justify-center rounded-2xl bg-brand-100 text-brand-700">
              {user?.email?.charAt(0).toUpperCase() ?? 'D'}
            </div>
            <div>
              <p className="font-semibold text-white">{user?.full_name ?? user?.email ?? 'DemoXV User'}</p>
              <p className="text-sm text-slate-400">Active account</p>
            </div>
          </div>
        </div>
      </div>
    </aside>
  )
}
