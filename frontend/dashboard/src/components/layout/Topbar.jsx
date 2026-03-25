import { useEffect, useRef, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useApp } from '@/context/AppContext'
import Logo from '@/components/ui/Logo'
import { ROUTES } from '@/constants/navigation'
import styles from './Topbar.module.css'

// ─────────────────────────────────────────────────────────────────
// Topbar
// Shared app topbar: logo + credits chip + avatar
// ─────────────────────────────────────────────────────────────────

export default function Topbar({ children }) {
  const { credits, user, logout } = useApp()
  const navigate = useNavigate()
  const [menuOpen, setMenuOpen] = useState(false)
  const menuRef = useRef(null)

  useEffect(() => {
    const handleOutsideClick = event => {
      if (menuRef.current && !menuRef.current.contains(event.target)) {
        setMenuOpen(false)
      }
    }

    const handleEscape = event => {
      if (event.key === 'Escape') setMenuOpen(false)
    }

    document.addEventListener('mousedown', handleOutsideClick)
    document.addEventListener('keydown', handleEscape)
    return () => {
      document.removeEventListener('mousedown', handleOutsideClick)
      document.removeEventListener('keydown', handleEscape)
    }
  }, [])

  const handleLogoClick = () => {
    navigate(ROUTES.DASHBOARD)
  }

  const handleLogout = () => {
    setMenuOpen(false)
    logout()
    navigate(ROUTES.LOGIN, { replace: true })
  }

  return (
    <header className={styles.topbar}>
      <div className={styles.left}>
        <button
          className={styles.logoButton}
          type="button"
          onClick={handleLogoClick}
          aria-label="Go to dashboard"
        >
          <Logo />
        </button>
      </div>

      {/* Optional center slot (e.g. picker title) */}
      {children && <div className={styles.center}>{children}</div>}

      <div className={styles.right}>
        <div className={styles.credits}>
          <div className={styles.creditsNum}>{credits}</div>
          <div className={styles.creditsLabel}>CREDITS</div>
        </div>
        <div className={styles.userMenu} ref={menuRef}>
          <button
            className={styles.avatarButton}
            type="button"
            aria-label="Open account menu"
            aria-expanded={menuOpen}
            onClick={() => setMenuOpen(current => !current)}
          >
            <div className={styles.avatar}>{user.initial}</div>
          </button>

          {menuOpen && (
            <div className={styles.menuCard}>
              <button
                className={styles.logoutButton}
                type="button"
                onClick={handleLogout}
              >
                Logout
              </button>
            </div>
          )}
        </div>
      </div>
    </header>
  )
}
