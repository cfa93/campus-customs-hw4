import { useEffect, useRef, useState, type FormEvent } from 'react'
import { Link, useLocation } from 'react-router-dom'
import {
  fetchChatHistory,
  formatPrice,
  sendChat,
  type ChatTurn,
  type ProductCard,
  type PublicUser,
} from '../api.ts'
import { useAuth } from '../auth-context.ts'
import { useChatProducts } from '../chat-products.ts'

type Message = {
  role: 'user' | 'assistant'
  content: string
  products?: ProductCard[]
}

const GREETING: Message = {
  role: 'assistant',
  content: "Hi! I'm the Campus Customs assistant. Ask me about products, sizes or stock.",
}

const MAX_HISTORY = 20

// Pull the product id out of a /products/:id path (not the /products list).
function productIdFromPath(pathname: string): string | null {
  const match = pathname.match(/^\/products\/([^/]+)$/)
  return match ? match[1] : null
}

// Remount the panel when the signed-in user changes, so state resets cleanly
// (fresh greeting for a guest, loaded history for a user) without clearing
// state synchronously inside an effect.
export default function ChatBox() {
  const { user } = useAuth()
  return <ChatPanel key={user?.id ?? 'guest'} user={user} />
}

function ChatPanel({ user }: { user: PublicUser | null }) {
  const { setMatches } = useChatProducts()
  const location = useLocation()
  const [open, setOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([GREETING])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [error, setError] = useState(false)
  // The turn that failed, kept so Retry can resend it with the same context.
  const [pending, setPending] = useState<{ text: string; history: ChatTurn[] } | null>(null)
  const scrollRef = useRef<HTMLDivElement>(null)

  // Load this shopper's saved history once, when the panel mounts for them.
  useEffect(() => {
    if (!user) return
    let cancelled = false
    fetchChatHistory(user.id)
      .then((data) => {
        if (cancelled) return
        const restored: Message[] = data.messages.map((m) => ({
          role: m.role,
          content: m.content,
          products: m.products,
        }))
        setMessages([GREETING, ...restored])
        const lastWithProducts = [...data.messages].reverse().find((m) => m.products.length > 0)
        if (lastWithProducts) setMatches(lastWithProducts.products)
      })
      .catch(() => {
        // keep the default greeting on failure
      })
    return () => {
      cancelled = true
    }
  }, [user, setMatches])

  function scrollToBottom() {
    requestAnimationFrame(() => {
      const el = scrollRef.current
      if (el) el.scrollTop = el.scrollHeight
    })
  }

  async function runTurn(text: string, history: ChatTurn[]) {
    setBusy(true)
    setError(false)
    scrollToBottom()
    try {
      const res = await sendChat(text, {
        history,
        user,
        currentProductId: productIdFromPath(location.pathname),
      })
      setMessages((prev) => [...prev, { role: 'assistant', content: res.message, products: res.products }])
      if (res.products.length > 0) setMatches(res.products)
      setPending(null)
    } catch {
      // Keep the turn so Retry can resend it with the same history.
      setPending({ text, history })
      setError(true)
    } finally {
      setBusy(false)
      scrollToBottom()
    }
  }

  function handleSubmit(e: FormEvent) {
    e.preventDefault()
    const text = input.trim()
    if (!text || busy) return

    const history: ChatTurn[] = messages
      .filter((m) => m !== GREETING)
      .slice(-MAX_HISTORY)
      .map((m) => ({ role: m.role, content: m.content }))

    setMessages((prev) => [...prev, { role: 'user', content: text }])
    setInput('')
    void runTurn(text, history)
  }

  function handleRetry() {
    if (!pending || busy) return
    void runTurn(pending.text, pending.history)
  }

  return (
    <div className="chat">
      {open && (
        <div className="chat-panel" role="dialog" aria-label="Shopping assistant">
          <header className="chat-header">
            <span>Campus Customs assistant</span>
            <button type="button" className="chat-close" onClick={() => setOpen(false)} aria-label="Close chat">
              ×
            </button>
          </header>
          <div className="chat-messages" ref={scrollRef}>
            {messages.map((m, i) => (
              <div key={i} className={`chat-row ${m.role}`}>
                <p className={`chat-msg ${m.role}`}>{m.content}</p>
                {m.products && m.products.length > 0 && (
                  <div className="chat-cards">
                    {m.products.map((p) => (
                      <Link key={p.product_id} to={`/products/${p.product_id}`} className="chat-card">
                        <img src={p.image_url} alt={p.name} loading="lazy" />
                        <div className="chat-card-body">
                          <span className="chat-card-name">{p.name}</span>
                          <span className="price">{formatPrice(p.price)}</span>
                        </div>
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            ))}
            {busy && (
              <p className="chat-msg assistant typing" aria-live="polite">
                Looking that up
                <span className="dots">
                  <span></span>
                  <span></span>
                  <span></span>
                </span>
              </p>
            )}
            {error && (
              <div className="chat-error" role="alert">
                <span>Couldn't reach the shop. Please try again.</span>
                <button type="button" className="btn btn-small" onClick={handleRetry} disabled={busy}>
                  Retry
                </button>
              </div>
            )}
          </div>
          <form className="chat-form" onSubmit={handleSubmit}>
            <input
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about a product…"
              aria-label="Message"
              disabled={busy}
            />
            <button type="submit" className="btn btn-small" disabled={busy}>
              Send
            </button>
          </form>
        </div>
      )}
      <button
        type="button"
        className="chat-toggle"
        onClick={() => setOpen((o) => !o)}
        aria-label={open ? 'Close chat' : 'Open chat'}
      >
        {open ? '×' : '💬'}
      </button>
    </div>
  )
}
