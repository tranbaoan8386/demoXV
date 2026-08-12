import { Navigate } from 'react-router-dom'

import { useAuth } from '../../hooks/useAuth'

interface ProtectedRouteProps {
  element: React.ReactNode
}

export function ProtectedRoute({ element }: ProtectedRouteProps) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return <div className="flex items-center justify-center h-screen">Loading...</div>
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />
  }

  return element
}
