import { useEffect, useRef } from 'react'
import anime from 'animejs'
import styles from './DonutChart.module.css'

// ─────────────────────────────────────────────────────────────────
// DonutChart
// SVG donut with anime.js stroke-dash draw animation on mount
//
// segments: [{ value, color, label }]
// ─────────────────────────────────────────────────────────────────

const R      = 48
const CX     = 60
const CY     = 60
const CIRCUM = 2 * Math.PI * R

function calcSegments(segments) {
  const total  = segments.reduce((s, seg) => s + seg.value, 0)
  let offset   = 0
  return segments.map(seg => {
    const dash   = (seg.value / total) * CIRCUM
    const gap    = CIRCUM - dash
    const result = { ...seg, dash, gap, offset }
    offset      += dash
    return result
  })
}

export default function DonutChart({ segments, center }) {
  const computed = calcSegments(segments)

  // Animate on mount
  useEffect(() => {
    const timer = setTimeout(() => {
      computed.forEach((_, i) => {
        anime({
          targets: `#donut-seg-${i}`,
          strokeDashoffset: [anime.setDashoffset, el => el.getAttribute('data-offset')],
          duration: 900 + i * 100,
          easing: 'easeOutCubic',
        })
      })
    }, 50)
    return () => clearTimeout(timer)
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [])

  return (
    <div className={styles.wrap}>
      <div className={styles.donut}>
        <svg width="120" height="120" viewBox="0 0 120 120">
          {/* Track */}
          <circle cx={CX} cy={CY} r={R} fill="none" stroke="#101e35" strokeWidth="14" />
          {/* Segments */}
          {computed.map((seg, i) => (
            <circle
              key={i}
              id={`donut-seg-${i}`}
              cx={CX}
              cy={CY}
              r={R}
              fill="none"
              stroke={seg.color}
              strokeWidth="14"
              strokeDasharray={`${seg.dash} ${seg.gap}`}
              strokeDashoffset={-(seg.offset - CIRCUM / 4)}
              data-offset={-(seg.offset - CIRCUM / 4)}
              strokeLinecap="butt"
              transform={`rotate(-90 ${CX} ${CY})`}
            />
          ))}
        </svg>

        {/* Center label */}
        {center && (
          <div className={styles.center}>
            <div className={styles.centerVal}>{center.value}</div>
            <div className={styles.centerLabel}>{center.label}</div>
          </div>
        )}
      </div>

      {/* Legend */}
      <div className={styles.legend}>
        {segments.map((seg, i) => (
          <div key={i} className={styles.legendRow}>
            <span className={styles.dot} style={{ background: seg.color }} />
            <span className={styles.legendLabel}>{seg.label}</span>
            <span className={styles.legendVal} style={{ color: seg.color }}>{seg.value}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
