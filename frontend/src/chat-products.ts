import { createContext, useContext } from 'react'
import type { ProductCard } from './api.ts'

export type ChatProductsState = {
  matches: ProductCard[]
  setMatches: (products: ProductCard[]) => void
}

export const ChatProductsContext = createContext<ChatProductsState | null>(null)

export function useChatProducts(): ChatProductsState {
  const ctx = useContext(ChatProductsContext)
  if (!ctx) throw new Error('useChatProducts must be used inside ChatProductsProvider')
  return ctx
}
