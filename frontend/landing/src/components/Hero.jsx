import { useRef } from 'react'
import { useHeroScroll } from '../hooks'
import DraftCanvas from './DraftCanvas'

const STADIUM_IMG = '/images/EstadioRojoyAzul.jpg' 

export default function Hero() {
  const wrapperRef = useRef(null)
  const progress   = useHeroScroll(wrapperRef)

  const draftProgress  = Math.max(0, Math.min(1, (progress - 0.04) / 0.76))
  const textOpacity    = Math.max(0, 1 - (progress / 0.15) * 2)
  const revealProgress = Math.max(0, Math.min(1, (progress - 0.92) / 0.08))

  return (
    <div ref={wrapperRef} style={{ height: '300vh', position: 'relative' }}>
      <div className="sticky top-0 h-screen overflow-hidden">

        <div
          className="absolute inset-0 bg-cover"
          style={{
            backgroundImage: `url(${STADIUM_IMG})`,
            backgroundPosition: 'center 35%',
          }}
        />

        <div
          className="absolute inset-0"
          style={{
            background: `
              linear-gradient(180deg, rgba(2,9,21,.75) 0%, rgba(2,9,21,0) 16%),
              linear-gradient(0deg,   rgba(2,9,21,1) 0%, rgba(2,9,21,.3) 28%, transparent 52%),
              linear-gradient(90deg,  rgba(2,9,21,.82) 0%, rgba(2,9,21,.4) 18%, transparent 32%),
              linear-gradient(270deg, rgba(2,9,21,.82) 0%, rgba(2,9,21,.4) 18%, transparent 32%)
            `,
          }}
        />

        <DraftCanvas progress={draftProgress} />

        <div
          className="absolute inset-0 z-10 pointer-events-none"
          style={{
            display: 'grid',
            gridTemplateColumns: '240px 1fr 240px',
            alignItems: 'center',
            padding: '80px clamp(28px, 4.2vw, 72px) 60px',
            opacity: textOpacity,
          }}
        >
          <div style={{ justifySelf: 'start' }}>
            <div
              className="inline-block font-mono text-[11px] tracking-widest text-teal uppercase mb-5 px-3 py-1"
              style={{ border: '1px solid rgba(10,200,185,0.3)' }}
            >
              Prediction Engine · AI
            </div>
            <h1
              className="font-cinzel font-bold text-gold leading-tight text-shadow-strong"
              style={{ fontSize: 'clamp(32px, 3.8vw, 52px)' }}
            >
              Predict<br />every<br />match.
              <span
                className="block font-cinzel mt-2 text-stroke-gold"
                style={{ fontSize: '0.58em', letterSpacing: '0.5em', textTransform: 'uppercase' }}
              >
                Before it starts
              </span>
            </h1>
            <div
              className="mt-5"
              style={{
                width: '36px', height: '2px',
                background: 'linear-gradient(90deg, #0AC8B9, transparent)',
              }}
            />
          </div>

          <div />

          <div className="flex flex-col items-end pointer-events-auto" style={{ justifySelf: 'end' }}>
            <div
              className="mb-5"
              style={{
                width: '36px', height: '1px',
                background: 'linear-gradient(270deg, #C8A96E, transparent)',
                marginBottom: '20px',
              }}
            />
            <p
              className="font-exo font-light text-[rgba(200,208,224,0.88)] text-right text-shadow-soft mb-6"
              style={{ fontSize: 'clamp(16px, 1.8vw, 20px)', lineHeight: '1.7', maxWidth: '320px' }}
            >
              Real-time win probability for professional League of Legends.
              Neural network + random forest. Two models, one verdict.
            </p>
            <div className="flex flex-col items-end gap-2">
              <a
                href="#pricing"
                className="font-cinzel text-[13px] font-bold tracking-widest text-[#050300] uppercase
                           px-11 py-4 clip-skew no-underline inline-block
                           transition-all hover:brightness-110 hover:-translate-y-0.5"
                style={{ background: 'linear-gradient(135deg, #D4B483, #7a5f38)' }}
                data-cursor-hover
              >
                Enter the Rift
              </a>
              <a
                href="#draft"
                className="font-rajdhani text-[13px] font-bold tracking-widest text-[#C8A96E] uppercase
                           px-8 py-3 clip-skew-sm no-underline inline-block
                           transition-all hover:border-gold-dim hover:text-gold"
                style={{ border: '1px solid rgba(200,169,110,0.38)' }}
                data-cursor-hover
              >
                How it works
              </a>
            </div>
          </div>
        </div>

        <div
          className="absolute inset-0 z-[12] flex flex-col items-center justify-end pointer-events-none"
          style={{ paddingBottom: '44px', opacity: revealProgress }}
        >
          <div
            className="absolute inset-x-0 bottom-0"
            style={{
              height: '38vh',
              background: 'linear-gradient(180deg, rgba(2,9,21,0) 0%, rgba(2,9,21,0.72) 62%, rgba(2,9,21,0.92) 100%)',
            }}
          />
          <div className="text-center pointer-events-auto">
            <p className="font-mono text-[11px] tracking-widest text-teal uppercase mb-3 text-shadow-soft">
              Worlds 2024 &nbsp;·&nbsp; AI Prediction
            </p>
            <h2
              className="font-cinzel font-black text-gold leading-none text-shadow-gold"
              style={{ fontSize: 'clamp(28px, 5.5vw, 70px)' }}
            >
              T1 wins. 82.4%.
            </h2>
            <p className="font-exo font-light text-[#C8A96E] mt-2 text-shadow-soft"
              style={{ fontSize: 'clamp(15px, 1.6vw, 18px)' }}>
              Draft analyzed before first blood.
            </p>
            <div className="flex items-center justify-center gap-3 mt-5">
              <a
                href="#pricing"
                className="font-cinzel text-[12px] font-bold tracking-widest text-[#050300] uppercase
                           px-10 py-3 clip-skew no-underline inline-block
                           transition-all hover:brightness-110"
                style={{ background: 'linear-gradient(135deg, #D4B483, #7a5f38)' }}
                data-cursor-hover
              >
                Start predicting
              </a>
              <a
                href="#draft"
                className="font-rajdhani text-[12px] font-bold tracking-widest text-[#C8A96E] uppercase
                           px-7 py-3 clip-skew-sm no-underline inline-block
                           transition-all hover:border-gold-dim hover:text-gold"
                style={{ border: '1px solid rgba(200,169,110,0.38)' }}
                data-cursor-hover
              >
                See the model
              </a>
            </div>
          </div>
        </div>

        <div
          className="absolute bottom-6 left-1/2 -translate-x-1/2 z-[15]
                     flex flex-col items-center gap-1.5"
          style={{ opacity: Math.max(0, 0.4 - progress * 3) }}
        >
              <span className="font-mono text-[10px] tracking-widest text-shadow-soft"
                style={{ color: 'rgba(200,169,110,0.55)' }}>
            Scroll
          </span>
          <div
            className="w-px animate-scroll-hint"
            style={{
              height: '30px',
              background: 'linear-gradient(180deg, #7a5f38, transparent)',
            }}
          />
        </div>

      </div>
    </div>
  )
}