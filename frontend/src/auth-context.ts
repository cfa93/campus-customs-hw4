import { createContext, useContext } from 'react'
import type { PublicUser } from './api.ts'

export type AuthState = {
  user: PublicUser | null
  setUser: (user: PublicUser | null) => void
}

export const STORAGE_KEY = 'campus_customs_user'
export const AuthContext = createContext<AuthState | null>(null)

export function useAuth(): AuthState {
  const ctx = useContext(AuthContext)
  if (!ctx) throw new Error('useAuth must be used inside AuthProvider')
  return ctx
}
