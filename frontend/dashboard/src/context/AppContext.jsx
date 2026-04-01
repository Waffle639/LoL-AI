import { createContext, useContext, useMemo, useState } from 'react'
import { login, register } from '@/api/auth'

// ─────────────────────────────────────────────────────────────────
// AppContext
// Global state: credits, sidebar open/closed, current user
// ─────────────────────────────────────────────────────────────────

const AppContext = createContext(null)
const AUTH_STORAGE_KEY = 'lol_ai_dashboard_auth'

function initialSession() {
  try {
    const raw = localStorage.getItem(AUTH_STORAGE_KEY)
    if (!raw) return null
    const parsed = JSON.parse(raw)
    if (!parsed?.user || !parsed?.accessToken) return null
    return parsed
  } catch {
    return null
  }
}

function persistSession(session) {
  if (!session) {
    localStorage.removeItem(AUTH_STORAGE_KEY)
    return
  }
  localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(session))
}

export function AppProvider({ children }) {
  const [session, setSession]       = useState(initialSession)
  const [credits, setCredits]       = useState(() => initialSession()?.credits ?? 0)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [authLoading, setAuthLoading] = useState(false)

  const user = session?.user ?? { name: 'Guest', initial: 'G', email: '' }
  const apiKey = session?.apiKey ?? ''
  const isAuthenticated = Boolean(session?.accessToken)

  const consumeCredit = () => {
    setCredits(current => {
      const next = Math.max(0, current - 1)
      if (session) {
        const updated = { ...session, credits: next }
        setSession(updated)
        persistSession(updated)
      }
      return next
    })
  }

  const applyAuthResponse = payload => {
    const normalized = {
      user: {
        name: payload.username,
        initial: (payload.username || '?').charAt(0).toUpperCase(),
        email: payload.email,
      },
      apiKey: payload.api_key ?? session?.apiKey ?? '',
      accessToken: payload.access_token,
      refreshToken: payload.refresh_token,
      credits: payload.credits_remaining ?? 0,
    }
    setSession(normalized)
    setCredits(normalized.credits)
    persistSession(normalized)
  }

  const loginClient = async credentials => {
    setAuthLoading(true)
    try {
      const payload = await login(credentials)
      applyAuthResponse(payload)
      return payload
    } finally {
      setAuthLoading(false)
    }
  }

  const registerClient = async profile => {
    setAuthLoading(true)
    try {
      const payload = await register(profile)
      applyAuthResponse(payload)
      return payload
    } finally {
      setAuthLoading(false)
    }
  }

  const logout = () => {
    setSession(null)
    setCredits(0)
    persistSession(null)
  }

  const value = useMemo(() => ({
    credits,
    setCredits,
    consumeCredit,
    sidebarOpen,
    setSidebarOpen,
    user,
    apiKey,
    isAuthenticated,
    authLoading,
    loginClient,
    registerClient,
    logout,
  }), [
    credits,
    sidebarOpen,
    user,
    apiKey,
    isAuthenticated,
    authLoading,
  ])

  return (
    <AppContext.Provider value={value}>
      {children}
    </AppContext.Provider>
  )
}

// Hook for consuming context
export function useApp() {
  const ctx = useContext(AppContext)
  if (!ctx) throw new Error('useApp must be used inside AppProvider')
  return ctx
}
