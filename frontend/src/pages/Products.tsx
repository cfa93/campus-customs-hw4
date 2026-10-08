import { useEffect, useMemo, useState } from 'react'
import { fetchProducts, type ProductSummary } from '../api.ts'
import ProductTile from '../components/ProductTile.tsx'

const PRICE_RANGES = [
  { label: 'Any price', min: 0, max: Infinity },
  { label: 'Under $40', min: 0, max: 40 },
  { label: '$40 – $60', min: 40, max: 60 },
  { label: '$60 – $80', min: 60, max: 80 },
  { label: '$80 & up', min: 80, max: Infinity },
]

export default function Products() {
  const [products, setProducts] = useState<ProductSummary[] | null>(null)
  const [error, setError] = useState(false)
  const [category, setCategory] = useState('All')
  const [priceIdx, setPriceIdx] = useState(0)

  useEffect(() => {
    fetchProducts()
      .then(setProducts)
      .catch(() => setError(true))
  }, [])

  const categories = useMemo(() => {
    if (!products) return []
    return ['All', ...[...new Set(products.map((p) => p.category))].sort()]
  }, [products])

  const filtered = useMemo(() => {
    if (!products) return []
    const range = PRICE_RANGES[priceIdx]
    return products.filter(
      (p) =>
        (category === 'All' || p.category === category) &&
        p.price >= range.min &&
        p.price < (range.max === Infinity ? Infinity : range.max),
    )
  }, [products, category, priceIdx])

  return (
    <>
      <section className="hero hero-compact">
        <p className="eyebrow">Products</p>
        <h1>
          The <span className="accent">collection</span>
        </h1>
        {products && (
          <p className="lead">
            {filtered.length === products.length
              ? `${products.length} pieces of Yale gear, ready to wear.`
              : `Showing ${filtered.length} of ${products.length} pieces.`}
          </p>
        )}
      </section>

      {error && <p className="notice">Couldn't load products. Is the backend running?</p>}
      {!products && !error && <p className="muted">Loading products…</p>}

      {products && (
        <>
          <div className="filters">
            <label className="filter">
              Category
              <select value={category} onChange={(e) => setCategory(e.target.value)}>
                {categories.map((c) => (
                  <option key={c} value={c}>
                    {c}
                  </option>
                ))}
              </select>
            </label>
            <label className="filter">
              Price
              <select value={priceIdx} onChange={(e) => setPriceIdx(Number(e.target.value))}>
                {PRICE_RANGES.map((r, i) => (
                  <option key={r.label} value={i}>
                    {r.label}
                  </option>
                ))}
              </select>
            </label>
            {(category !== 'All' || priceIdx !== 0) && (
              <button
                type="button"
                className="btn btn-ghost btn-small"
                onClick={() => {
                  setCategory('All')
                  setPriceIdx(0)
                }}
              >
                Clear filters
              </button>
            )}
          </div>

          {filtered.length === 0 ? (
            <p className="muted">No products match these filters.</p>
          ) : (
            <section className="product-grid">
              {filtered.map((p) => (
                <ProductTile key={p.product_id} product={p} />
              ))}
            </section>
          )}
        </>
      )}
    </>
  )
}
