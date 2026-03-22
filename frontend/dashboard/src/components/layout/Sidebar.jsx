import { useLocation, useNavigate } from 'react-router-dom'
import { useSidebar } from '@/hooks/useSidebar'
import { NAV_ITEMS } from '@/constants/navigation'
import styles from './Sidebar.module.css'

// ─────────────────────────────────────────────────────────────────
// Sidebar
// Collapsible nav with icons + labels + tooltips
// ─────────────────────────────────────────────────────────────────

export default function Sidebar() {
  const { pathname } = useLocation()
  const navigate = useNavigate()
  const { sidebarOpen, toggle } = useSidebar()

  // Group items by section
  const sections = NAV_ITEMS.reduce((acc, item) => {
    if (!acc[item.section]) acc[item.section] = []
    acc[item.section].push(item)
    return acc
  }, {})

  return (
    <aside className={`${styles.sidebar} sidebar ${sidebarOpen ? '' : 'col'}`}>
      <div className={styles.inner}>
        {Object.entries(sections).map(([section, items], si) => (
          <div key={section}>
            {si > 0 && <div className={styles.gap} />}
            <div className={`${styles.section} sb-sec`}>{section}</div>
            {items.map(item => {
              const isActive = pathname === item.route
              return (
                <div
                  key={item.route}
                  className={`${styles.item} sb-item ${isActive ? `${styles.active} active` : ''}`}
                  onClick={() => navigate(item.route)}
                >
                  <div className={`${styles.ico} ico`}>
                    <svg viewBox="0 0 24 24" fill="currentColor">
                      <item.icon />
                    </svg>
                  </div>
                  <span className={`${styles.label} lbl`}>{item.label}</span>
                  <span className={`${styles.tooltip} tip`}>{item.label}</span>
                </div>
              )
            })}
          </div>
        ))}
      </div>

      {/* Collapse toggle */}
      <button className={styles.toggle} onClick={toggle} aria-label="Toggle sidebar">
        <svg viewBox="0 0 24 24" fill="none">
          <path
            d="M15 18l-6-6 6-6"
            stroke="#7a5f38"
            strokeWidth="1.5"
            strokeLinecap="round"
            strokeLinejoin="round"
          />
        </svg>
      </button>
    </aside>
  )
}
