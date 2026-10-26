import { useEffect, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { api } from '../api'

const PAGE_SIZE = 12
const FILTER_KEYS = ['search', 'category_id', 'min_price', 'max_price']

export default function Products({ user }) {
  // Filters live in the URL so they survive refresh and can be shared
  const [params, setParams] = useSearchParams()
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(true)
  const [categories, setCategories] = useState([])
  const [draft, setDraft] = useState({})

  const page = Number(params.get('page') || 1)
  const activeCategory = params.get('category_id') || ''
  const hasFilters = FILTER_KEYS.some((k) => params.get(k))
  const totalPages = data ? Math.max(1, Math.ceil(data.total / PAGE_SIZE)) : 1

  useEffect(() => {
    api('/categories').then(setCategories)
  }, [])

  useEffect(() => {
    setDraft({
      search: params.get('search') || '',
      min_price: params.get('min_price') || '',
      max_price: params.get('max_price') || '',
    })
    const query = new URLSearchParams(params)
    query.set('page_size', PAGE_SIZE)
    setLoading(true)
    api(`/products?${query}`).then(setData).finally(() => setLoading(false))
  }, [params])

  const update = (changes) => {
    const next = new URLSearchParams(params)
    for (const [k, v] of Object.entries(changes)) v ? next.set(k, v) : next.delete(k)
    if (!('page' in changes)) next.delete('page')
    setParams(next)
  }

  const goToPage = (p) => {
    update({ page: p })
    window.scrollTo({ top: 0, behavior: 'smooth' })
  }

  const set = (name) => (e) => setDraft({ ...draft, [name]: e.target.value })

  return (
    <>
      <div className="page-head">
        <div>
          <h1>Products</h1>
          <p className="muted" style={{ margin: '4px 0 0' }}>
            {data ? `${data.total} item${data.total === 1 ? '' : 's'}` : 'Loading…'}
          </p>
        </div>
        {hasFilters && <button className="btn btn-ghost btn-sm" onClick={() => setParams({})}>Clear filters</button>}
      </div>

      <div className="toolbar">
        <form className="toolbar-row" onSubmit={(e) => { e.preventDefault(); update(draft) }}>
          <label className="search">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              <circle cx="11" cy="11" r="7" /><path d="M20 20l-3.5-3.5" />
            </svg>
            <input className="input" placeholder="Search products" value={draft.search || ''} onChange={set('search')}
              aria-label="Search products" />
          </label>
          <div className="price">
            <input className="input" type="number" min="0" placeholder="Min ₹" value={draft.min_price || ''}
              onChange={set('min_price')} aria-label="Minimum price" />
            <span className="muted">–</span>
            <input className="input" type="number" min="0" placeholder="Max ₹" value={draft.max_price || ''}
              onChange={set('max_price')} aria-label="Maximum price" />
          </div>
          <button type="submit" className="btn btn-primary">Apply</button>
        </form>

        <div className="chips" role="tablist" aria-label="Categories">
          <button className={`chip${!activeCategory ? ' active' : ''}`} onClick={() => update({ category_id: '' })}>
            All
          </button>
          {categories.map((c) => (
            <button key={c.id} className={`chip${activeCategory === String(c.id) ? ' active' : ''}`}
              onClick={() => update({ category_id: String(c.id) })}>
              {c.name}
            </button>
          ))}
        </div>
      </div>

      {!data ? (
        <div className="grid">
          {Array.from({ length: 8 }, (_, i) => (
            <div key={i} className="product skeleton" style={{ '--i': 0 }}>
              <div className="thumb bone" />
              <div className="bone" style={{ width: '40%' }} />
              <div className="bone" style={{ width: '85%' }} />
              <div className="bone" style={{ width: '60%' }} />
            </div>
          ))}
        </div>
      ) : data.items.length === 0 ? (
        <div className="empty">
          <h3>No products found</h3>
          <p className="muted">Try a different search or clear the filters.</p>
          {hasFilters && <button className="btn" onClick={() => setParams({})}>Clear filters</button>}
        </div>
      ) : (
        <div className={`grid${loading ? ' is-loading' : ''}`}>
          {data.items.map((p, i) => (
            <article key={p.id} className="product" style={{ '--i': i }}>
              <div className="thumb" aria-hidden="true">{p.name[0]}</div>
              <span className="tag">{p.category.name}</span>
              <h3>{p.name}</h3>
              <p className="muted clamp" style={{ margin: 0 }}>{p.description}</p>
              <div className="product-foot">
                <span className="price-tag">₹{p.price.toLocaleString('en-IN')}</span>
                <span className={`stock${p.stock ? '' : ' out'}`}>
                  {p.stock ? `${p.stock} in stock` : 'Out of stock'}
                </span>
              </div>
              {user && <Link to={`/products/${p.id}/edit`} className="btn btn-sm">Edit</Link>}
            </article>
          ))}
        </div>
      )}

      {data && totalPages > 1 && (
        <nav className="pagination" aria-label="Pagination">
          <button className="btn btn-sm" disabled={page <= 1} onClick={() => goToPage(page - 1)}>Previous</button>
          {pageWindow(page, totalPages).map((n) => (
            <button key={n} className={`btn btn-sm page-num${n === page ? ' active' : ''}`}
              onClick={() => goToPage(n)} aria-current={n === page ? 'page' : undefined}>
              {n}
            </button>
          ))}
          <button className="btn btn-sm" disabled={page >= totalPages} onClick={() => goToPage(page + 1)}>Next</button>
        </nav>
      )}
    </>
  )
}

// Up to 5 page numbers centred on the current page
function pageWindow(page, total) {
  const start = Math.max(1, Math.min(page - 2, total - 4))
  return Array.from({ length: Math.min(5, total) }, (_, i) => start + i)
}
