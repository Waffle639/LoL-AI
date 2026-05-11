import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || 'http://localhost:8000',
})

export async function register(payload: { username: string; email: string; password: string }) {
  const { data } = await api.post('/auth/register', payload)
  return data
}

export async function login(payload: { email: string; password: string }) {
  const { data } = await api.post('/auth/login', payload)
  return data
}
