import { useScrollReveal } from '../hooks'

export default function Scene({ id, imageSrc, textSide = 'right', label, title, body, tags = [], cta }) {
  const { ref, visible } = useScrollReveal(0.12)

  const overlayStyle = textSide === 'right'
    ? { background: 'linear-gradient(90deg, rgba(2,9,21,0) 30%, rgba(2,9,21,0.92) 66%, rgba(2,9,21,1) 100%)' }
    : { background: 'linear-gradient(270deg, rgba(2,9,21,0) 30%, rgba(2,9,21,0.92) 66%, rgba(2,9,21,1) 100%)' }

  return (
    <section
      id={id}
      ref={ref}
      className="relative h-screen flex items-center overflow-hidden"
      style={{
        opacity: visible ? 1 : 0,
        transform: visible ? 'translateY(0)' : 'translateY(20px)',
        transition: 'opacity 1.2s ease-out, transform 1.2s ease-out',
      }}
    >
      <div className="absolute inset-0">
        <img
          src={imageSrc}
          alt=""
          className="w-full h-full object-cover"
        />
      </div>

      <div className="absolute inset-0" style={overlayStyle} />

      <div
        className="absolute inset-0"
        style={{
          background: 'linear-gradient(180deg, rgba(2,9,21,1) 0%, rgba(2,9,21,0) 25%, rgba(2,9,21,0) 75%, rgba(2,9,21,1) 100%)',
        }}
      />

      <div
        className={`relative z-10 max-w-[390px] ${textSide === 'right' ? 'ml-auto pr-15' : 'pl-15'}`}
        style={{ padding: textSide === 'right' ? '0 60px 0 0' : '0 0 0 60px' }}
      >
        <div className="flex items-center gap-3 font-mono text-[9px] tracking-widest text-teal uppercase mb-3">
          <span style={{ width: '22px', height: '1px', background: '#0AC8B9', display: 'inline-block' }} />
          {label}
        </div>

        <h2
          className="font-cinzel font-bold text-gold uppercase tracking-wide leading-[1.02]"
          style={{ fontSize: 'clamp(26px, 3.8vw, 52px)' }}
          dangerouslySetInnerHTML={{ __html: title }}
        />

        <p
          className="font-exo font-light text-[rgba(138,149,176,0.85)] mt-3 leading-relaxed"
          style={{ fontSize: '14px', maxWidth: '310px' }}
        >
          {body}
        </p>

        {tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-3">
            {tags.map(tag => (
              <span
                key={tag}
                className="font-mono text-[9px] tracking-widest text-gold px-2.5 py-1"
                style={{
                  background: 'rgba(200,169,110,0.06)',
                  border: '1px solid rgba(200,169,110,0.18)',
                }}
              >
                {tag}
              </span>
            ))}
          </div>
        )}

        {cta && (
          <div className="mt-5">
            <a
              href={cta.href}
              className={`
                font-rajdhani text-[12px] font-bold tracking-widest uppercase
                px-8 py-3 clip-skew-sm no-underline inline-block transition-all
                ${cta.variant === 'gold'
                  ? 'text-[#050300] hover:brightness-110'
                  : 'text-[#8a95b0] hover:border-gold-dim hover:text-gold'
                }
              `}
              style={cta.variant === 'gold'
                ? { background: 'linear-gradient(135deg, #D4B483, #7a5f38)' }
                : { border: '1px solid rgba(200,169,110,0.38)' }
              }
              data-cursor-hover
            >
              {cta.label}
            </a>
          </div>
        )}
      </div>
    </section>
  )
}