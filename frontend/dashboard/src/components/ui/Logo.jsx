import styles from './Logo.module.css'

// ─────────────────────────────────────────────────────────────────
// Logo
// Tries to load lol-esports-logo.png from public/.
// Falls back to the hextech SVG if missing.
// ─────────────────────────────────────────────────────────────────

export default function Logo({ size = 'md' }) {
  return (
    <div className={`${styles.logo} ${styles[size]}`}>
      <div className={styles.mark}>
        <img
          src="/lol-esports-logo.png"
          alt="LoL-AI"
          className={styles.img}
          onError={e => {
            e.currentTarget.style.display = 'none'
            e.currentTarget.nextElementSibling.style.display = 'flex'
          }}
        />
        {/* Fallback hextech SVG */}
        <div className={styles.fallback} style={{ display: 'none' }}>
          <svg viewBox="0 0 40 40" width="26" height="26">
            <polygon
              points="20,2 38,11 38,29 20,38 2,29 2,11"
              fill="#020d1a" stroke="#1a78c2" strokeWidth="1.5"
            />
            <polygon
              points="20,7 33,14 33,26 20,33 7,26 7,14"
              fill="none" stroke="#0a3a6a" strokeWidth=".5"
            />
            <text
              x="20" y="24" textAnchor="middle"
              fontFamily="Georgia,serif" fontSize="10"
              fontWeight="900" fill="#1a78c2"
            >AI</text>
          </svg>
        </div>
      </div>

      <div className={styles.text}>
        <div className={styles.name}>LOL-AI</div>
        <div className={styles.sub}>PREDICTION ENGINE</div>
      </div>
    </div>
  )
}
