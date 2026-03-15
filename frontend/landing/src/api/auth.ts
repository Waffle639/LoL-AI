import axios from 'axios'

const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
})

export async function register(payload: { username: string; email: string; password: string }) {
  const { data } = await api.post('/account/register', payload)
  return data
}

export async function login(payload: { email: string; password: string }) {
  const { data } = await api.post('/account/login', payload)
  return data
}
