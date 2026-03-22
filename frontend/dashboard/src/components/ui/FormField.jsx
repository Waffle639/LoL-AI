import styles from './FormField.module.css'

// ─────────────────────────────────────────────────────────────────
// FormField
// Riot-style: label above, thin bottom-border input
// variant: 'default' | 'riot' (bottom-border only)
// ─────────────────────────────────────────────────────────────────

export default function FormField({
  label,
  type = 'text',
  value,
  onChange,
  placeholder,
  variant = 'default',
}) {
  return (
    <div className={`${styles.group} ${styles[variant]}`}>
      {label && <label className={styles.label}>{label}</label>}
      <input
        type={type}
        value={value}
        onChange={onChange}
        placeholder={placeholder}
        className={styles.input}
      />
    </div>
  )
}
