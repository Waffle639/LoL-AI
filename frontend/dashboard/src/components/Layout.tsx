import { Outlet } from 'react-router-dom'

export default function Layout() {
  return (
    <div>
      <header>Header</header>
      <aside>Sidebar</aside>
      <main>
        <Outlet />
      </main>
    </div>
  )
}
