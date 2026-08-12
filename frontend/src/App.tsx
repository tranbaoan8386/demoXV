import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'

import { ProtectedRoute } from './components/guards/ProtectedRoute'
import { PublicRoute } from './components/guards/PublicRoute'
import { LoginPage } from './pages/LoginPage'
import { RegisterPage } from './pages/RegisterPage'
import { DashboardPage } from './pages/DashboardPage'
import { AuditPage } from './pages/AuditPage'
import { NotFoundPage } from './pages/NotFoundPage'

function App() {
  return (
    <Router>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<PublicRoute element={<LoginPage />} />} />
        <Route
          path="/register"
          element={<PublicRoute element={<RegisterPage />} />}
        />

        {/* Protected routes */}
        <Route
          path="/dashboard"
          element={<ProtectedRoute element={<DashboardPage />} />}
        />
        <Route
          path="/audit"
          element={<ProtectedRoute element={<AuditPage />} />}
        />
        <Route
          path="/audit/:documentId"
          element={<ProtectedRoute element={<AuditPage />} />}
        />

        {/* Redirects & 404 */}
        <Route path="/" element={<Navigate to="/dashboard" replace />} />
        <Route path="*" element={<NotFoundPage />} />
      </Routes>
    </Router>
  )
}

export default App
