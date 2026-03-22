import Topbar from './Topbar'
import Sidebar from './Sidebar'
import styles from './AppLayout.module.css'

// ─────────────────────────────────────────────────────────────────
// AppLayout
// Wraps every authenticated screen:
//   <Topbar> / <Sidebar> + <main content>
// ─────────────────────────────────────────────────────────────────

export default function AppLayout({ children, topbarCenter }) {
  return (
    <div className={styles.app}>
      <Topbar>{topbarCenter}</Topbar>
      <div className={styles.body}>
        <Sidebar />
        <main className={styles.content}>
          {children}
        </main>
      </div>
    </div>
  )
}
