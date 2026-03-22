import { createContext, useContext, useState } from 'react'

// ─────────────────────────────────────────────────────────────────
// AppContext
// Global state: credits, sidebar open/closed, current user
// ─────────────────────────────────────────────────────────────────

const AppContext = createContext(null)

export function AppProvider({ children }) {
  const [credits, setCredits]       = useState(42)
  const [sidebarOpen, setSidebarOpen] = useState(true)
  const [user] = useState({ name: 'Waffle639', initial: 'W' })

  const consumeCredit = () => setCredits(c => Math.max(0, c - 1))

  return (
    <AppContext.Provider value={{
      credits,
      setCredits,
      consumeCredit,
      sidebarOpen,
      setSidebarOpen,
      user,
    }}>
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
