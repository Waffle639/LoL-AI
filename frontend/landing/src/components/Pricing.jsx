import { useState } from 'react'
import { PRICING } from '../data/content'
import { useScrollReveal } from '../hooks'

function FeatureRow({ label, included }) {
  return (
    <div className="flex items-center gap-2 mb-1.5 text-left font-exo text-[12px] font-light">
      <span
        className="w-3 text-center text-[10px] flex-shrink-0"
        style={{ color: included ? '#0AC8B9' : 'rgba(90,101,128,0.3)' }}
      >
        {included ? '✓' : '✕'}
      </span>
      <span style={{ color: included ? '#8a95b0' : 'rgba(90,101,128,0.36)' }}>
        {label}
      </span>
    </div>
  )
}

function PricingCard({ plan, index }) {
  const [showTip, setShowTip] = useState(false)
  const { ref, visible } = useScrollReveal(0.1)

  return (
    <div
      ref={ref}
      className="relative text-center overflow-visible transition-all duration-250"
      style={{
        background: plan.featured
          ? 'linear-gradient(180deg, rgba(200,169,110,0.04), #020915)'
          : '#020915',
        border: plan.featured
          ? '1px solid #C8A96E'
          : '1px solid transparent',
        padding: '36px 22px',
        opacity: visible ? 1 : 0,
        transform: visible ? 'translateY(0)' : 'translateY(30px)',
        transition: `opacity 0.6s ${index * 0.1}s ease, transform 0.6s ${index * 0.1}s ease, border-color 0.25s ease`,
      }}
      onMouseEnter={e => {
        if (!plan.featured) e.currentTarget.style.borderColor = '#7a5f38'
        setShowTip(true)
      }}
      onMouseLeave={e => {
        if (!plan.featured) e.currentTarget.style.borderColor = 'transparent'
        setShowTip(false)
      }}
    >
      <div
        className="absolute top-0 left-0 right-0 h-px"
        style={{
          background: plan.featured
            ? 'linear-gradient(90deg, transparent, #C8A96E, transparent)'
            : 'linear-gradient(90deg, transparent, #7a5f38, transparent)',
        }}
      />

      {plan.badge && (
        <div
          className="absolute top-0 left-1/2 -translate-x-1/2 font-mono text-[8px] tracking-widest px-4 py-1 whitespace-nowrap"
          style={{ background: '#C8A96E', color: '#050300', letterSpacing: '0.2em' }}
        >
          {plan.badge}
        </div>
      )}

      {plan.tip && showTip && (
        <div
          className="absolute font-mono text-[8px] tracking-wide whitespace-nowrap px-3 py-2 z-50"
          style={{
            bottom: 'calc(100% + 10px)',
            left: '50%',
            transform: 'translateX(-50%)',
            background: '#0b1628',
            border: '1px solid rgba(10,200,185,0.2)',
            color: '#0AC8B9',
          }}
        >
          {plan.tip}
          <span
            className="absolute top-full left-1/2 -translate-x-1/2"
            style={{
              border: '5px solid transparent',
              borderTopColor: 'rgba(10,200,185,0.2)',
            }}
          />
        </div>
      )}

      <p className="font-cinzel font-bold text-gold leading-none" style={{ fontSize: '56px' }}>
        {plan.credits}
      </p>
      <p className="font-mono text-[8px] tracking-widest mb-3.5" style={{ color: '#3a4560', letterSpacing: '0.3em' }}>
        CREDITS
      </p>

      <div className="h-px my-3.5" style={{ background: 'rgba(200,169,110,0.14)' }} />

      <p className="font-cinzel font-bold text-[24px] text-[#C8D0E0] mb-0.5">{plan.price}</p>
      <p className="font-mono text-[8px] tracking-wide mb-4" style={{ color: '#3a4560' }}>
        {plan.perCredit}
      </p>

      <div className="mb-1">
        {plan.features.map(f => (
          <FeatureRow key={f.label} label={f.label} included={f.included} />
        ))}
      </div>

      <button
        className={`
          block w-full mt-4 font-rajdhani text-[11px] font-bold tracking-widest uppercase py-3
          transition-all cursor-none
          ${plan.ctaVariant === 'gold' ? 'clip-skew text-[#050300] hover:brightness-110' : 'hover:bg-gold/7'}
        `}
        style={plan.ctaVariant === 'gold'
          ? { background: 'linear-gradient(135deg, #D4B483, #7a5f38)' }
          : {
              background: 'transparent',
              border: '1px solid rgba(200,169,110,0.38)',
              color: '#C8A96E',
            }
        }
        data-cursor-hover
      >
        {plan.cta}
      </button>
    </div>
  )
}

export default function Pricing() {
  const { ref, visible } = useScrollReveal(0.08)

  return (
    <section
      id="pricing"
      style={{
        background: '#060f1e',
        borderTop: '1px solid rgba(200,169,110,0.14)',
        padding: '88px 52px',
      }}
    >
      <div style={{ maxWidth: '960px', margin: '0 auto' }}>
        <div
          ref={ref}
          className="text-center"
          style={{
            opacity: visible ? 1 : 0,
            transform: visible ? 'translateY(0)' : 'translateY(20px)',
            transition: 'opacity 0.66s ease, transform 0.66s ease',
          }}
        >
          <p className="font-mono text-[9px] tracking-widest text-teal uppercase mb-2">
            Pricing
          </p>
          <h2
            className="font-cinzel font-bold text-gold uppercase tracking-wide"
            style={{ fontSize: 'clamp(22px, 4vw, 44px)' }}
          >
            Pay per prediction.<br />
            <em className="text-stroke-gold not-italic">No subscriptions.</em>
          </h2>
          <p className="font-exo font-light mt-2.5" style={{ fontSize: '13px', color: '#3a4560' }}>
            Credits never expire.
          </p>
        </div>

        <div
          className="grid mt-10"
          style={{ gridTemplateColumns: 'repeat(3, 1fr)', gap: '2px' }}
        >
          {PRICING.map((plan, i) => (
            <PricingCard key={plan.id} plan={plan} index={i} />
          ))}
        </div>
      </div>
    </section>
  )
}