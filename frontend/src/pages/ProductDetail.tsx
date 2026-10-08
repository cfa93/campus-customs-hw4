import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { fetchProduct, formatPrice, NotFoundError, type ProductDetail as Product } from '../api.ts'

const LOW_STOCK = 5

type Result = {
  id: string
  status: 'ready' | 'not-found' | 'error'
  product?: Product
}

export default function ProductDetail() {
  const { productId = '' } = useParams()
  const [result, setResult] = useState<Result | null>(null)

  useEffect(() => {
    let cancelled = false
    fetchProduct(productId)
      .then((product) => !cancelled && setResult({ id: productId, status: 'ready', product }))
      .catch(
        (err) =>
          !cancelled && setResult({ id: productId, status: err instanceof NotFoundError ? 'not-found' : 'error' }),
      )
    return () => {
      cancelled = true
    }
  }, [productId])

  // Still loading until the result matches the product in the URL.
  if (result?.id !== productId) return <p className="muted">Loading product…</p>
  const { status, product } = result
  if (status !== 'ready' || !product) {
    return (
      <section className="hero hero-compact">
        <h1>{status === 'not-found' ? 'Product not found' : "Couldn't load this product"}</h1>
        <Link to="/products" className="btn">
          Back to products
        </Link>
      </section>
    )
  }

  return (
    <>
      <Link to="/products" className="back-link">
        ← All products
      </Link>
      <section className="product-detail">
        <div className="product-detail-img">
          <img src={product.image_url} alt={product.name} />
        </div>
        <div className="product-detail-info">
          <p className="eyebrow">{product.garment_type}</p>
          <h1>{product.name}</h1>
          <p className="price price-large">{formatPrice(product.price)}</p>
          <p>{product.description}</p>
          <p className="muted">Colors: {product.colors.join(', ')}</p>

          <h2 className="sizes-heading">Sizes</h2>
          {product.total_stock === 0 ? (
            <p className="notice">Sold out in every size.</p>
          ) : (
            <ul className="size-list">
              {product.inventory.map((s) => (
                <li key={s.size} className={s.quantity === 0 ? 'size sold-out' : 'size'}>
                  <span className="size-label">{s.size}</span>
                  <span className="size-stock">
                    {s.quantity === 0
                      ? 'Sold out'
                      : s.quantity <= LOW_STOCK
                        ? `Only ${s.quantity} left`
                        : `${s.quantity} in stock`}
                  </span>
                </li>
              ))}
            </ul>
          )}
        </div>
      </section>
    </>
  )
}
