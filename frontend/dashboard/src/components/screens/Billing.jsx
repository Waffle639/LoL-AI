import { useEffect } from 'react'
import anime from 'animejs'
import AppLayout from '@/components/layout/AppLayout'
import Panel, { PanelTitle } from '@/components/ui/Panel'
import Button from '@/components/ui/Button'
import { useApp } from '@/context/AppContext'
import styles from './Billing.module.css'

// ─────────────────────────────────────────────────────────────────
// Billing
// Credit balance · usage summary · Stripe checkout plans
// Balance bar animates on entry · Featured plan pulses
// ─────────────────────────────────────────────────────────────────

const PLANS = [
  { credits: 25,  price: '€4.99',  per: '≈ 0.20€ per credit', featured: false },
  { credits: 100, price: '€14.99', per: '≈ 0.15€ per credit', featured: true  },
  { credits: 500, price: '€49.99', per: '≈ 0.10€ per credit', featured: false },
]

const USAGE = [
  { label: 'Today',        value: '8',   color: 'var(--red)'  },
  { label: 'This Week',    value: '23',  color: 'var(--txt)'  },
  { label: 'Total Used',   value: '85',  color: 'var(--txt)'  },
  { label: 'Total Bought', value: '127', color: 'var(--gold)' },
]

export default function Billing() {
  const { credits } = useApp()

  useEffect(() => {
    anime({ targets: '#s-billing .panel', opacity:[0,1], translateY:[18,0], delay: anime.stagger(90), duration:450, easing:'easeOutExpo' })
    anime({ targets: '#bal-fill',         width:['0%','84%'], duration:950, delay:400, easing:'easeOutExpo' })
    anime({ targets: '.price-card',       opacity:[0,1], translateY:[28,0], scale:[.94,1], delay: anime.stagger(110,{start:480}), duration:460, easing:'easeOutBack' })
    anime({ targets: '.feat-card',        boxShadow:['0 0 0px rgba(200,169,110,0)','0 0 22px rgba(200,169,110,0.18)','0 0 0px rgba(200,169,110,0)'], duration:1800, delay:900, loop:true, easing:'easeInOutSine' })
  }, [])

  return (
    <AppLayout>
      <div id="s-billing">
        <h1 className="sec-title">Credits &amp; Billing</h1>
        <p className="sec-sub">Secure payments via Stripe &nbsp;·&nbsp; Credits never expire</p>

        <div className={styles.topRow}>
          {/* Balance panel */}
          <Panel accent="gold" className={`panel ${styles.balancePanel}`}>
            <PanelTitle>Current Balance</PanelTitle>
            <div className={styles.balanceNum}>{credits}</div>
            <div className={styles.balanceLbl}>CREDITS AVAILABLE</div>
            <div className={styles.balBar}>
              <div id="bal-fill" className={styles.balFill} style={{ width: 0 }} />
            </div>
            <div className={styles.balMeta}>
              <span>0</span>
              <span>{credits} / 50</span>
            </div>
          </Panel>

          {/* Usage panel */}
          <Panel accent="teal" className="panel">
            <PanelTitle>Usage Summary</PanelTitle>
            <div className={styles.usageGrid}>
              {USAGE.map((u, i) => (
                <div key={i} className={styles.usageCell}>
                  <div className={styles.usageLabel}>{u.label}</div>
                  <div className={styles.usageVal} style={{ color: u.color }}>{u.value}</div>
                </div>
              ))}
            </div>
          </Panel>
        </div>

        {/* Pricing */}
        <h2 className={styles.plansTitle}>Purchase Credits</h2>
        <p className={styles.plansSub}>Powered by Stripe &nbsp;·&nbsp; Instant delivery</p>

        <div className={styles.plansGrid}>
          {PLANS.map((p, i) => (
            <div key={i} className={`price-card ${styles.priceCard} ${p.featured ? `feat-card ${styles.featured}` : ''}`}>
              {p.featured && <div className={styles.featLabel}>BEST VALUE</div>}
              <div className={styles.planCredits}>{p.credits}</div>
              <div className={styles.planCreditsLbl}>CREDITS</div>
              <div className={styles.planPrice}>{p.price}</div>
              <div className={styles.planPer}>{p.per}</div>
              <Button variant={p.featured ? 'gold' : 'ghost'} fullWidth>
                Purchase
              </Button>
            </div>
          ))}
        </div>
      </div>
    </AppLayout>
  )
}
