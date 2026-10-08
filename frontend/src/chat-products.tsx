import { useMemo, useState, type ReactNode } from 'react'
import type { ProductCard } from './api.ts'
import { ChatProductsContext, type ChatProductsState } from './chat-products.ts'

export function ChatProductsProvider({ children }: { children: ReactNode }) {
  const [matches, setMatches] = useState<ProductCard[]>([])
  const value = useMemo<ChatProductsState>(() => ({ matches, setMatches }), [matches])
  return <ChatProductsContext.Provider value={value}>{children}</ChatProductsContext.Provider>
}
