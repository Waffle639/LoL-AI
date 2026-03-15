import { Navigate, Outlet } from 'react-router-dom'

export default function AuthGuard() {
  const apiKey = localStorage.getItem('api_key')
  if (!apiKey) return <Navigate to="/login" replace />
  return <Outlet />
}
