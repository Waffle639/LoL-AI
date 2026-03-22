import { useState, useEffect } from 'react'
import anime from 'animejs'
import AppLayout from '@/components/layout/AppLayout'
import Badge from '@/components/ui/Badge'
import Button from '@/components/ui/Button'
import styles from './History.module.css'

// ─────────────────────────────────────────────────────────────────
// History
// Full prediction log with search, filter, export
// Rows animate in as a data stream on enter
// ─────────────────────────────────────────────────────────────────

const ALL_ROWS = [
  { id: 127, t1: 'G2 Esports',   t2: 'MAD Lions',   type: 'PRE',  winner: 'G2',     prob: 77.8, model: 'RF v1',  date: '11/03 14:22', result: 'win'  },
  { id: 126, t1: 'T1',           t2: 'Gen.G',        type: 'LIVE', winner: 'T1',     prob: 87.3, model: 'NN v1',  date: '11/03 11:05', result: 'win'  },
  { id: 125, t1: 'Cloud9',       t2: 'Team Liquid',  type: 'LIVE', winner: 'C9',     prob: 34.1, model: 'NN v1',  date: '10/03 22:44', result: 'loss' },
  { id: 124, t1: 'Fnatic',       t2: 'NaVi',         type: 'PRE',  winner: 'FNC',    prob: 61.2, model: 'RF v1',  date: '10/03 19:30', result: 'win'  },
  { id: 123, t1: '100 Thieves',  t2: 'TSM',          type: 'LIVE', winner: '100T',   prob: 70.4, model: 'NN v1',  date: '10/03 17:12', result: 'win'  },
  { id: 122, t1: 'BLG',          t2: 'JDG',          type: 'PRE',  winner: 'BLG',    prob: 42.6, model: 'RF v1',  date: '09/03 20:00', result: 'loss' },
  { id: 121, t1: 'KT Rolster',   t2: 'DRX',          type: 'LIVE', winner: 'KT',     prob: 68.9, model: 'NN v1',  date: '09/03 15:45', result: 'win'  },
]

export default function History() {
  const [search, setSearch]       = useState('')
  const [typeFilter, setTypeFilter] = useState('ALL')

  useEffect(() => {
    anime({ targets: '.sec-title, .sec-sub', opacity:[0,1], translateY:[-7,0], delay: anime.stagger(55), duration:320, easing:'easeOutExpo' })
    anime({ targets: 'th',                   opacity:[0,1], translateY:[-4,0], delay: anime.stagger(25,{start:150}), duration:220, easing:'easeOutExpo' })
    anime({ targets: '.hist-row',            opacity:[0,1], translateX:[-12,0], delay: anime.stagger(80,{start:300}), duration:350, easing:'easeOutExpo' })
  }, [])

  const rows = ALL_ROWS.filter(r => {
    const matchSearch = r.t1.toLowerCase().includes(search.toLowerCase()) || r.t2.toLowerCase().includes(search.toLowerCase())
    const matchType   = typeFilter === 'ALL' || r.type === typeFilter
    return matchSearch && matchType
  })

  return (
    <AppLayout>
      <h1 className="sec-title">Prediction History</h1>
      <p className="sec-sub">127 predictions &mdash; filter and export</p>

      {/* Controls */}
      <div className={styles.controls}>
        <input
          className={styles.search}
          placeholder="Search team or player..."
          value={search}
          onChange={e => setSearch(e.target.value)}
        />
        {['ALL', 'LIVE', 'PRE'].map(t => (
          <button
            key={t}
            className={`${styles.typeBtn} ${typeFilter === t ? styles.typeBtnActive : ''}`}
            onClick={() => setTypeFilter(t)}
          >
            {t}
          </button>
        ))}
        <div className={styles.spacer} />
        <Button variant="ghost" size="sm">Export CSV</Button>
      </div>

      {/* Table */}
      <div className={styles.tableWrap}>
        <table className={styles.table}>
          <thead>
            <tr>
              <th>#</th><th>Team 1</th><th>Team 2</th><th>Type</th>
              <th>Winner</th><th>Prob.</th><th>Model</th><th>Date</th><th />
            </tr>
          </thead>
          <tbody>
            {rows.map(r => (
              <tr key={r.id} className="hist-row">
                <td className={styles.mono}>#{r.id}</td>
                <td>{r.t1}</td>
                <td>{r.t2}</td>
                <td><Badge variant={r.type === 'PRE' ? 'teal' : 'gold'}>{r.type}</Badge></td>
                <td className={r.result === 'win' ? styles.win : styles.loss}>{r.winner}</td>
                <td className={styles.mono}>{r.prob}%</td>
                <td className={styles.mono}>{r.model}</td>
                <td className={styles.mono}>{r.date}</td>
                <td><Button variant="ghost" size="sm">View</Button></td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Pagination */}
      <div className={styles.pagination}>
        <Button variant="ghost" size="sm">Prev</Button>
        <Button size="sm">1</Button>
        <Button variant="ghost" size="sm">2</Button>
        <Button variant="ghost" size="sm">3</Button>
        <Button variant="ghost" size="sm">Next</Button>
      </div>
    </AppLayout>
  )
}
