import { Navigate } from 'react-router-dom'

import { useAuth } from '../../hooks/useAuth'

interface PublicRouteProps {
  element: React.ReactNode
}

export function PublicRoute({ element }: PublicRouteProps) {
  const { isAuthenticated, isLoading } = useAuth()

  if (isLoading) {
    return <div className="flex items-center justify-center h-screen">Loading...</div>
  }

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />
  }

  return element
}
