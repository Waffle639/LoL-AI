import { useEffect } from 'react'
import anime from 'animejs'
import AppLayout from '@/components/layout/AppLayout'
import Panel, { PanelTitle } from '@/components/ui/Panel'
import Badge from '@/components/ui/Badge'
import styles from './Models.module.css'

// ─────────────────────────────────────────────────────────────────
// Models
// Neural Network + Random Forest metrics
// Accuracy bars animate from 0 on entry
// DVC version history table
// ─────────────────────────────────────────────────────────────────

const MODELS = [
  {
    name:    'Neural Network',
    type:    'nn',
    subtype: 'PyTorch · In-game · neural_net_v1.pth',
    endpoint:'/predict',
    badgeV:  'teal',
    stats: [
      { key: 'ACCURACY', val: '97.76%', barW: 97.76, barId: 'nn-bar', color: 'var(--teal)' },
      { key: 'ROC-AUC',  val: '0.9968', barW: 99.68, barId: 'nn-bar2' },
    ],
    meta: [
      { key: 'ARCHITECTURE', val: '24 → 64 → 32 → 1' },
      { key: 'DROPOUT',      val: '0.2' },
      { key: 'OPTIMIZER',    val: 'Adam' },
    ],
  },
  {
    name:    'Random Forest',
    type:    'rf',
    subtype: 'scikit-learn · Pre-game · pregame_rf_v1.pkl',
    endpoint:'/predict/pregame',
    badgeV:  'gold',
    stats: [
      { key: 'ACCURACY', val: '76.75%', barW: 76.75, barId: 'rf-bar', color: 'var(--gold)' },
      { key: 'ROC-AUC',  val: '0.8955', barW: 89.55, barId: 'rf-bar2' },
    ],
    meta: [
      { key: 'N_ESTIMATORS', val: '200' },
      { key: 'MAX_DEPTH',    val: '15' },
      { key: 'DATASET',      val: '12,276 rows' },
    ],
  },
]

const VERSION_ROWS = [
  { v: 'v1.0.0', name: 'Neural Network', acc: '97.76%', auc: '0.9968', rows: '12,276', accColor: 'var(--teal)' },
  { v: 'v1.0.0', name: 'Random Forest',  acc: '76.75%', auc: '0.8955', rows: '12,276', accColor: 'var(--gold)' },
]

export default function Models() {
  useEffect(() => {
    anime({ targets: '.metric-panel', opacity:[0,1], translateX:(el,i)=>[i===0?-26:26,0], duration:560, delay: anime.stagger(70), easing:'easeOutExpo' })
    anime({ targets: '#nn-bar',  width:['0%','97.76%'], duration:1050, delay:400,  easing:'easeOutExpo' })
    anime({ targets: '#nn-bar2', width:['0%','99.68%'], duration:950,  delay:450,  easing:'easeOutExpo' })
    anime({ targets: '#rf-bar',  width:['0%','76.75%'], duration:960,  delay:540,  easing:'easeOutExpo' })
    anime({ targets: '#rf-bar2', width:['0%','89.55%'], duration:900,  delay:580,  easing:'easeOutExpo' })
    anime({ targets: '.m-row',   opacity:[0,1], translateY:[5,0], delay: anime.stagger(50,{start:480}), duration:280, easing:'easeOutExpo' })
    anime({ targets: '#s-models tbody tr', opacity:[0,1], translateX:[-8,0], delay: anime.stagger(90,{start:850}), duration:320, easing:'easeOutExpo' })
  }, [])

  return (
    <AppLayout>
      <div id="s-models">
        <h1 className="sec-title">ML Models</h1>
        <p className="sec-sub">Metrics &nbsp;·&nbsp; Architecture &nbsp;·&nbsp; DVC versioning via DagsHub</p>

        <div className={styles.metricsGrid}>
          {MODELS.map(m => (
            <div key={m.type} className={`metric-panel ${styles.panel} ${styles[m.type]}`}>
              <div className={`${styles.modelName} ${styles[`name-${m.type}`]}`}>{m.name}</div>
              <div className={styles.modelType}>{m.subtype}</div>

              {m.stats.map((s, i) => (
                <div key={i}>
                  <div className={`m-row ${styles.mRow}`}>
                    <span className={styles.mKey}>{s.key}</span>
                    <span className={styles.mVal} style={{ color: s.color || 'var(--txt)' }}>{s.val}</span>
                  </div>
                  <div className={styles.accBar}>
                    <div id={s.barId} className={`${styles.accFill} ${styles[m.type]}`} style={{ width: 0 }} />
                  </div>
                </div>
              ))}

              {m.meta.map((r, i) => (
                <div key={i} className={`m-row ${styles.mRow}`}>
                  <span className={styles.mKey}>{r.key}</span>
                  <span className={styles.mVal} style={{ fontSize: 13 }}>{r.val}</span>
                </div>
              ))}

              <div className={`m-row ${styles.mRow}`}>
                <span className={styles.mKey}>ENDPOINT</span>
                <Badge variant={m.badgeV}>{m.endpoint}</Badge>
              </div>
            </div>
          ))}
        </div>

        {/* Version table */}
        <div className={styles.tableWrap}>
          <div className={styles.tableHeader}>
            <span className={styles.tableTitle}>Version History — DVC + DagsHub</span>
            <Badge variant="teal">ACTIVE</Badge>
          </div>
          <table className={styles.table}>
            <thead>
              <tr><th>Version</th><th>Model</th><th>Accuracy</th><th>ROC-AUC</th><th>Dataset</th><th>Status</th></tr>
            </thead>
            <tbody>
              {VERSION_ROWS.map((r, i) => (
                <tr key={i}>
                  <td className={styles.mono}>{r.v}</td>
                  <td>{r.name}</td>
                  <td className={styles.mono} style={{ color: r.accColor }}>{r.acc}</td>
                  <td className={styles.mono}>{r.auc}</td>
                  <td className={styles.mono}>{r.rows} rows</td>
                  <td><Badge variant="green">ACTIVE</Badge></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </AppLayout>
  )
}
