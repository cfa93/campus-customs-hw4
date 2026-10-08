import { useMemo, useState, type ReactNode } from 'react'
import type { PublicUser } from './api.ts'
import { AuthContext, STORAGE_KEY, type AuthState } from './auth-context.ts'

function readStoredUser(): PublicUser | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? (JSON.parse(raw) as PublicUser) : null
  } catch {
    return null
  }
}

export function AuthProvider({ children }: { children: ReactNode }) {
  const [user, setUserState] = useState<PublicUser | null>(readStoredUser)

  const value = useMemo<AuthState>(
    () => ({
      user,
      setUser: (next) => {
        setUserState(next)
        if (next) localStorage.setItem(STORAGE_KEY, JSON.stringify(next))
        else localStorage.removeItem(STORAGE_KEY)
      },
    }),
    [user],
  )

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>
}
