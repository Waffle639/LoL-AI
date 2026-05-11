import { useEffect, useState } from 'react'
import anime from 'animejs'
import AppLayout from '@/components/layout/AppLayout'
import StatCard from '@/components/ui/StatCard'
import Panel, { PanelTitle } from '@/components/ui/Panel'
import Badge from '@/components/ui/Badge'
import DonutChart from '@/components/charts/DonutChart'
import Sparkline from '@/components/charts/Sparkline'
import { useApp } from '@/context/AppContext'
import { getBillingSummary } from '@/api/billing'
import styles from './Dashboard.module.css'

// ─────────────────────────────────────────────────────────────────
// Dashboard
// Overview: KPI cards · donut breakdown · sparkline · recent table
// ─────────────────────────────────────────────────────────────────

const RECENT = [
  { id: 127, t1: 'G2 Esports',   t2: 'MAD Lions', type: 'PRE',  winner: 'G2 Esports',  prob: 77.8, result: 'win'  },
  { id: 126, t1: 'T1',           t2: 'Gen.G',      type: 'LIVE', winner: 'T1',          prob: 87.3, result: 'win'  },
  { id: 125, t1: 'Cloud9',       t2: 'Team Liquid', type: 'LIVE', winner: 'C9',          prob: 34.1, result: 'loss' },
  { id: 124, t1: 'Fnatic',       t2: 'NaVi',        type: 'PRE',  winner: 'Fnatic',      prob: 61.2, result: 'win'  },
]

export default function Dashboard() {
  const { credits, setCredits, accessToken, getAccessToken } = useApp()
  const [usage, setUsage] = useState({
    used_today: 0,
    used_total: 0,
    bought_total: 0,
  })

  useEffect(() => {
    let active = true
    if (!accessToken) return () => { active = false }

    const loadSummary = async () => {
      try {
        const token = await getAccessToken()
        if (!token || !active) return
        const data = await getBillingSummary({ accessToken: token })
        if (!active) return
        setUsage({
          used_today: data?.used_today ?? 0,
          used_total: data?.used_total ?? 0,
          bought_total: data?.bought_total ?? 0,
        })
        if (typeof data?.credits_remaining === 'number') {
          setCredits(data.credits_remaining)
        }
      } catch {
        if (!active) return
      }
    }

    loadSummary()

    return () => { active = false }
  }, [accessToken, getAccessToken, setCredits])

  // Entry animations
  useEffect(() => {
    anime({ targets: '.sec-title, .sec-sub', opacity: [0,1], translateY: [-8,0], delay: anime.stagger(60), duration: 350, easing: 'easeOutExpo' })
    anime({ targets: '.scard',               opacity: [0,1], translateY: [22,0], scale: [0.96,1], delay: anime.stagger(80, { start: 200 }), duration: 460, easing: 'easeOutBack' })
    anime({ targets: '.dash-panel',          opacity: [0,1], translateY: [16,0], delay: anime.stagger(90, { start: 500 }), duration: 400, easing: 'easeOutExpo' })
    anime({ targets: '#s-dashboard tbody tr',opacity: [0,1], translateX: [-8,0], delay: anime.stagger(65, { start: 800 }), duration: 320, easing: 'easeOutExpo' })
    // Credits counter
    const obj = { val: 0 }
    anime({ targets: obj, val: credits, duration: 900, delay: 250, easing: 'easeOutExpo', update: () => {
      const el = document.getElementById('db-credits')
      if (el) el.textContent = Math.round(obj.val)
    }})
  }, [credits])

  return (
    <AppLayout>
      <h1 className="sec-title">Dashboard</h1>
      <p className="sec-sub">Welcome back, Waffle639 &mdash; last seen 2h ago</p>

      {/* KPI cards */}
      <div className={styles.statRow}>
        <StatCard label="Total Predictions" value="127"  trend="+14 this week" trendUp color="gold"  />
        <StatCard label="Avg Accuracy"       value="89%"  trend="model performing well" trendUp color="green" />
        <StatCard label="Credits Left"       value={<span id="db-credits">{credits}</span>} trend={`of ${usage.bought_total} purchased`} color="teal"  />
        <StatCard label="Credits Used"       value={usage.used_total}  trend={`${usage.used_today} today`} color="red"   />
      </div>

      {/* Charts row */}
      <div className={styles.chartRow}>
        <Panel accent="gold" className="dash-panel">
          <PanelTitle>
            Prediction Breakdown
            <Badge variant="gold">ALL TIME</Badge>
          </PanelTitle>
          <DonutChart
            segments={[
              { value: 78,  color: '#0AC8B9', label: 'LIVE'     },
              { value: 49,  color: '#C8A96E', label: 'PRE-GAME' },
              { value: 113, color: '#2ecc71', label: 'CORRECT'  },
              { value: 14,  color: '#C83020', label: 'WRONG'    },
            ]}
            center={{ value: '127', label: 'TOTAL' }}
          />
        </Panel>

        <Panel accent="teal" className="dash-panel">
          <PanelTitle>
            Win Probability — Last 14 Predictions
            <Badge variant="teal">TREND</Badge>
          </PanelTitle>
          <Sparkline />
        </Panel>
      </div>

      {/* Recent predictions table */}
      <div className={styles.tableWrap} id="s-dashboard">
        <div className={styles.tableHeader}>
          <span className={styles.tableTitle}>Recent Predictions</span>
          <Badge variant="gold">LATEST</Badge>
        </div>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>Team 1</th><th>Team 2</th><th>Type</th>
              <th>Prediction</th><th>Prob.</th><th>Date</th>
            </tr>
          </thead>
          <tbody>
            {RECENT.map(r => (
              <tr key={r.id}>
                <td>{r.t1}</td>
                <td>{r.t2}</td>
                <td><Badge variant={r.type === 'PRE' ? 'teal' : 'gold'}>{r.type}</Badge></td>
                <td className={r.result === 'win' ? styles.win : styles.loss}>
                  {r.winner} {r.result === 'win' ? 'WIN' : 'LOSS'}
                </td>
                <td>
                  <div className={styles.probRow}>
                    <div className={styles.probTrack}>
                      <div className={styles.probFill} style={{ width: `${r.prob}%` }} />
                    </div>
                    <span className={styles.probNum}>{r.prob}%</span>
                  </div>
                </td>
                <td className={styles.mono}>today</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </AppLayout>
  )
}
