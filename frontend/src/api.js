const TOKEN_KEY = 'token'

export const getToken = () => localStorage.getItem(TOKEN_KEY)
export const setToken = (token) =>
  token ? localStorage.setItem(TOKEN_KEY, token) : localStorage.removeItem(TOKEN_KEY)

export class ApiError extends Error {
  constructor(status, detail) {
    super(typeof detail === 'string' ? detail : 'Please fix the errors below')
    this.status = status
    // FastAPI validation errors -> { fieldName: message }
    this.fields = {}
    if (Array.isArray(detail)) {
      for (const d of detail) this.fields[d.loc[d.loc.length - 1]] = d.msg
    }
  }
}

export async function api(path, { method = 'GET', body } = {}) {
  const headers = { 'Content-Type': 'application/json' }
  const token = getToken()
  if (token) headers.Authorization = `Bearer ${token}`

  const res = await fetch(`/api${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : undefined,
  })
  if (res.status === 401 && token) {
    // Session is gone on the server: drop it locally and tell the app
    setToken(null)
    window.dispatchEvent(new Event('session-expired'))
  }
  if (res.status === 204) return null
  const data = await res.json()
  if (!res.ok) throw new ApiError(res.status, data.detail)
  return data
}
