import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useApp } from '@/context/AppContext'
import { AppProvider } from '@/context/AppContext'
import { ROUTES } from '@/constants/navigation'

import Login       from '@/components/screens/Login'
import Dashboard   from '@/components/screens/Dashboard'
import PredictLive from '@/components/screens/PredictLive'
import PreGame     from '@/components/screens/PreGame'
// import History     from '@/components/screens/History'
import Billing     from '@/components/screens/Billing'
import Account     from '@/components/screens/Account'
import Models      from '@/components/screens/Models'

// ─────────────────────────────────────────────────────────────────
// App
// Root component — wraps everything in providers + router
// ─────────────────────────────────────────────────────────────────

function AuthenticatedRoute({ children }) {
  const { isAuthenticated, authReady } = useApp()
  if (!authReady) {
    return (
      <div style={{ padding: 40, color: 'var(--txt-d)', fontFamily: 'Exo 2, sans-serif' }}>
        Loading session...
      </div>
    )
  }
  if (!isAuthenticated) return <Navigate to={ROUTES.LOGIN} replace />
  return children
}

function AppRoutes() {
  const { isAuthenticated, authReady } = useApp()

  if (!authReady) {
    return (
      <div style={{ padding: 40, color: 'var(--txt-d)', fontFamily: 'Exo 2, sans-serif' }}>
        Loading session...
      </div>
    )
  }

  return (
    <Routes>
      <Route
        path={ROUTES.LOGIN}
        element={isAuthenticated ? <Navigate to={ROUTES.DASHBOARD} replace /> : <Login />}
      />
      <Route path={ROUTES.DASHBOARD} element={<AuthenticatedRoute><Dashboard /></AuthenticatedRoute>} />
      <Route path={ROUTES.PREDICT_LIVE} element={<AuthenticatedRoute><PredictLive /></AuthenticatedRoute>} />
      <Route path={ROUTES.PRE_GAME} element={<AuthenticatedRoute><PreGame /></AuthenticatedRoute>} />
      {/* <Route path={ROUTES.HISTORY} element={<AuthenticatedRoute><History /></AuthenticatedRoute>} /> */}
      <Route path={ROUTES.BILLING} element={<AuthenticatedRoute><Billing /></AuthenticatedRoute>} />
      <Route path={ROUTES.ACCOUNT} element={<AuthenticatedRoute><Account /></AuthenticatedRoute>} />
      <Route path={ROUTES.MODELS} element={<AuthenticatedRoute><Models /></AuthenticatedRoute>} />
      <Route path="*" element={<Navigate to={isAuthenticated ? ROUTES.DASHBOARD : ROUTES.LOGIN} replace />} />
    </Routes>
  )
}

export default function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <AppRoutes />
      </BrowserRouter>
    </AppProvider>
  )
}
