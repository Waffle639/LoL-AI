import axios from 'axios'

const client = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
})

client.interceptors.request.use((cfg) => {
  const key = localStorage.getItem('api_key')
  if (key) {
    cfg.headers['X-API-Key'] = key
  }
  return cfg
})

export default client
