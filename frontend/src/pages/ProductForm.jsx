import { useEffect, useState } from 'react'
import { Link, useNavigate, useParams } from 'react-router-dom'
import { api } from '../api'

const EMPTY = { name: '', description: '', price: '', stock: '0', category_id: '' }

export default function ProductForm() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [form, setForm] = useState(EMPTY)
  const [categories, setCategories] = useState([])
  const [error, setError] = useState(null)
  const [saving, setSaving] = useState(false)

  useEffect(() => {
    api('/categories').then(setCategories)
    if (id) api(`/products/${id}`).then(({ category, ...p }) => setForm(p))
  }, [id])

  const submit = async (e) => {
    e.preventDefault()
    setError(null)
    setSaving(true)
    try {
      await api(id ? `/products/${id}` : '/products', { method: id ? 'PUT' : 'POST', body: form })
      navigate('/')
    } catch (err) {
      setError(err)
    } finally {
      setSaving(false)
    }
  }

  const set = (name) => (e) => setForm({ ...form, [name]: e.target.value })
  const invalid = (name) => `input${error?.fields[name] ? ' invalid' : ''}`
  const fieldError = (name) => error?.fields[name] && <span className="field-error">{error.fields[name]}</span>

  return (
    <form className="card form-card" onSubmit={submit} noValidate>
      <div>
        <h2>{id ? 'Edit product' : 'Add product'}</h2>
        <p className="muted" style={{ margin: '4px 0 0' }}>All fields are checked by the server.</p>
      </div>
      {error && <div className="alert alert-error">{error.message}</div>}
      <label className="field">Name
        <input className={invalid('name')} value={form.name} onChange={set('name')} />{fieldError('name')}
      </label>
      <label className="field">Description
        <textarea className={invalid('description')} value={form.description} onChange={set('description')} />
        {fieldError('description')}
      </label>
      <div className="field-row">
        <label className="field">Price (₹)
          <input className={invalid('price')} type="number" step="0.01" value={form.price} onChange={set('price')} />
          {fieldError('price')}
        </label>
        <label className="field">Stock
          <input className={invalid('stock')} type="number" value={form.stock} onChange={set('stock')} />
          {fieldError('stock')}
        </label>
      </div>
      <label className="field">Category
        <select className={invalid('category_id')} value={form.category_id} onChange={set('category_id')}>
          <option value="">Select a category</option>
          {categories.map((c) => <option key={c.id} value={c.id}>{c.name}</option>)}
        </select>
        {fieldError('category_id')}
      </label>
      <div className="form-actions">
        <Link to="/" className="btn btn-ghost">Cancel</Link>
        <button type="submit" className="btn btn-primary" disabled={saving}>{saving ? 'Saving…' : 'Save product'}</button>
      </div>
    </form>
  )
}
