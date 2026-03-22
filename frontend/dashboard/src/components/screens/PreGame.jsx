import { useState, useEffect, useRef } from 'react'
import anime from 'animejs'
import Topbar from '@/components/layout/Topbar'
import { CHAMPIONS, TEAM_BLUE, TEAM_RED } from '@/constants/champions'
import styles from './PreGame.module.css'

// ─────────────────────────────────────────────────────────────────
// PreGame  —  POST /predict/pregame
// Champion select UI · Random Forest · Accuracy 76.75%
// ─────────────────────────────────────────────────────────────────

const ROLES = ['ALL', 'TOP', 'JNG', 'MID', 'BOT', 'SUP']

export default function PreGame() {
  const [filter, setFilter] = useState('ALL')
  const [search, setSearch] = useState('')
  const [timer, setTimer]   = useState(25)
  const intervalRef = useRef(null)

  useEffect(() => {
    anime({ targets: '.team-panel', opacity:[0,1], translateX:(el,i)=>[i===0?-28:28,0], delay: anime.stagger(80), duration:560, easing:'easeOutExpo' })
    anime({ targets: '.p-slot',     opacity:[0,1], translateY:[10,0], delay: anime.stagger(70,{start:180}), duration:380, easing:'easeOutExpo' })
    anime({ targets: '.cc',         opacity:[0,1], scale:[.88,1], delay: anime.stagger(16,{from:'center'}), duration:280, easing:'easeOutBack' })
    anime({ targets: '.f-role',     opacity:[0,1], translateY:[-6,0], delay: anime.stagger(35), duration:300, easing:'easeOutExpo' })

    // Live countdown
    intervalRef.current = setInterval(() => {
      setTimer(t => {
        const next = t - 1
        if (next <= 0) { clearInterval(intervalRef.current); return 0 }
        return next
      })
    }, 1000)
    return () => clearInterval(intervalRef.current)
  }, [])

  const champList = CHAMPIONS.filter(c =>
    (filter === 'ALL' || true) &&
    c.id.toLowerCase().includes(search.toLowerCase())
  )

  const timerColor = timer <= 10 ? 'var(--red)' : 'var(--teal)'
  const timerCircum = 2 * Math.PI * 20
  const timerDash   = (timer / 25) * timerCircum

  return (
    <div>
      {/* ─ Topbar with title in center ─ */}
      <Topbar>
        <div className={styles.pickerTitle}>
          <div className={styles.pickerName}>PICK YOUR CHAMPION</div>
          <div className={styles.pickerSub}>Pre-Game Prediction · Random Forest</div>
        </div>
      </Topbar>

      <div className={styles.layout}>

        {/* ── Blue team ── */}
        <div className={`${styles.teamPanel} team-panel`}>
          <div className={styles.teamHeader}>
            <span className={`${styles.dot} ${styles.blue}`} />
            G2 ESPORTS
            <span className={styles.side}>BLUE</span>
          </div>

          {TEAM_BLUE.map((p, i) => (
            <div key={i} className={`${styles.slot} p-slot ${p.picking ? styles.picking : ''}`}>
              <div className={styles.portrait}>
                <svg viewBox="0 0 24 24" fill="var(--txt-d)" opacity=".3">
                  <path d="M12 2l3 7h7l-5.5 4 2 7L12 16l-6.5 4 2-7L2 9h7z"/>
                </svg>
              </div>
              <div className={styles.slotInfo}>
                <div className={styles.slotPos}>{p.position}</div>
                <div className={styles.slotPlayer}>{p.player}</div>
                <div className={`${styles.slotChamp} ${p.picking ? styles.blinking : ''}`}>
                  {p.picking ? 'Picking...' : p.champion}
                </div>
              </div>
            </div>
          ))}

          <div className={styles.probArea}>
            <div className={styles.probLabel}>WIN PROBABILITY</div>
            <div className={styles.probVal} style={{ color: 'var(--teal)' }}>77.82%</div>
            <div className={styles.probBar}><div className={styles.probFill} style={{ width: '77.82%', background: 'linear-gradient(90deg,var(--teal),rgba(10,200,185,.3))' }} /></div>
          </div>
        </div>

        {/* ── Center: champion grid ── */}
        <div className={styles.center}>
          {/* Filters */}
          <div className={styles.filterRow}>
            {ROLES.map(r => (
              <button key={r} className={`${styles.roleBtn} f-role ${filter === r ? styles.roleBtnActive : ''}`} onClick={() => setFilter(r)}>{r}</button>
            ))}
            <input className={styles.search} placeholder="Search champion..." value={search} onChange={e => setSearch(e.target.value)} />
          </div>

          {/* Grid */}
          <div className={styles.grid}>
            {champList.map(c => (
              <div key={c.id} className={`${styles.champCell} cc ${c.picked ? styles.picked : ''}`}>
                <div className={styles.champBg} style={{ background: c.bg }} />
                <div className={styles.champName}>{c.id}</div>
              </div>
            ))}
          </div>

          {/* Bottom bar */}
          <div className={styles.bottomBar}>
            <span className={styles.pickingInfo}>BrokenBlade is picking — Blue side</span>
            {/* Timer */}
            <div className={styles.timerRing}>
              <svg width="48" height="48">
                <circle cx="24" cy="24" r="20" fill="none" stroke="#101e35" strokeWidth="4" />
                <circle cx="24" cy="24" r="20" fill="none" stroke={timerColor} strokeWidth="4"
                  strokeDasharray={`${timerDash} ${timerCircum}`} strokeDashoffset={timerCircum / 4}
                  strokeLinecap="round" transform="rotate(-90 24 24)"
                  style={{ transition: 'stroke-dasharray .3s, stroke .3s' }} />
              </svg>
              <span className={styles.timerNum} style={{ color: timerColor }}>{timer}</span>
            </div>
          </div>

          <div className={styles.lockWrap}>
            <button className={styles.lockBtn}>Lock In &amp; Predict</button>
          </div>
        </div>

        {/* ── Red team ── */}
        <div className={`${styles.teamPanel} ${styles.teamRight} team-panel`}>
          <div className={styles.teamHeader}>
            <span className={`${styles.dot} ${styles.red}`} />
            MAD LIONS
            <span className={styles.side}>RED</span>
          </div>

          {TEAM_RED.map((p, i) => (
            <div key={i} className={`${styles.slot} ${styles.slotRight} p-slot ${p.picking ? styles.pickingEnemy : ''}`}>
              <div className={styles.slotInfo} style={{ textAlign: 'right' }}>
                <div className={styles.slotPos}>{p.position}</div>
                <div className={styles.slotPlayer}>{p.player}</div>
                <div className={`${styles.slotChamp} ${p.picking ? styles.blinkingRed : ''}`}>
                  {p.picking ? 'Picking...' : p.champion}
                </div>
              </div>
              <div className={styles.portrait}>
                <svg viewBox="0 0 24 24" fill="var(--txt-d)" opacity=".3">
                  <path d="M12 2l3 7h7l-5.5 4 2 7L12 16l-6.5 4 2-7L2 9h7z"/>
                </svg>
              </div>
            </div>
          ))}

          <div className={styles.probArea}>
            <div className={styles.probLabel}>WIN PROBABILITY</div>
            <div className={styles.probVal} style={{ color: 'var(--red)' }}>22.18%</div>
            <div className={styles.probBar}><div className={styles.probFill} style={{ width: '22.18%', background: 'linear-gradient(90deg,var(--red),rgba(200,48,32,.3))' }} /></div>
          </div>
        </div>

      </div>
    </div>
  )
}
