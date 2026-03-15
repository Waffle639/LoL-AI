import { createContext, ReactNode, useMemo, useState } from 'react'

type AuthContextValue = {
  apiKey: string | null
  setApiKey: (key: string | null) => void
  clearApiKey: () => void
}

export const AuthContext = createContext<AuthContextValue>({
  apiKey: null,
  setApiKey: () => {},
  clearApiKey: () => {},
})

export function AuthProvider({ children }: { children: ReactNode }) {
  const [apiKey, setApiKeyState] = useState<string | null>(() => localStorage.getItem('api_key'))

  const setApiKey = (key: string | null) => {
    if (key) {
      localStorage.setItem('api_key', key)
    } else {
      localStorage.removeItem('api_key')
    }
    setApiKeyState(key)
  }

  const clearApiKey = () => setApiKey(null)

  const value = useMemo(
    () => ({ apiKey, setApiKey, clearApiKey }),
    [apiKey],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
