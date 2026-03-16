import { useState } from 'react'
import { PLAYERS } from '../data/content'
import { useScrollReveal } from '../hooks'

const IMAGE_PATHS = {
  faker:  '/images/faker.jpg',
  caps:   '/images/caps.jpg',
  zeus:   '/images/zeus.jpg', 
  elyoya: '/images/elYoya.jpg',  
  bin:    '/images/bin.jpg', 
}

export default function Players() {
  const [active, setActive] = useState(0)
  const [locked, setLocked] = useState(0)
  const { ref, visible } = useScrollReveal(0.08)

  const handleEnter = (idx) => {
    setActive(idx)
    setLocked(idx)
  }
  const handleLeave = () => {
    setActive(locked)
  }

  return (
    <section
      id="players"
      ref={ref}
      className="relative h-screen flex overflow-hidden"
      style={{
        borderTop: '1px solid rgba(200,169,110,0.14)',
        opacity: visible ? 1 : 0,
        transform: visible ? 'translateY(0)' : 'translateY(20px)',
        transition: 'opacity 0.66s ease, transform 0.66s ease',
      }}
    >
      <div
        className="relative z-10 flex flex-col justify-center"
        style={{
          width: '35%',
          flexShrink: 0,
          padding: '0 52px',
          background: 'linear-gradient(90deg, rgba(2,9,21,0.97) 72%, rgba(2,9,21,0) 100%)',
        }}
      >
        <div className="mb-7">
          <p className="font-mono text-[9px] tracking-widest text-teal uppercase mb-2">
            Pro Players
          </p>
          <h2
            className="font-cinzel font-bold text-gold uppercase leading-[1.05]"
            style={{ fontSize: 'clamp(20px, 2.6vw, 34px)' }}
          >
            The best.<br />
            <span className="text-stroke-gold-dim">Tracked.</span>
          </h2>
        </div>

        {PLAYERS.map((p, i) => {
          const isActive = active === i
          return (
            <div
              key={p.id}
              data-cursor-hover
              onMouseEnter={() => handleEnter(i)}
              onMouseLeave={handleLeave}
              className="relative flex items-baseline gap-3 py-4 transition-all duration-200"
              style={{
                borderBottom: '1px solid rgba(200,169,110,0.05)',
                borderTop: i === 0 ? '1px solid rgba(200,169,110,0.05)' : 'none',
                paddingLeft: isActive ? '13px' : '0',
              }}
            >
              <div
                className="absolute left-0 top-0 bottom-0 w-0.5 transition-transform duration-200 origin-center"
                style={{
                  background: '#C8A96E',
                  transform: isActive ? 'scaleY(1)' : 'scaleY(0)',
                }}
              />

              <span
                className="font-mono text-[9px] w-5 flex-shrink-0 transition-colors duration-200"
                style={{ color: isActive ? 'rgba(200,169,110,0.35)' : '#3a4560' }}
              >
                0{p.id + 1}
              </span>

              <span
                className="font-cinzel font-bold tracking-wide transition-colors duration-200"
                style={{
                  fontSize: 'clamp(18px, 2.3vw, 30px)',
                  color: isActive ? '#C8A96E' : '#8a95b0',
                }}
              >
                {p.name}
              </span>

              <span
                className="font-mono text-[8px] tracking-widest uppercase transition-colors duration-200"
                style={{ color: isActive ? '#0AC8B9' : '#3a4560' }}
              >
                {p.role.split(' ')[0]}
              </span>

              <span
                className="font-exo text-[11px] font-light ml-auto transition-colors duration-200"
                style={{ color: isActive ? '#8a95b0' : '#3a4560' }}
              >
                {p.team.split(' · ')[0]}
              </span>
            </div>
          )
        })}
      </div>

      <div className="flex-1 relative overflow-hidden">
        {PLAYERS.map((p, i) => {
          const isVisible = active === i

          return (
            <div
              key={p.id}
              className="absolute inset-0 player-photo"
              style={{ opacity: isVisible ? 1 : 0 }}
            >
              <img
                src={IMAGE_PATHS[p.imageKey]}
                alt={p.name}
                className="w-full h-full object-cover object-top"
              />

              <div
                className="absolute inset-0"
                style={{
                  background: `
                    linear-gradient(270deg, rgba(2,9,21,0) 38%, rgba(2,9,21,0.9) 100%),
                    linear-gradient(180deg, rgba(2,9,21,.2) 0%, transparent 22%, transparent 52%, rgba(2,9,21,.88) 100%)
                  `,
                }}
              />

              <div
                className="absolute bottom-11 right-12 z-[5] flex flex-col gap-1.5 items-end player-stats-overlay"
                style={{
                  opacity: isVisible ? 1 : 0,
                  transform: isVisible ? 'translateY(0)' : 'translateY(8px)',
                }}
              >
                <h3
                  className="font-cinzel font-black text-gold text-right"
                  style={{
                    fontSize: 'clamp(26px, 4vw, 50px)',
                    textShadow: '0 2px 20px rgba(0,0,0,0.95)',
                  }}
                >
                  {p.name}
                </h3>
                <p className="font-mono text-[9px] tracking-widest text-teal uppercase text-right mt-0.5">
                  {p.role} &nbsp;·&nbsp; {p.team}
                </p>

                <div className="flex gap-1.5 mt-2.5">
                  {[
                    { label: 'Win Rate', value: p.winRate, color: '#0AC8B9' },
                    { label: 'KDA',      value: p.kda,     color: '#C8A96E' },
                    { label: 'Games',    value: p.games,   color: '#C8D0E0' },
                  ].map(stat => (
                    <div
                      key={stat.label}
                      className="text-center min-w-[62px] px-3 py-2"
                      style={{
                        background: 'rgba(6,15,30,0.82)',
                        border: '1px solid rgba(200,169,110,0.14)',
                        backdropFilter: 'blur(4px)',
                      }}
                    >
                      <p className="font-mono text-[7px] tracking-widest uppercase mb-0.5"
                         style={{ color: '#3a4560' }}>
                        {stat.label}
                      </p>
                      <p className="font-cinzel text-[14px] font-bold" style={{ color: stat.color }}>
                        {stat.value}
                      </p>
                    </div>
                  ))}
                </div>

                <div className="flex gap-1 mt-1.5 justify-end">
                  {p.champions.map(c => (
                    <span
                      key={c}
                      className="font-mono text-[8px] px-2 py-1"
                      style={{
                        color: '#7a5f38',
                        background: 'rgba(200,169,110,0.07)',
                        border: '1px solid rgba(200,169,110,0.13)',
                      }}
                    >
                      {c}
                    </span>
                  ))}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </section>
  )
}