import { useEffect, useState } from 'react'
import { Link, Navigate, NavLink, Route, Routes, useLocation, useNavigate } from 'react-router-dom'
import { api, getToken, setToken } from './api'
import Login from './pages/Login'
import Products from './pages/Products'
import ProductForm from './pages/ProductForm'
import Categories from './pages/Categories'

const navClass = ({ isActive }) => `nav-link${isActive ? ' active' : ''}`

export default function App() {
  const [user, setUser] = useState(null)
  const [checking, setChecking] = useState(!!getToken())
  const [menuOpen, setMenuOpen] = useState(false)
  const navigate = useNavigate()
  const location = useLocation()

  // Verify any stored session with the server on load
  useEffect(() => {
    if (!getToken()) return
    api('/auth/me')
      .then(setUser)
      .catch(() => setUser(null))
      .finally(() => setChecking(false))
  }, [])

  useEffect(() => {
    const onExpired = () => {
      setUser(null)
      navigate('/login', { state: { message: 'Your session has expired. Please log in again.' } })
    }
    window.addEventListener('session-expired', onExpired)
    return () => window.removeEventListener('session-expired', onExpired)
  }, [navigate])

  // Close the mobile menu whenever the page changes
  useEffect(() => setMenuOpen(false), [location.pathname])

  const logout = async () => {
    await api('/auth/logout', { method: 'POST' }).catch(() => {})
    setToken(null)
    setUser(null)
    navigate('/')
  }

  if (checking) return <div className="spinner" aria-label="Loading" />

  const requireAuth = (el) => (user ? el : <Navigate to="/login" replace />)

  const links = (
    <>
      <NavLink to="/" end className={navClass}>Products</NavLink>
      <NavLink to="/categories" className={navClass}>Categories</NavLink>
    </>
  )
  const actions = user ? (
    <>
      <span className="user-email">{user.email}</span>
      <button className="btn btn-ghost btn-sm" onClick={logout}>Log out</button>
      <Link to="/products/new" className="btn btn-primary btn-sm">Add product</Link>
    </>
  ) : (
    <Link to="/login" className="btn btn-primary btn-sm">Log in</Link>
  )

  return (
    <>
      <header className="nav">
        <div className="nav-inner">
          <Link to="/" className="brand"><span className="brand-dot" />ProductSite</Link>
          <nav className="nav-links">{links}</nav>
          <div className="nav-actions">{actions}</div>
          <button className="btn btn-ghost btn-sm menu-toggle" onClick={() => setMenuOpen(!menuOpen)}
            aria-label="Menu" aria-expanded={menuOpen}>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
              {menuOpen ? <path d="M6 6l12 12M18 6L6 18" /> : <path d="M4 7h16M4 12h16M4 17h16" />}
            </svg>
          </button>
        </div>
        {menuOpen && <div className="mobile-menu">{links}{actions}</div>}
      </header>
      <main className="container">
        <div className="page" key={location.pathname}>
          <Routes location={location}>
            <Route path="/" element={<Products user={user} />} />
            <Route path="/login" element={<Login onLogin={setUser} />} />
            <Route path="/categories" element={<Categories user={user} />} />
            <Route path="/products/new" element={requireAuth(<ProductForm />)} />
            <Route path="/products/:id/edit" element={requireAuth(<ProductForm />)} />
          </Routes>
        </div>
      </main>
    </>
  )
}
