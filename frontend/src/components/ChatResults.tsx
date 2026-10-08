import { useChatProducts } from '../chat-products.ts'
import ProductTile from './ProductTile.tsx'

// Products the chatbot matched, rendered as cards on the page. Updates whenever
// the assistant returns a new set of matches.
export default function ChatResults() {
  const { matches } = useChatProducts()
  if (matches.length === 0) return null

  return (
    <section className="chat-results">
      <h2>
        Picked from your <span className="accent">chat</span>
      </h2>
      <div className="product-grid">
        {matches.map((p) => (
          <ProductTile key={p.product_id} product={p} />
        ))}
      </div>
    </section>
  )
}
