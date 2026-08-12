import { useNavigate } from 'react-router-dom'

import { Button } from '../components/common/Button'

export function NotFoundPage() {
  const navigate = useNavigate()

  return (
    <div className="flex items-center justify-center min-h-screen bg-gray-100">
      <div className="text-center">
        <h1 className="text-6xl font-bold text-gray-800">404</h1>
        <p className="text-xl text-gray-600 mt-4">Page Not Found</p>
        <Button
          onClick={() => navigate('/', { replace: true })}
          className="mt-6"
        >
          Go Home
        </Button>
      </div>
    </div>
  )
}
