import { useScrollReveal } from '../hooks'

export default function Scene({ id, imageSrc, textSide = 'right', label, title, body, tags = [], cta }) {
  const { ref, visible } = useScrollReveal(0.12)
  const isDraftSection = id === 'draft'

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
        className={`relative z-10 max-w-[460px] ${textSide === 'right' ? 'ml-auto pr-15' : 'pl-15'}`}
        style={{ padding: textSide === 'right' ? '0 60px 0 0' : '0 0 0 60px' }}
      >
        <div
          className="flex items-center gap-3 font-mono text-[11px] tracking-widest uppercase mb-3"
          style={{ color: isDraftSection ? '#C8A96E' : '#0AC8B9' }}
        >
          <span
            style={{
              width: '22px',
              height: '1px',
              background: isDraftSection ? '#C8A96E' : '#0AC8B9',
              display: 'inline-block',
            }}
          />
          {label}
        </div>

        <h2
          className="font-cinzel font-bold text-gold uppercase tracking-wide leading-[1.02]"
          style={{ fontSize: 'clamp(32px, 4.4vw, 62px)' }}
          dangerouslySetInnerHTML={{ __html: title }}
        />

        <p
          className="font-exo font-light mt-3 leading-relaxed"
          style={{
            fontSize: '16px',
            maxWidth: '360px',
            color: isDraftSection ? 'rgba(200,169,110,0.92)' : 'rgba(138,149,176,0.85)',
          }}
        >
          {body}
        </p>

        {tags.length > 0 && (
          <div className="flex flex-wrap gap-1.5 mt-3">
            {tags.map(tag => (
              <span
                key={tag}
                className="font-mono text-[10px] tracking-widest text-gold px-2.5 py-1"
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
                font-rajdhani text-[13px] font-bold tracking-widest uppercase
                px-9 py-3.5 clip-skew-sm no-underline inline-block transition-all
                ${cta.variant === 'gold'
                  ? 'text-[#050300] hover:brightness-110'
                  : isDraftSection
                    ? 'text-gold hover:brightness-110'
                    : 'text-[#8a95b0] hover:border-gold-dim hover:text-gold'
                }
              `}
              style={cta.variant === 'gold'
                ? { background: 'linear-gradient(135deg, #D4B483, #7a5f38)' }
                : {
                    border: '1px solid rgba(200,169,110,0.38)',
                    background: isDraftSection ? 'rgba(200,169,110,0.05)' : 'transparent',
                  }
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