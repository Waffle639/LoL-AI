import styles from './Panel.module.css'

// ─────────────────────────────────────────────────────────────────
// Panel
// accent: 'gold' | 'teal' | 'none'
// ─────────────────────────────────────────────────────────────────

export default function Panel({ children, accent = 'none', className = '', style }) {
  return (
    <div
      className={[styles.panel, styles[`accent-${accent}`], className].join(' ')}
      style={style}
    >
      {children}
    </div>
  )
}

export function PanelTitle({ children }) {
  return <div className={styles.title}>{children}</div>
}
