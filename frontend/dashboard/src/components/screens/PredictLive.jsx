import { useState, useEffect } from 'react'
import anime from 'animejs'
import AppLayout from '@/components/layout/AppLayout'
import Panel, { PanelTitle } from '@/components/ui/Panel'
import FormField from '@/components/ui/FormField'
import Button from '@/components/ui/Button'
import { useApp } from '@/context/AppContext'
import styles from './PredictLive.module.css'

// ─────────────────────────────────────────────────────────────────
// PredictLive  —  POST /predict
// Neural Network (24→64→32→1) · Accuracy 97.76%
// ─────────────────────────────────────────────────────────────────

const DEFAULT_FORM = {
  team: 'G2 Esports', player: 'Caps', champion: 'Azir',
  side: 'Blue', position: 'mid',
  kills: '5', deaths: '2', assists: '8',
  dragons: '3', barons: '2', towers: '9', gold: '15000',
}

export default function PredictLive() {
  const { credits, consumeCredit } = useApp()
  const [form, setForm]       = useState(DEFAULT_FORM)
  const [result, setResult]   = useState({ prob: 87.32, winner: 'G2 Esports', victory: true })
  const [loading, setLoading] = useState(false)

  const set = key => e => setForm(f => ({ ...f, [key]: e.target.value }))

  useEffect(() => {
    anime({ targets: '#pl-left .panel',  opacity:[0,1], translateX:[-18,0], delay: anime.stagger(90), duration:480, easing:'easeOutExpo' })
    anime({ targets: '#pl-result',       opacity:[0,1], translateY:[18,0],  delay:280, duration:560, easing:'easeOutExpo' })
  }, [])

  const handlePredict = () => {
    setLoading(true)
    setTimeout(() => {
      consumeCredit()
      setLoading(false)
      // Burst animation on result card
      const burst = document.getElementById('predict-burst')
      if (burst) {
        burst.innerHTML = ''
        for (let i = 0; i < 16; i++) {
          const p = document.createElement('div')
          p.style.cssText = `position:absolute;width:${Math.random()*5+3}px;height:${Math.random()*5+3}px;border-radius:${Math.random()>.5?'50%':'2px'};background:${Math.random()>.5?'#0AC8B9':'#C8A96E'};left:50%;top:50%;pointer-events:none;`
          burst.appendChild(p)
        }
        anime({ targets:'#predict-burst > div', translateX:()=>anime.random(-110,110), translateY:()=>anime.random(-70,70), scale:[1,0], opacity:[1,0], duration:()=>anime.random(480,850), easing:'easeOutExpo' })
      }
      anime({ targets:'#pl-result', borderColor:['rgba(10,200,185,.8)','rgba(200,169,110,.18)'], duration:750, easing:'easeOutExpo' })
      anime({ targets:'#r-team-name', scale:[.65,1.06,1], opacity:[0,1], duration:560, easing:'easeOutBack' })
    }, 600)
  }

  const blueW = result.prob
  const redW  = 100 - result.prob

  return (
    <AppLayout>
      <h1 className="sec-title">Predict Live</h1>
      <p className="sec-sub">In-game state &nbsp;·&nbsp; Neural Network &nbsp;·&nbsp; 1 credit</p>

      <div className={styles.grid}>

        {/* Form column */}
        <div id="pl-left">
          <Panel accent="gold" style={{ marginBottom: 16 }}>
            <PanelTitle>Player Identity</PanelTitle>
            <FormField label="Team"     value={form.team}     onChange={set('team')} />
            <FormField label="Player"   value={form.player}   onChange={set('player')} />
            <FormField label="Champion" value={form.champion} onChange={set('champion')} />
            <div className={styles.twoCol}>
              <FormField label="Side"     value={form.side}     onChange={set('side')} />
              <FormField label="Position" value={form.position} onChange={set('position')} />
            </div>
          </Panel>

          <Panel accent="teal">
            <PanelTitle>Live Game Stats</PanelTitle>
            <div className={styles.threeCol}>
              <FormField label="Kills"   value={form.kills}   onChange={set('kills')} />
              <FormField label="Deaths"  value={form.deaths}  onChange={set('deaths')} />
              <FormField label="Assists" value={form.assists} onChange={set('assists')} />
              <FormField label="Dragons" value={form.dragons} onChange={set('dragons')} />
              <FormField label="Barons"  value={form.barons}  onChange={set('barons')} />
              <FormField label="Towers"  value={form.towers}  onChange={set('towers')} />
            </div>
            <FormField label="Total Gold" value={form.gold} onChange={set('gold')} />
          </Panel>
        </div>

        {/* Result column */}
        <div>
          <div className={styles.resultCard} id="pl-result">
            <div id="predict-burst" className={styles.burst} />
            <div className={styles.resultLabel}>NEURAL NETWORK PREDICTION</div>
            <div className={styles.resultTeam} id="r-team-name">
              {result.victory ? 'VICTORY' : 'DEFEAT'}
            </div>
            <div className={styles.resultProb}>{result.prob}% win probability</div>

            <div className={styles.vsTrack}>
              <div className={styles.vsBlue} style={{ flex: blueW }} />
              <div className={styles.vsRed}  style={{ flex: redW  }} />
            </div>
            <div className={styles.vsLabels}>
              <span style={{ color: 'var(--teal)' }}>{form.team} {blueW.toFixed(1)}%</span>
              <span style={{ color: 'var(--red)'  }}>{redW.toFixed(1)}%</span>
            </div>

            <div className={styles.chips}>
              <div className={styles.chip}><div className={styles.chipLabel}>MODEL</div><div className={styles.chipVal}>Neural Net v1.0</div></div>
              <div className={styles.chip}><div className={styles.chipLabel}>CREDITS AFTER</div><div className={styles.chipVal} style={{ color: 'var(--gold)' }}>{credits - 1}</div></div>
            </div>
          </div>

          <div className={styles.actions}>
            <Button fullWidth onClick={handlePredict} disabled={loading}>
              {loading ? 'Running...' : 'Run Prediction'}
            </Button>
            <Button variant="ghost" onClick={() => setForm(DEFAULT_FORM)}>Clear</Button>
          </div>
        </div>

      </div>
    </AppLayout>
  )
}
