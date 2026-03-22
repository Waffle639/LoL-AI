import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { AppProvider } from '@/context/AppContext'
import { ROUTES } from '@/constants/navigation'

import Login       from '@/components/screens/Login'
import Dashboard   from '@/components/screens/Dashboard'
import PredictLive from '@/components/screens/PredictLive'
import PreGame     from '@/components/screens/PreGame'
import History     from '@/components/screens/History'
import Billing     from '@/components/screens/Billing'
import Account     from '@/components/screens/Account'
import Models      from '@/components/screens/Models'

// ─────────────────────────────────────────────────────────────────
// App
// Root component — wraps everything in providers + router
// ─────────────────────────────────────────────────────────────────

export default function App() {
  return (
    <AppProvider>
      <BrowserRouter>
        <Routes>
          <Route path={ROUTES.LOGIN}        element={<Login />}       />
          <Route path={ROUTES.DASHBOARD}    element={<Dashboard />}   />
          <Route path={ROUTES.PREDICT_LIVE} element={<PredictLive />} />
          <Route path={ROUTES.PRE_GAME}     element={<PreGame />}     />
          <Route path={ROUTES.HISTORY}      element={<History />}     />
          <Route path={ROUTES.BILLING}      element={<Billing />}     />
          <Route path={ROUTES.ACCOUNT}      element={<Account />}     />
          <Route path={ROUTES.MODELS}       element={<Models />}      />
          {/* Fallback */}
          <Route path="*" element={<Navigate to={ROUTES.LOGIN} replace />} />
        </Routes>
      </BrowserRouter>
    </AppProvider>
  )
}
