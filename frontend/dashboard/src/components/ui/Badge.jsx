import styles from './Badge.module.css'

// ─────────────────────────────────────────────────────────────────
// Badge
// variant: 'gold' | 'teal' | 'green' | 'red'
// ─────────────────────────────────────────────────────────────────

export default function Badge({ children, variant = 'gold' }) {
  return (
    <span className={`${styles.badge} ${styles[variant]}`}>
      {children}
    </span>
  )
}
