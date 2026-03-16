import { useScrollReveal } from '../hooks'

const CUP_IMG = '/images/copa.jpg'

export function CupCTA() {
  const { ref, visible } = useScrollReveal(0.15)

  return (
    <section className="relative overflow-hidden flex items-center justify-center" style={{ height: '76vh' }}>
      <div className="absolute inset-0">
        <img
          src={CUP_IMG}
          alt="Summoner's Cup"
          className="w-full h-full object-cover"
          style={{ objectPosition: 'center 30%' }}
        />
      </div>

      <div
        className="absolute inset-0"
        style={{
          background: 'radial-gradient(ellipse at 50% 45%, rgba(2,9,21,.05) 0%, rgba(2,9,21,.55) 52%, rgba(2,9,21,.96) 100%)',
        }}
      />

      <div
        ref={ref}
        className="relative z-10 text-center px-6"
        style={{
          opacity: visible ? 1 : 0,
          transform: visible ? 'translateY(0)' : 'translateY(20px)',
          transition: 'opacity 0.66s ease, transform 0.66s ease',
        }}
      >
        <h2
          className="font-cinzel font-black text-gold uppercase leading-none"
          style={{
            fontSize: 'clamp(24px, 6vw, 72px)',
            textShadow: '0 0 70px rgba(200,169,110,0.18), 0 2px 20px rgba(0,0,0,0.9)',
          }}
        >
          The Rift awaits.
        </h2>
        <p
          className="font-exo font-light mt-3 mx-auto leading-relaxed"
          style={{ fontSize: '14px', color: '#8a95b0', maxWidth: '340px' }}
        >
          Stop guessing. Start predicting.
        </p>
        <div className="mt-6">
          <a
            href="#pricing"
            className="font-cinzel text-[12px] font-bold tracking-widest text-[#050300] uppercase
                       px-11 py-4 clip-skew no-underline inline-block
                       transition-all hover:brightness-110 hover:-translate-y-0.5"
            style={{ background: 'linear-gradient(135deg, #D4B483, #7a5f38)' }}
            data-cursor-hover
          >
            Enter the Rift
          </a>
        </div>
      </div>
    </section>
  )
}

export function Footer() {
  return (
    <footer
      className="flex items-center justify-between flex-wrap gap-3 px-13 py-7"
      style={{
        background: '#060f1e',
        borderTop: '1px solid rgba(200,169,110,0.14)',
        padding: '28px 52px',
      }}
    >
      <div className="flex items-center gap-2.5">
        <div
          className="flex items-center justify-center w-6 h-6 clip-hex"
          style={{
            background: 'linear-gradient(135deg, #1a1200, #3a2800)',
            border: '1px solid #3a2c15',
          }}
        >
          <svg width="10" height="10" viewBox="0 0 24 24" fill="#7a5f38">
            <path d="M12 2l2.5 5.5H20l-4.5 4 1.5 6L12 14.5 7 17.5l1.5-6L4 7.5h5.5z" />
          </svg>
        </div>
        <span className="font-cinzel text-[11px] font-bold tracking-widest2" style={{ color: '#7a5f38' }}>
          LOL&middot;AI
        </span>
      </div>

      <div className="flex gap-6">
        {['Privacy', 'Terms', 'API Docs', 'GitHub'].map(link => (
          <a
            key={link}
            href="#"
            className="font-mono text-[9px] tracking-widest uppercase no-underline transition-colors hover:text-gold"
            style={{ color: '#3a4560', letterSpacing: '0.15em' }}
            data-cursor-hover
          >
            {link}
          </a>
        ))}
      </div>

      <p className="font-mono text-[9px]" style={{ color: '#3a4560' }}>
        © 2025 LOL-AI · Not affiliated with Riot Games
      </p>
    </footer>
  )
}