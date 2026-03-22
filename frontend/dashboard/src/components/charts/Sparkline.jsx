import { useEffect } from 'react'
import anime from 'animejs'
import styles from './Sparkline.module.css'

// ─────────────────────────────────────────────────────────────────
// Sparkline
// Animated SVG line chart. Draws on mount.
// points: number[] — values 0–100
// ─────────────────────────────────────────────────────────────────

const W = 400
const H = 92
const PAD_L = 32
const PAD_B = 8

function buildPath(points) {
  const xStep = (W - PAD_L) / (points.length - 1)
  return points.map((v, i) => {
    const x = PAD_L + i * xStep
    const y = H - PAD_B - ((v / 100) * (H - PAD_B - 8))
    return `${i === 0 ? 'M' : 'L'}${x},${y}`
  }).join(' ')
}

function buildArea(points) {
  return buildPath(points) + ` L${W},${H} L${PAD_L},${H} Z`
}

// color per point: red if low, gold if mid, teal if high
function dotColor(v) {
  if (v < 45) return '#C83020'
  if (v < 65) return '#C8A96E'
  return '#0AC8B9'
}

const POINTS    = [75, 89, 68, 85, 38, 72, 61, 81, 50, 85, 71, 90, 65, 79]
const LINE_LEN  = 700

export default function Sparkline() {
  useEffect(() => {
    const t = setTimeout(() => {
      anime({ targets: '#spark-line', strokeDashoffset: [LINE_LEN, 0], duration: 1050, easing: 'easeInOutCubic' })
      anime({ targets: '#spark-area', opacity: [0, 1], duration: 550, delay: 1400, easing: 'easeOutQuad' })
      anime({ targets: '.sp-dot', opacity: [0, 1], scale: [0, 1], delay: anime.stagger(60, { start: 1050 }), duration: 230, easing: 'easeOutBack' })
      anime({ targets: '#sp-ring', opacity: [0, 0.55, 0], scale: [0.6, 1.4], duration: 1400, delay: 2000, loop: true, easing: 'easeInOutSine' })
    }, 50)
    return () => clearTimeout(t)
  }, [])

  const xStep = (W - PAD_L) / (POINTS.length - 1)
  const yOf   = v => H - PAD_B - ((v / 100) * (H - PAD_B - 8))

  return (
    <div className={styles.wrap}>
      <svg id="spark-svg" viewBox={`0 0 ${W} ${H}`} width="100%" height={H} overflow="visible">
        {/* Grid */}
        {[8, H / 2, H - PAD_B].map((y, i) => (
          <line key={i} x1={PAD_L} y1={y} x2={W} y2={y} stroke="#101e35" strokeWidth="1" />
        ))}
        {/* Y labels */}
        <text x="0" y="12"       fontFamily="Share Tech Mono,monospace" fontSize="8" fill="#5a6580">100%</text>
        <text x="0" y={H / 2 + 4} fontFamily="Share Tech Mono,monospace" fontSize="8" fill="#5a6580">50%</text>
        <text x="0" y={H + 2}   fontFamily="Share Tech Mono,monospace" fontSize="8" fill="#5a6580">0%</text>

        <defs>
          <linearGradient id="sg" x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%"   stopColor="#0AC8B9" stopOpacity=".16" />
            <stop offset="100%" stopColor="#0AC8B9" stopOpacity="0"   />
          </linearGradient>
        </defs>

        {/* Area fill */}
        <path id="spark-area" d={buildArea(POINTS)} fill="url(#sg)" opacity="0" />

        {/* Line */}
        <path
          id="spark-line"
          d={buildPath(POINTS)}
          fill="none"
          stroke="#0AC8B9"
          strokeWidth="1.6"
          strokeDasharray={LINE_LEN}
          strokeDashoffset={LINE_LEN}
        />

        {/* Dots */}
        {POINTS.map((v, i) => {
          const x = PAD_L + i * xStep
          const y = yOf(v)
          const isLast = i === POINTS.length - 1
          return (
            <g key={i}>
              <circle
                className="sp-dot"
                cx={x} cy={y} r="3"
                fill={isLast ? dotColor(v) : '#020915'}
                stroke={dotColor(v)}
                strokeWidth="1.4"
                opacity="0"
              />
              {isLast && (
                <circle id="sp-ring" cx={x} cy={y} r="6" fill="none" stroke="#0AC8B9" strokeWidth="1" opacity="0" />
              )}
            </g>
          )
        })}
      </svg>

      <div className={styles.xLabels}>
        <span>MAR 03</span><span>MAR 07</span><span>MAR 11</span><span>MAR 16</span>
      </div>
    </div>
  )
}
