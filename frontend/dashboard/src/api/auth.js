const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function request(path, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  }
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    credentials: options.credentials || 'omit',
    headers,
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
  return request('/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
    credentials: 'include',
  })
}

export function login(payload) {
  return request('/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
    credentials: 'include',
  })
}

export function me({ accessToken, apiKey } = {}) {
  const headers = {}
  if (accessToken) headers.Authorization = `Bearer ${accessToken}`
  if (apiKey) headers['X-API-Key'] = apiKey
  return request('/auth/me', {
    method: 'GET',
    headers,
  })
}

export function refresh() {
  return request('/auth/refresh', {
    method: 'POST',
    credentials: 'include',
  })
}

export function createApiKey(accessToken) {
  return request('/auth/apikey/create', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  })
}

export function regenerateApiKey(accessToken) {
  return request('/auth/apikey/regenerate', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
  })
}
