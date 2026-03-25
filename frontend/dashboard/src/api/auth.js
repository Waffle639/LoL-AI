const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function request(path, options = {}) {
  const res = await fetch(`${API_BASE_URL}${path}`, {
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
    ...options,
  })

  const data = await res.json().catch(() => null)
  if (!res.ok) {
    const detail = data?.detail
    const message = typeof detail === 'string' ? detail : data?.message || 'Request failed'
    throw new Error(message)
  }
  return data
}

export function register(payload) {
  return request('/account/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function login(payload) {
  return request('/account/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

export function me(apiKey) {
  return request('/account/me', {
    method: 'GET',
    headers: {
      'X-API-Key': apiKey,
    },
  })
}
