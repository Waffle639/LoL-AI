import styles from './StatCard.module.css'

// ─────────────────────────────────────────────────────────────────
// StatCard
// color: 'gold' | 'teal' | 'green' | 'red'
// ─────────────────────────────────────────────────────────────────

export default function StatCard({ label, value, trend, trendUp, color = 'gold' }) {
  return (
    <div className={`${styles.card} ${styles[color]}`}>
      <div className={styles.label}>{label}</div>
      <div className={styles.value}>{value}</div>
      {trend && (
        <div className={`${styles.trend} ${trendUp ? styles.up : styles.dn}`}>
          {trend}
        </div>
      )}
    </div>
  )
}
