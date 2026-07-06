const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

async function request(path, options = {}) {
  const headers = {
    'Content-Type': 'application/json',
    ...(options.headers || {}),
  }
  const res = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
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

export function getBillingSummary({ accessToken, apiKey } = {}) {
  const headers = {}
  if (accessToken) headers.Authorization = `Bearer ${accessToken}`
  if (apiKey) headers['X-API-Key'] = apiKey
  return request('/billing/summary', { method: 'GET', headers })
}

export function getCreditPacks() {
  return request('/billing/packs', { method: 'GET' })
}

export function createCreditCheckout({ accessToken, packId }) {
  return request('/billing/purchase', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({ pack_id: packId }),
  })
}

export function verifyPurchase({ accessToken, sessionId }) {
  return request('/billing/verify-session', {
    method: 'POST',
    headers: {
      Authorization: `Bearer ${accessToken}`,
    },
    body: JSON.stringify({ session_id: sessionId }),
  })
}
