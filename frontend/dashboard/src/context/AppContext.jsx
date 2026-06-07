import { createContext, useContext, useMemo, useState, useEffect, useRef } from 'react'
import { login, register, refresh, me } from '@/api/auth'

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
    if (parsed?.apiKey) {
      delete parsed.apiKey
      localStorage.setItem(AUTH_STORAGE_KEY, JSON.stringify(parsed))
    }
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

function parseJwt(token) {
  if (!token) return null
  try {
    const payload = token.split('.')[1]
    if (!payload) return null
    const normalized = payload.replace(/-/g, '+').replace(/_/g, '/')
    const padded = normalized + '==='.slice((normalized.length + 3) % 4)
    const decoded = atob(padded)
    return JSON.parse(decoded)
  } catch {
    return null
  }
}

export function AppProvider({ children }) {
  const [session, setSession]       = useState(initialSession)
  const [credits, setCredits]       = useState(() => initialSession()?.credits ?? 0)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [authLoading, setAuthLoading] = useState(false)
  const [authReady, setAuthReady] = useState(false)
  const refreshTimerRef = useRef(null)

  const user = session?.user ?? { name: 'Guest', initial: 'G', email: '' }
  const apiKeyPrefix = session?.apiKeyPrefix ?? ''
  const accessToken = session?.accessToken ?? ''
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

  const setSessionAndPersist = next => {
    setSession(next)
    setCredits(next?.credits ?? 0)
    persistSession(next)
  }

  const clearRefreshTimer = () => {
    if (refreshTimerRef.current) {
      clearTimeout(refreshTimerRef.current)
      refreshTimerRef.current = null
    }
  }

  const scheduleRefresh = accessTokenValue => {
    clearRefreshTimer()
    const payload = parseJwt(accessTokenValue)
    if (!payload?.exp) return
    const expMs = payload.exp * 1000
    const delay = Math.max(expMs - Date.now() - 60_000, 10_000)
    refreshTimerRef.current = setTimeout(() => {
      refreshSession()
    }, delay)
  }

  const applyAuthResponse = payload => {
    const normalized = {
      user: {
        name: payload.username,
        initial: (payload.username || '?').charAt(0).toUpperCase(),
        email: payload.email,
      },
      apiKeyPrefix: payload.api_key_prefix ?? session?.apiKeyPrefix ?? '',
      accessToken: payload.access_token,
      refreshToken: payload.refresh_token,
      credits: payload.credits_remaining ?? 0,
    }
    setSessionAndPersist(normalized)
    scheduleRefresh(normalized.accessToken)
  }

  const applyProfile = (profile, accessTokenOverride) => {
    const accessTokenValue = accessTokenOverride || session?.accessToken || ''
    const normalized = {
      user: {
        name: profile?.username || session?.user?.name || 'Guest',
        initial: (profile?.username || session?.user?.name || '?').charAt(0).toUpperCase(),
        email: profile?.email || session?.user?.email || '',
      },
      apiKeyPrefix: profile?.api_key_prefix ?? session?.apiKeyPrefix ?? '',
      accessToken: accessTokenValue,
      refreshToken: session?.refreshToken,
      credits: profile?.credits_remaining ?? session?.credits ?? 0,
    }
    setSessionAndPersist(normalized)
    if (accessTokenValue) scheduleRefresh(accessTokenValue)
  }

  const updateApiKeyPrefix = nextPrefix => {
    if (!session) return
    const updated = {
      ...session,
      apiKeyPrefix: nextPrefix ?? '',
    }
    setSession(updated)
    persistSession(updated)
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

  const refreshSession = async (options = {}) => {
    try {
      const payload = await refresh()
      const accessTokenValue = payload?.access_token
      if (!accessTokenValue) throw new Error('No access token')

      if (options.updateProfile || !session?.user) {
        const profile = await me({ accessToken: accessTokenValue })
        applyProfile(profile, accessTokenValue)
      } else if (session) {
        const updated = { ...session, accessToken: accessTokenValue }
        setSessionAndPersist(updated)
        scheduleRefresh(accessTokenValue)
      }
      return accessTokenValue
    } catch (err) {
      console.error('Session refresh failed', err)
      logout()
      return null
    }
  }

  const getAccessToken = async () => {
    if (session?.accessToken) {
      const payload = parseJwt(session.accessToken)
      const expMs = payload?.exp ? payload.exp * 1000 : 0
      if (!expMs || expMs - Date.now() > 60_000) {
        return session.accessToken
      }
    }

    return await refreshSession()
  }

  const logout = () => {
    clearRefreshTimer()
    setSessionAndPersist(null)
  }

  useEffect(() => {
    let active = true
    const bootstrap = async () => {
      if (session?.accessToken) {
        const payload = parseJwt(session.accessToken)
        const expMs = payload?.exp ? payload.exp * 1000 : 0
        if (expMs && expMs - Date.now() < 60_000) {
          await refreshSession({ updateProfile: true })
        } else {
          scheduleRefresh(session.accessToken)
        }
        if (active) setAuthReady(true)
        return
      }

      await refreshSession({ updateProfile: true })
      if (active) setAuthReady(true)
    }

    bootstrap()
    return () => {
      active = false
      clearRefreshTimer()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  const value = useMemo(() => ({
    credits,
    setCredits,
    consumeCredit,
    sidebarOpen,
    setSidebarOpen,
    user,
    apiKeyPrefix,
    accessToken,
    isAuthenticated,
    authLoading,
    authReady,
    loginClient,
    registerClient,
    logout,
    updateApiKeyPrefix,
    refreshSession,
    getAccessToken,
  }), [
    credits,
    sidebarOpen,
    user,
    apiKeyPrefix,
    accessToken,
    isAuthenticated,
    authLoading,
    authReady,
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
