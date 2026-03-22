import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import anime from 'animejs'
import Logo from '@/components/ui/Logo'
import FormField from '@/components/ui/FormField'
import { ROUTES } from '@/constants/navigation'
import styles from './Login.module.css'
import splashSrc from '@/assets/splash.jpg'

// ─────────────────────────────────────────────────────────────────
// Login
// Riot-inspired split panel: form left, splash art right
// ─────────────────────────────────────────────────────────────────

export default function Login() {
  const navigate = useNavigate()
  const [tab, setTab]           = useState('signin')
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')

  // Entry animations
  useEffect(() => {
    anime({
      targets: '#auth-left > *',
      opacity: [0, 1],
      translateY: [16, 0],
      delay: anime.stagger(70, { start: 100 }),
      duration: 500,
      easing: 'easeOutExpo',
    })
    anime({ targets: '#auth-right', opacity: [0, 1], duration: 900, delay: 200, easing: 'easeOutQuad' })
    // Scan line on right panel
    anime({ targets: '#scan-h', x1: [-800, 800], x2: [0, 1600], duration: 1800, delay: 400, easing: 'easeInOutCubic' })
    // Orb drifts
    anime({ targets: '#orb1', translateY: [0, -18, 0], duration: 7000, loop: true, direction: 'alternate', easing: 'easeInOutSine' })
    anime({ targets: '#orb2', translateY: [0, 12, 0],  duration: 9000, delay: 1200, loop: true, direction: 'alternate', easing: 'easeInOutSine' })
    // Grid lines
    anime({ targets: '.svgl', opacity: [0, 1], delay: anime.stagger(120, { start: 300 }), duration: 600, easing: 'easeOutQuad' })
    // Subtle particles
    const container = document.getElementById('auth-particles')
    if (container && !container.children.length) {
      for (let i = 0; i < 24; i++) {
        const p = document.createElement('div')
        p.style.cssText = `position:absolute;width:${Math.random()*1.5+.5}px;height:${Math.random()*1.5+.5}px;border-radius:50%;background:${Math.random()>.6?'#C8A96E':'#0AC8B9'};left:${Math.random()*100}%;top:${Math.random()*100}%;opacity:0;pointer-events:none;`
        container.appendChild(p)
      }
      anime({ targets: '#auth-particles > div', opacity: [0, () => Math.random() * .12 + .02], duration: () => Math.random() * 1400 + 800, delay: anime.stagger(70, { from: 'random' }), easing: 'easeOutQuad' })
    }
  }, [])

  const handleSubmit = e => {
    e.preventDefault()
    navigate(ROUTES.DASHBOARD)
  }

  return (
    <div className={styles.wrap}>

      {/* ── LEFT: Form ── */}
      <div className={styles.left} id="auth-left">
        <div id="auth-particles" className={styles.particles} />

        <div className={styles.logoMark}><Logo size="lg" /></div>

        <div className={styles.productLabel}>Esports Intelligence Platform</div>
        <div className={styles.title}>Sign in to<br />LoL-AI</div>
        <div className={styles.sub}>Access your prediction dashboard,<br />API keys and credit balance.</div>

        {/* Tabs */}
        <div className={styles.tabs}>
          <button className={`${styles.tab} ${tab === 'signin' ? styles.tabActive : ''}`} onClick={() => setTab('signin')}>Sign in</button>
          <button className={`${styles.tab} ${tab === 'register' ? styles.tabActive : ''}`} onClick={() => setTab('register')}>Create account</button>
        </div>

        <form onSubmit={handleSubmit}>
          <FormField label="Username" variant="riot" value={username} onChange={e => setUsername(e.target.value)} placeholder="Your summoner name" />
          <FormField label="Password" type="password" variant="riot" value={password} onChange={e => setPassword(e.target.value)} placeholder="Your password" />
          <button type="submit" className={styles.submit}>Continue</button>
        </form>

        <div className={styles.footer}>
          <label className={styles.remember}>
            <input type="checkbox" defaultChecked style={{ accentColor: 'var(--gold)' }} />
            <span>Stay signed in</span>
          </label>
          <a className={styles.link}>Forgot password?</a>
        </div>
      </div>

      {/* ── RIGHT: Splash art ── */}
      <div className={styles.right} id="auth-right">
        <div className={styles.rightBg} style={{ backgroundImage: `url(${splashSrc})` }} />
        <div className={styles.overlay} />
        <div className={styles.grid} />

        <div className={styles.orb} id="orb1" style={{ width: 280, height: 280, background: 'rgba(10,200,185,.07)', top: '10%', left: '15%' }} />
        <div className={styles.orb} id="orb2" style={{ width: 220, height: 220, background: 'rgba(200,169,110,.06)', bottom: '18%', right: '10%' }} />

        <svg className={styles.lines} viewBox="0 0 800 600" preserveAspectRatio="none">
          <line className="svgl" x1="0" y1="200" x2="800" y2="200" stroke="rgba(10,200,185,.06)" strokeWidth="1" />
          <line className="svgl" x1="0" y1="400" x2="800" y2="400" stroke="rgba(10,200,185,.04)" strokeWidth="1" />
          <line className="svgl" x1="200" y1="0" x2="200" y2="600" stroke="rgba(200,169,110,.04)" strokeWidth="1" />
          <line className="svgl" x1="600" y1="0" x2="600" y2="600" stroke="rgba(200,169,110,.03)" strokeWidth="1" />
          <line className="svgl" x1="0" y1="600" x2="800" y2="0" stroke="rgba(10,200,185,.035)" strokeWidth="1" strokeDasharray="4 8" />
          <line id="scan-h" x1="-800" y1="300" x2="0" y2="300" stroke="rgba(10,200,185,.15)" strokeWidth="1.5" />
        </svg>
      </div>

    </div>
  )
}
