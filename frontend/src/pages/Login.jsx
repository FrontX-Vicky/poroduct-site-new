import { useState } from 'react'
import { useLocation, useNavigate } from 'react-router-dom'
import { api, setToken } from '../api'

export default function Login({ onLogin }) {
  const [mode, setMode] = useState('login')
  const [form, setForm] = useState({ email: '', password: '' })
  const [error, setError] = useState(null)
  const [busy, setBusy] = useState(false)
  const navigate = useNavigate()
  const message = useLocation().state?.message

  const submit = async (e) => {
    e.preventDefault()
    setError(null)
    setBusy(true)
    try {
      const { token, user } = await api(`/auth/${mode}`, { method: 'POST', body: form })
      setToken(token)
      onLogin(user)
      navigate('/')
    } catch (err) {
      setError(err)
    } finally {
      setBusy(false)
    }
  }

  const switchMode = (next) => {
    setMode(next)
    setError(null)
  }

  const field = (name, type, label) => (
    <label className="field">
      {label}
      <input className={`input${error?.fields[name] ? ' invalid' : ''}`} type={type} value={form[name]}
        autoComplete={name === 'password' ? (mode === 'login' ? 'current-password' : 'new-password') : 'email'}
        onChange={(e) => setForm({ ...form, [name]: e.target.value })} />
      {error?.fields[name] && <span className="field-error">{error.fields[name]}</span>}
    </label>
  )

  return (
    <form className="card form-card auth" onSubmit={submit} noValidate>
      <div>
        <h2>{mode === 'login' ? 'Welcome back' : 'Create your account'}</h2>
        <p className="muted" style={{ margin: '4px 0 0' }}>
          {mode === 'login' ? 'Log in to add and edit products.' : 'It only takes a moment.'}
        </p>
      </div>
      <div className={`segmented${mode === 'register' ? ' right' : ''}`}>
        <span className="indicator" />
        <button type="button" className={mode === 'login' ? 'active' : ''} onClick={() => switchMode('login')}>Log in</button>
        <button type="button" className={mode === 'register' ? 'active' : ''} onClick={() => switchMode('register')}>Register</button>
      </div>
      {message && <div className="alert">{message}</div>}
      {error && <div className="alert alert-error">{error.message}</div>}
      {field('email', 'email', 'Email')}
      {field('password', 'password', 'Password')}
      <button type="submit" className="btn btn-primary" disabled={busy}>
        {busy ? 'Please wait…' : mode === 'login' ? 'Log in' : 'Create account'}
      </button>
    </form>
  )
}
