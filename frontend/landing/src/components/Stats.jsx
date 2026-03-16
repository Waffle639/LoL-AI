import { useEffect, useRef } from 'react'
import { STATS } from '../data/content'
import { useScrollReveal, useCountUp } from '../hooks'

function StatBlock({ stat }) {
  const { ref, visible } = useScrollReveal(0.3)
  const { value, start } = useCountUp(stat.target, stat.decimals)

  useEffect(() => {
    if (visible) start()
  }, [visible, start])

  return (
    <div
      ref={ref}
      className="relative text-center px-5 py-9"
      style={{
        background: '#020915',
        opacity: visible ? 1 : 0,
        transform: visible ? 'translateY(0)' : 'translateY(16px)',
        transition: 'opacity 0.46s ease, transform 0.46s ease',
      }}
    >
      <div
        className="absolute top-0 left-0 right-0 h-0.5"
        style={{ background: 'linear-gradient(90deg, #7a5f38, transparent)' }}
      />

      <p
        className="font-cinzel font-bold text-gold leading-none"
        style={{
          fontSize: 'clamp(28px, 5vw, 52px)',
          textShadow: '0 0 20px rgba(200,169,110,0.1)',
        }}
      >
        {value}{stat.suffix}
      </p>
      <p className="font-mono text-[8px] tracking-widest uppercase mt-1.5 mb-1"
         style={{ color: '#3a4560' }}>
        {stat.label}
      </p>
      <p className="font-exo text-[11px] font-light" style={{ color: '#3a4560' }}>
        {stat.sub}
      </p>
    </div>
  )
}

export default function Stats() {
  const { ref, visible } = useScrollReveal(0.1)

  return (
    <section
      id="stats"
      ref={ref}
      className="relative overflow-hidden px-13 py-22"
      style={{
        padding: '88px 52px',
        background: '#060f1e',
        borderTop: '1px solid rgba(200,169,110,0.14)',
      }}
    >
      <div
        className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2
                   font-cinzel font-black pointer-events-none select-none whitespace-nowrap"
        style={{
          fontSize: '200px',
          color: 'transparent',
          WebkitTextStroke: '1px rgba(200,169,110,0.02)',
          letterSpacing: '-0.05em',
        }}
      >
        97.76%
      </div>

      <div
        className="relative z-10 text-center mb-14"
        style={{
          opacity: visible ? 1 : 0,
          transform: visible ? 'translateY(0)' : 'translateY(20px)',
          transition: 'opacity 0.66s ease, transform 0.66s ease',
        }}
      >
        <p className="font-mono text-[9px] tracking-widest text-teal uppercase mb-2">
          By the numbers
        </p>
        <h2
          className="font-cinzel font-bold text-gold uppercase tracking-wide"
          style={{ fontSize: 'clamp(22px, 4vw, 44px)' }}
        >
          Built on{' '}
          <em className="text-stroke-gold not-italic">real</em>{' '}
          data
        </h2>
      </div>

      <div
        className="relative z-10 grid grid-cols-4 gap-0.5 max-w-[1040px] mx-auto"
        style={{ gap: '2px' }}
      >
        {STATS.map(stat => (
          <StatBlock key={stat.id} stat={stat} />
        ))}
      </div>
    </section>
  )
}