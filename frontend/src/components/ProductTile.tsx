import { Link } from 'react-router-dom'
import { formatPrice } from '../api.ts'

type Props = {
  product: {
    product_id: string
    name: string
    description: string
    price: number
    image_url: string
    total_stock: number
  }
}

// One product card, shared by the Products grid and the chat results so both
// look the same and open the same product page.
export default function ProductTile({ product: p }: Props) {
  return (
    <Link to={`/products/${p.product_id}`} className="product-card">
      <div className="product-card-img">
        <img src={p.image_url} alt={p.name} loading="lazy" />
        {p.total_stock === 0 && <span className="badge">Sold out</span>}
      </div>
      <div className="product-card-body">
        <h3>{p.name}</h3>
        <p className="product-card-desc">{p.description}</p>
        <p className="price">{formatPrice(p.price)}</p>
      </div>
    </Link>
  )
}
