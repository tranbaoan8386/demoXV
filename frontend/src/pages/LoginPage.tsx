import { useState } from 'react'
import { useNavigate } from 'react-router-dom'

import { useAuth } from '../hooks/useAuth'
import { Button } from '../components/common/Button'
import { AlertBanner } from '../components/common/AlertBanner'
import { getApiErrorMessage } from '../utils/api'

export function LoginPage() {
  const navigate = useNavigate()
  const { login } = useAuth()
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [fieldErrors, setFieldErrors] = useState<Record<string, string>>({})
  const [formData, setFormData] = useState({ email: '', password: '' })

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value,
    })
    setFieldErrors((current) => ({ ...current, [e.target.name]: '' }))
  }

  const validate = () => {
    const nextErrors: Record<string, string> = {}

    if (!formData.email.trim()) {
      nextErrors.email = 'Email không được để trống.'
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(formData.email)) {
      nextErrors.email = 'Email không hợp lệ.'
    }

    if (!formData.password) {
      nextErrors.password = 'Mật khẩu không được để trống.'
    }

    setFieldErrors(nextErrors)
    return Object.keys(nextErrors).length === 0
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')

    if (!validate()) {
      return
    }

    setLoading(true)

    try {
      await login(formData)
      navigate('/dashboard', { replace: true })
    } catch (err) {
      setError(getApiErrorMessage(err))
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="flex min-h-screen items-center justify-center bg-slate-100 px-4 py-8">
      <div className="w-full max-w-xl rounded-[32px] border border-slate-200 bg-white/95 p-8 shadow-glow backdrop-blur-xl">
        <div className="mb-10 flex flex-col items-center gap-3 text-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-3xl bg-brand-500 text-2xl font-semibold text-white shadow-lg shadow-brand-500/25">
            DX
          </div>
          <div>
            <p className="text-sm uppercase tracking-[0.35em] text-brand-600">DemoXV</p>
            <h1 className="mt-2 text-3xl font-semibold text-slate-900">Đăng nhập vào bảng điều khiển</h1>
            <p className="mt-2 text-sm text-slate-500">Quản lý tài liệu và audit AI trong một nền tảng SaaS chuyên nghiệp.</p>
          </div>
        </div>

        {error && <AlertBanner type="error" message={error} className="mb-6" />}

        <form onSubmit={handleSubmit} className="space-y-5">
          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700">Email</label>
            <div className="relative rounded-3xl border bg-slate-50 px-4 py-2 transition focus-within:border-brand-500 focus-within:ring-2 focus-within:ring-brand-200">
              <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="h-5 w-5">
                  <path d="M2.25 6.75A2.25 2.25 0 014.5 4.5h15a2.25 2.25 0 012.25 2.25v10.5A2.25 2.25 0 0119.5 19.5h-15A2.25 2.25 0 012.25 17.25V6.75zM4.5 6.75v.638l7.5 4.61 7.5-4.61V6.75h-15zm7.5 5.39L4.736 7.618 4.5 7.751v9.499h15V7.75l-.236-.133L12 12.14z" />
                </svg>
              </span>
              <input
                type="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="hello@demoxv.com"
                className="w-full border-none bg-transparent pl-12 text-slate-900 outline-none placeholder:text-slate-400"
                disabled={loading}
              />
            </div>
            {fieldErrors.email && <p className="text-sm text-rose-600">{fieldErrors.email}</p>}
          </div>

          <div className="space-y-2">
            <label className="text-sm font-medium text-slate-700">Mật khẩu</label>
            <div className="relative rounded-3xl border bg-slate-50 px-4 py-2 transition focus-within:border-brand-500 focus-within:ring-2 focus-within:ring-brand-200">
              <span className="pointer-events-none absolute left-4 top-1/2 -translate-y-1/2 text-slate-400">
                <svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor" className="h-5 w-5">
                  <path d="M12 1.5A4.5 4.5 0 007.5 6v3H6A3 3 0 003 12v7.5A3 3 0 006 22.5h12a3 3 0 003-3V12a3 3 0 00-3-3h-1.5V6A4.5 4.5 0 0012 1.5zM9 6a3 3 0 116 0v3H9V6zm-3 6h12v7.5a.75.75 0 01-.75.75H6.75a.75.75 0 01-.75-.75V12z" />
                </svg>
              </span>
              <input
                type="password"
                name="password"
                value={formData.password}
                onChange={handleChange}
                placeholder="••••••••"
                className="w-full border-none bg-transparent pl-12 text-slate-900 outline-none placeholder:text-slate-400"
                disabled={loading}
              />
            </div>
            {fieldErrors.password && <p className="text-sm text-rose-600">{fieldErrors.password}</p>}
          </div>

          <Button type="submit" loading={loading} disabled={loading} className="w-full">
            Đăng nhập
          </Button>
        </form>

        <p className="mt-6 text-center text-sm text-slate-500">
          Chưa có tài khoản?{' '}
          <button onClick={() => navigate('/register')} className="font-semibold text-brand-600 hover:text-brand-700">
            Đăng ký ngay
          </button>
        </p>
      </div>
    </div>
  )
}
