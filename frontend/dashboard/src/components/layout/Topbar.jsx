import { useApp } from '@/context/AppContext'
import Logo from '@/components/ui/Logo'
import styles from './Topbar.module.css'

// ─────────────────────────────────────────────────────────────────
// Topbar
// Shared app topbar: logo + credits chip + avatar
// ─────────────────────────────────────────────────────────────────

export default function Topbar({ children }) {
  const { credits, user } = useApp()

  return (
    <header className={styles.topbar}>
      <div className={styles.left}>
        <Logo />
      </div>

      {/* Optional center slot (e.g. picker title) */}
      {children && <div className={styles.center}>{children}</div>}

      <div className={styles.right}>
        <div className={styles.credits}>
          <div className={styles.creditsNum}>{credits}</div>
          <div className={styles.creditsLabel}>CREDITS</div>
        </div>
        <div className={styles.avatar}>{user.initial}</div>
      </div>
    </header>
  )
}
