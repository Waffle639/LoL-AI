import { useEffect, useState } from 'react'
import anime from 'animejs'
import AppLayout from '@/components/layout/AppLayout'
import Panel, { PanelTitle } from '@/components/ui/Panel'
import Button from '@/components/ui/Button'
import { useApp } from '@/context/AppContext'
import { getBillingSummary, getCreditPacks, createCreditCheckout } from '@/api/billing'
import styles from './Billing.module.css'

// ─────────────────────────────────────────────────────────────────
// Billing
// Credit balance · usage summary · Stripe checkout plans
// Balance bar animates on entry · Featured plan pulses
// ─────────────────────────────────────────────────────────────────

const FALLBACK_PLANS = [
  { id: 'duelist', credits: 25,  price: '€4.99',  per: '≈ 0.20€ per credit', featured: false },
  { id: 'elite',   credits: 100, price: '€14.99', per: '≈ 0.15€ per credit', featured: true  },
  { id: 'legend',  credits: 500, price: '€49.99', per: '≈ 0.10€ per credit', featured: false },
]

const EMPTY_USAGE = {
  used_today: 0,
  used_week: 0,
  used_total: 0,
  bought_total: 0,
}

export default function Billing() {
  const { credits, setCredits, accessToken, getAccessToken } = useApp()
  const [usage, setUsage] = useState(EMPTY_USAGE)
  const [packs, setPacks] = useState([])
  const [packError, setPackError] = useState('')
  const [checkoutError, setCheckoutError] = useState('')
  const [checkoutLoading, setCheckoutLoading] = useState('')
  const [notice, setNotice] = useState('')

  const balanceTotal = Math.max(usage.bought_total || 0, credits)
  const balancePct = balanceTotal > 0
    ? Math.min(100, Math.round((credits / balanceTotal) * 100))
    : 0

  const usageItems = [
    { label: 'Today',        value: usage.used_today,  color: 'var(--red)'  },
    { label: 'This Week',    value: usage.used_week,   color: 'var(--txt)'  },
    { label: 'Total Used',   value: usage.used_total,  color: 'var(--txt)'  },
    { label: 'Total Bought', value: usage.bought_total, color: 'var(--gold)' },
  ]

  useEffect(() => {
    let active = true
    if (!accessToken) return () => { active = false }

    const loadSummary = async () => {
      try {
        const token = await getAccessToken()
        if (!token || !active) return
        const data = await getBillingSummary({ accessToken: token })
        if (!active) return
        const nextUsage = {
          used_today: data?.used_today ?? 0,
          used_week: data?.used_week ?? 0,
          used_total: data?.used_total ?? 0,
          bought_total: data?.bought_total ?? 0,
        }
        setUsage(nextUsage)
        if (typeof data?.credits_remaining === 'number') {
          setCredits(data.credits_remaining)
        }
      } catch (err) {
        console.error('Billing: error loading summary', err)
        if (!active) return
      }
    }

    loadSummary()

    return () => { active = false }
  }, [accessToken, getAccessToken, setCredits])

  useEffect(() => {
    let active = true
    getCreditPacks()
      .then(data => {
        if (!active) return
        const items = Array.isArray(data?.packs) ? data.packs : []
        setPacks(items)
      })
      .catch(err => {
        if (!active) return
        setPackError(err.message || 'No se pudieron cargar los packs')
      })

    return () => { active = false }
  }, [])

  useEffect(() => {
    const params = new URLSearchParams(window.location.search)
    if (params.get('success') === 'true') {
      setNotice('Compra aprobada. Tus creditos se actualizaran en segundos.')
    } else if (params.get('canceled') === 'true') {
      setNotice('Pago cancelado. No se ha realizado ningun cargo.')
    }
  }, [])

  useEffect(() => {
    anime({ targets: '#s-billing .panel', opacity:[0,1], translateY:[18,0], delay: anime.stagger(90), duration:450, easing:'easeOutExpo' })
    anime({ targets: '.price-card',       opacity:[0,1], translateY:[28,0], scale:[.94,1], delay: anime.stagger(110,{start:480}), duration:460, easing:'easeOutBack' })
    anime({ targets: '.feat-card',        boxShadow:['0 0 0px rgba(200,169,110,0)','0 0 22px rgba(200,169,110,0.18)','0 0 0px rgba(200,169,110,0)'], duration:1800, delay:900, loop:true, easing:'easeInOutSine' })
  }, [])

  useEffect(() => {
    anime({ targets: '#bal-fill', width:["0%", `${balancePct}%`], duration:950, delay:400, easing:'easeOutExpo' })
  }, [balancePct])

  const plans = packs.length ? packs : FALLBACK_PLANS

  const handlePurchase = async packId => {
    setCheckoutError('')

    const token = await getAccessToken()
    if (!token) {
      setCheckoutError('Necesitas iniciar sesion para comprar creditos.')
      return
    }

    setCheckoutLoading(packId)
    try {
      const payload = await createCreditCheckout({ accessToken: token, packId })
      if (payload?.checkout_url) {
        window.location.href = payload.checkout_url
      } else {
        throw new Error('No se pudo iniciar el checkout')
      }
    } catch (err) {
      setCheckoutError(err.message || 'No se pudo iniciar el checkout')
      setCheckoutLoading('')
    }
  }

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
              <span>{credits} / {balanceTotal}</span>
            </div>
          </Panel>

          {/* Usage panel */}
          <Panel accent="teal" className="panel">
            <PanelTitle>Usage Summary</PanelTitle>
            <div className={styles.usageGrid}>
              {usageItems.map((u, i) => (
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

        {notice && <div className={styles.plansNotice}>{notice}</div>}
        {packError && <div className={styles.plansError}>{packError}</div>}
        {checkoutError && <div className={styles.plansError}>{checkoutError}</div>}

        <div className={styles.plansGrid}>
          {plans.map((p, i) => (
            <div key={p.id || i} className={`price-card ${styles.priceCard} ${p.featured ? `feat-card ${styles.featured}` : ''}`}>
              {p.featured && <div className={styles.featLabel}>BEST VALUE</div>}
              <div className={styles.planCredits}>{p.credits}</div>
              <div className={styles.planCreditsLbl}>CREDITS</div>
              <div className={styles.planPrice}>{p.price}</div>
              <div className={styles.planPer}>{p.per}</div>
              <Button
                variant={p.featured ? 'gold' : 'ghost'}
                fullWidth
                onClick={() => handlePurchase(p.id)}
                disabled={checkoutLoading === p.id}
              >
                {checkoutLoading === p.id ? 'Redirecting...' : 'Purchase'}
              </Button>
            </div>
          ))}
        </div>
      </div>
    </AppLayout>
  )
}
