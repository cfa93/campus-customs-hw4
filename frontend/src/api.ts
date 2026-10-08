export type SizeStock = {
  size: string
  quantity: number
}

export type ProductSummary = {
  product_id: string
  name: string
  garment_type: string
  category: string
  description: string
  colors: string[]
  price: number
  image_url: string
  total_stock: number
}

export type ProductDetail = ProductSummary & {
  search_tags: string[]
  inventory: SizeStock[]
}

export class NotFoundError extends Error {}

async function getJson<T>(url: string): Promise<T> {
  const res = await fetch(url)
  if (res.status === 404) throw new NotFoundError()
  if (!res.ok) throw new Error(`Request failed: ${res.status}`)
  return res.json() as Promise<T>
}

export const fetchProducts = () => getJson<ProductSummary[]>('/api/products')

export const fetchProduct = (id: string) =>
  getJson<ProductDetail>(`/api/products/${encodeURIComponent(id)}`)

export const formatPrice = (price: number) => `$${price.toFixed(2)}`

export type PublicUser = {
  id: number
  first_name: string | null
  last_name: string | null
  name: string
  email: string
}

export type SignupInput = {
  first_name: string
  last_name: string
  email: string
  password: string
}

async function postJson<T>(url: string, body: unknown): Promise<T> {
  const res = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
  if (!res.ok) {
    let detail = `Request failed: ${res.status}`
    try {
      const data = await res.json()
      if (typeof data?.detail === 'string') detail = data.detail
    } catch {
      // keep the default message
    }
    throw new Error(detail)
  }
  return res.json() as Promise<T>
}

export const signup = (input: SignupInput) => postJson<PublicUser>('/api/signup', input)

export const login = (email: string, password: string) =>
  postJson<PublicUser>('/api/login', { email, password })

export const resetPassword = (email: string, newPassword: string) =>
  postJson<PublicUser>('/api/reset-password', { email, new_password: newPassword })

export type ChatTurn = {
  role: 'user' | 'assistant'
  content: string
}

export type ChatResponse = {
  message: string
  products: ProductCard[]
}

export type ProductCard = {
  product_id: string
  name: string
  garment_type: string
  description: string
  colors: string[]
  price: number
  image_url: string
  inventory: SizeStock[]
  total_stock: number
}

export type ChatContext = {
  history: ChatTurn[]
  user: PublicUser | null
  currentProductId: string | null
}

export const sendChat = (message: string, ctx: ChatContext) =>
  postJson<ChatResponse>('/api/chat', {
    message,
    history: ctx.history,
    user_id: ctx.user?.id ?? null,
    first_name: ctx.user?.first_name ?? null,
    last_name: ctx.user?.last_name ?? null,
    email: ctx.user?.email ?? null,
    current_product_id: ctx.currentProductId,
  })

export type ChatHistoryMessage = {
  role: 'user' | 'assistant'
  content: string
  products: ProductCard[]
}

export const fetchChatHistory = (userId: number) =>
  getJson<{ messages: ChatHistoryMessage[] }>(`/api/chat/history?user_id=${userId}`)
