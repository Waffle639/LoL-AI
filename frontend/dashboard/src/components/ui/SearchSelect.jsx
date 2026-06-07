import { useMemo, useRef, useState, useEffect } from 'react'
import styles from './SearchSelect.module.css'

export default function SearchSelect({
  label,
  value,
  onChange,
  options = [],
  placeholder,
  iconResolver,
  emptyText = 'No matches',
  name,
  required = false,
  invalid = false,
}) {
  const [open, setOpen] = useState(false)
  const [query, setQuery] = useState(value || '')
  const blurTimer = useRef(null)

  useEffect(() => {
    setQuery(value || '')
  }, [value])

  const normalizedOptions = useMemo(() => {
    return options.map((option) => {
      if (typeof option === 'string') {
        return { value: option, label: option }
      }
      return {
        value: option.value ?? option.label,
        label: option.label ?? option.value,
      }
    })
  }, [options])

  const filtered = useMemo(() => {
    const needle = query.trim().toLowerCase()
    if (!needle) return normalizedOptions.slice(0, 12)
    return normalizedOptions
      .filter(option => option.label.toLowerCase().includes(needle))
      .slice(0, 12)
  }, [normalizedOptions, query])

  const handleInput = (event) => {
    const next = event.target.value
    setQuery(next)
    onChange?.(next)
    setOpen(true)
  }

  const handleFocus = () => {
    if (blurTimer.current) {
      clearTimeout(blurTimer.current)
      blurTimer.current = null
    }
    setOpen(true)
  }

  const handleBlur = () => {
    blurTimer.current = setTimeout(() => setOpen(false), 120)
  }

  const handleSelect = (option) => {
    onChange?.(option.value)
    setOpen(false)
  }

  const iconUrl = iconResolver ? iconResolver(value) : ''
  const showIcon = Boolean(iconResolver && iconUrl)

  return (
    <div className={styles.wrap}>
      {label ? <label className={styles.label}>{label}</label> : null}
      <div className={styles.inputWrap}>
        {showIcon ? (
          <img
            src={iconUrl}
            alt=""
            className={styles.icon}
            onError={(event) => {
              event.currentTarget.style.display = 'none'
            }}
          />
        ) : null}
        <input
          className={`${styles.input} ${showIcon ? styles.inputIcon : ''} ${invalid ? styles.inputError : ''}`.trim()}
          value={query}
          onChange={handleInput}
          onFocus={handleFocus}
          onBlur={handleBlur}
          placeholder={placeholder}
          name={name}
          required={required}
          aria-invalid={invalid}
          autoComplete="off"
        />
      </div>

      {open ? (
        <div className={styles.menu}>
          {filtered.length ? (
            filtered.map(option => (
              <button
                key={option.value}
                type="button"
                className={styles.menuItem}
                onMouseDown={() => handleSelect(option)}
              >
                {iconResolver ? (
                  <img
                    src={iconResolver(option.value)}
                    alt=""
                    className={styles.menuIcon}
                    onError={(event) => {
                      event.currentTarget.style.display = 'none'
                    }}
                  />
                ) : null}
                <span className={styles.menuLabel}>{option.label}</span>
              </button>
            ))
          ) : (
            <div className={styles.empty}>{emptyText}</div>
          )}
        </div>
      ) : null}
    </div>
  )
}
