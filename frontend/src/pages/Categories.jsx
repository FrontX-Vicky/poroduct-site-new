import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'

export default function Categories({ user }) {
  const [categories, setCategories] = useState([])
  const [name, setName] = useState('')
  const [error, setError] = useState(null)
  const [saving, setSaving] = useState(false)

  const load = () => api('/categories').then(setCategories)
  useEffect(() => { load() }, [])

  const submit = async (e) => {
    e.preventDefault()
    setError(null)
    setSaving(true)
    try {
      await api('/categories', { method: 'POST', body: { name } })
      setName('')
      load()
    } catch (err) {
      setError(err)
    } finally {
      setSaving(false)
    }
  }

  return (
    <>
      <div className="page-head">
        <div>
          <h1>Categories</h1>
          <p className="muted" style={{ margin: '4px 0 0' }}>Pick a category to browse its products.</p>
        </div>
      </div>

      {user && (
        <form onSubmit={submit} style={{ maxWidth: 480, marginBottom: 24 }}>
          <div className="inline-form">
            <input className={`input${error ? ' invalid' : ''}`} placeholder="New category name" value={name}
              onChange={(e) => setName(e.target.value)} aria-label="New category name" />
            <button type="submit" className="btn btn-primary" disabled={saving}>Add</button>
          </div>
          {error && <span className="field-error">{error.fields.name || error.message}</span>}
        </form>
      )}

      <div className="cat-grid">
        {categories.map((c, i) => (
          <Link key={c.id} to={`/?category_id=${c.id}`} className="cat" style={{ '--i': i }}>
            {c.name}<span>→</span>
          </Link>
        ))}
      </div>
    </>
  )
}
