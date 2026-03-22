import styles from './Button.module.css'

// ─────────────────────────────────────────────────────────────────
// Button
// variant: 'gold' | 'ghost' | 'red'
// size:    'md' | 'sm'
// ─────────────────────────────────────────────────────────────────

export default function Button({
  children,
  variant = 'gold',
  size = 'md',
  fullWidth = false,
  onClick,
  type = 'button',
  disabled = false,
}) {
  return (
    <button
      type={type}
      disabled={disabled}
      onClick={onClick}
      className={[
        styles.btn,
        styles[variant],
        styles[size],
        fullWidth ? styles.full : '',
      ].join(' ')}
    >
      {children}
    </button>
  )
}
