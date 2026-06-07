import { useState, useEffect } from 'react'
import anime from 'animejs'
import AppLayout from '@/components/layout/AppLayout'
import Panel, { PanelTitle } from '@/components/ui/Panel'
import FormField from '@/components/ui/FormField'
import SearchSelect from '@/components/ui/SearchSelect'
import Button from '@/components/ui/Button'
import { useApp } from '@/context/AppContext'
import { getChampionIconUrl } from '@/utils/championIcons'
import styles from './PredictLive.module.css'

// ─────────────────────────────────────────────────────────────────
// PredictLive  —  POST /predict
// Neural Network (24→64→32→1) · Accuracy 97.76%
// ─────────────────────────────────────────────────────────────────

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const API_KEY_STORAGE = 'lol_ai_predict_api_key'

const DEFAULT_FORM = {
  apiKey: '',
  team: '',
  player: '',
  champion: '',
  side: '',
  position: '',
  team_winrate: '',
  player_winrate: '',
  player_kda: '',
  champion_winrate: '',
  player_champ_winrate: '',
  kills: '',
  deaths: '',
  assists: '',
  teamkills: '',
  teamdeaths: '',
  dragons: '',
  opp_dragons: '',
  elders: '',
  opp_elders: '',
  barons: '',
  opp_barons: '',
  towers: '',
  opp_towers: '',
  totalgold: '',
}

const PERFORMANCE_FIELDS = [
  { key: 'team_winrate', label: 'Team Winrate', min: 0, max: 1, step: 0.01, placeholder: '0.65' },
  { key: 'player_winrate', label: 'Player Winrate', min: 0, max: 1, step: 0.01, placeholder: '0.58' },
  { key: 'player_kda', label: 'Player KDA', min: 0, step: 0.1, placeholder: '3.2' },
  { key: 'champion_winrate', label: 'Champion Winrate', min: 0, max: 1, step: 0.01, placeholder: '0.52' },
  { key: 'player_champ_winrate', label: 'Player+Champ Winrate', min: 0, max: 1, step: 0.01, placeholder: '0.71' },
]

const COMBAT_FIELDS = [
  { key: 'kills', label: 'Kills', min: 0, max: 30, step: 1 },
  { key: 'deaths', label: 'Deaths', min: 0, max: 30, step: 1 },
  { key: 'assists', label: 'Assists', min: 0, max: 40, step: 1 },
]

const TEAM_FIELDS = [
  { key: 'teamkills', label: 'Team Kills', min: 0, max: 80, step: 1 },
  { key: 'teamdeaths', label: 'Team Deaths', min: 0, max: 80, step: 1 },
  { key: 'totalgold', label: 'Total Gold', min: 0, step: 1, placeholder: '15000' },
]

const OBJECTIVE_FIELDS = [
  { key: 'dragons', label: 'Dragons', min: 0, max: 5, step: 1 },
  { key: 'opp_dragons', label: 'Opp. Dragons', min: 0, max: 5, step: 1 },
  { key: 'elders', label: 'Elders', min: 0, max: 3, step: 1 },
  { key: 'opp_elders', label: 'Opp. Elders', min: 0, max: 3, step: 1 },
  { key: 'barons', label: 'Barons', min: 0, max: 5, step: 1 },
  { key: 'opp_barons', label: 'Opp. Barons', min: 0, max: 5, step: 1 },
  { key: 'towers', label: 'Towers', min: 0, max: 11, step: 1 },
  { key: 'opp_towers', label: 'Opp. Towers', min: 0, max: 11, step: 1 },
]

const SIDE_OPTIONS = [
  { value: 'Blue', label: 'Blue Side', tone: 'blue' },
  { value: 'Red', label: 'Red Side', tone: 'red' },
]

const ROLE_ICON_PATHS = {
  top: 'M12 3l8 8h-5v10H9V11H4l8-8z',
  jng: 'M12 3c4 1 7 5 7 9 0 4-3 8-7 9-4-1-7-5-7-9 0-4 3-8 7-9z',
  mid: 'M12 3l9 9-9 9-9-9 9-9z',
  bot: 'M12 21l-8-8h5V3h6v10h5l-8 8z',
  sup: 'M12 3l2.6 5.2 5.7.8-4.1 4 1 5.6L12 16.8 6.8 18.6l1-5.6-4.1-4 5.7-.8L12 3z',
}

const ROLE_OPTIONS = [
  { value: 'top', label: 'Top' },
  { value: 'jng', label: 'Jungle' },
  { value: 'mid', label: 'Mid' },
  { value: 'bot', label: 'Bot' },
  { value: 'sup', label: 'Support' },
]

function RoleIcon({ role }) {
  const path = ROLE_ICON_PATHS[role]
  if (!path) return null
  return (
    <svg viewBox="0 0 24 24" className={styles.roleIcon} aria-hidden="true">
      <path d={path} />
    </svg>
  )
}

export default function PredictLive() {
  const { credits, consumeCredit, setCredits } = useApp()
  const [form, setForm] = useState(DEFAULT_FORM)
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [fieldErrors, setFieldErrors] = useState({})
  const [errorPulse, setErrorPulse] = useState(false)
  const [statsLoading, setStatsLoading] = useState(false)
  const [statsError, setStatsError] = useState('')
  const [confirmState, setConfirmState] = useState(null)
  const [options, setOptions] = useState({
    teams: [],
    players: [],
    champions: [],
  })
  const [optionsLoading, setOptionsLoading] = useState(false)
  const [optionsError, setOptionsError] = useState('')

  const setField = (key, value) => {
    setForm(current => ({ ...current, [key]: value }))
    setFieldErrors(current => {
      if (!current[key]) return current
      const next = { ...current }
      delete next[key]
      return next
    })
  }

  useEffect(() => {
    anime({ targets: '#pl-left .panel', opacity:[0,1], translateX:[-18,0], delay: anime.stagger(90), duration:480, easing:'easeOutExpo' })
    anime({ targets: '#pl-result', opacity:[0,1], translateY:[18,0], delay:280, duration:560, easing:'easeOutExpo' })
  }, [])

  useEffect(() => {
    const storedKey = localStorage.getItem(API_KEY_STORAGE)
    if (storedKey) {
      setForm(current => ({ ...current, apiKey: storedKey }))
    }
  }, [])

  useEffect(() => {
    if (form.apiKey) {
      localStorage.setItem(API_KEY_STORAGE, form.apiKey)
    } else {
      localStorage.removeItem(API_KEY_STORAGE)
    }
  }, [form.apiKey])

  useEffect(() => {
    let active = true
    const loadOptions = async () => {
      setOptionsLoading(true)
      setOptionsError('')
      try {
        const res = await fetch(`${API_BASE_URL}/predict/options`)
        const data = await res.json().catch(() => null)
        if (!res.ok) {
          throw new Error('Unable to load options')
        }
        if (!active) return
        setOptions(current => ({
          ...current,
          teams: Array.isArray(data?.teams) ? data.teams : current.teams,
          players: Array.isArray(data?.players) ? data.players : current.players,
          champions: Array.isArray(data?.champions) ? data.champions : current.champions,
        }))
      } catch (err) {
        if (active) setOptionsError(err.message || 'Unable to load options')
      } finally {
        if (active) setOptionsLoading(false)
      }
    }

    loadOptions()
    return () => {
      active = false
    }
  }, [])

  useEffect(() => {
    let active = true
    const loadStats = async () => {
      if (!form.team?.trim() || !form.player?.trim() || !form.champion?.trim()) return

      setStatsLoading(true)
      setStatsError('')
      try {
        const params = new URLSearchParams({
          team: form.team.trim(),
          player: form.player.trim(),
          champion: form.champion.trim(),
        })
        const res = await fetch(`${API_BASE_URL}/predict/stats?${params.toString()}`)
        const data = await res.json().catch(() => null)
        if (!res.ok) {
          throw new Error('Unable to load historical stats')
        }
        if (!active) return

        const format = (value, digits = 2) => {
          const num = Number(value)
          return Number.isFinite(num) ? num.toFixed(digits) : ''
        }

        setForm(current => ({
          ...current,
          team: data?.team || current.team,
          player: data?.player || current.player,
          champion: data?.champion || current.champion,
          team_winrate: format(data?.team_winrate),
          player_winrate: format(data?.player_winrate),
          player_kda: format(data?.player_kda, 2),
          champion_winrate: format(data?.champion_winrate),
          player_champ_winrate: format(data?.player_champ_winrate),
        }))
      } catch (err) {
        if (active) setStatsError(err.message || 'Unable to load historical stats')
      } finally {
        if (active) setStatsLoading(false)
      }
    }

    loadStats()
    return () => {
      active = false
    }
  }, [form.team, form.player, form.champion])

  const triggerResultAnimation = () => {
    const burst = document.getElementById('predict-burst')
    if (burst) {
      burst.innerHTML = ''
      for (let i = 0; i < 16; i++) {
        const p = document.createElement('div')
        p.style.cssText = `position:absolute;width:${Math.random() * 5 + 3}px;height:${Math.random() * 5 + 3}px;border-radius:${Math.random() > .5 ? '50%' : '2px'};background:${Math.random() > .5 ? '#0AC8B9' : '#C8A96E'};left:50%;top:50%;pointer-events:none;`
        burst.appendChild(p)
      }
      anime({ targets:'#predict-burst > div', translateX:()=>anime.random(-110,110), translateY:()=>anime.random(-70,70), scale:[1,0], opacity:[1,0], duration:()=>anime.random(480,850), easing:'easeOutExpo' })
    }
    anime({ targets:'#pl-result', borderColor:['rgba(10,200,185,.8)','rgba(200,169,110,.18)'], duration:750, easing:'easeOutExpo' })
    anime({ targets:'#r-team-name', scale:[.65,1.06,1], opacity:[0,1], duration:560, easing:'easeOutBack' })
  }

  const validateForm = () => {
    const nextErrors = {}

    if (!form.apiKey?.trim()) {
      nextErrors.apiKey = 'Required'
    }

    const requiredText = ['team', 'player', 'champion', 'side', 'position']
    requiredText.forEach((key) => {
      if (!form[key]?.toString().trim()) {
        nextErrors[key] = 'Required'
      }
    })

    const numericFields = [...PERFORMANCE_FIELDS, ...COMBAT_FIELDS, ...TEAM_FIELDS, ...OBJECTIVE_FIELDS]
    for (const field of numericFields) {
      const raw = form[field.key]
      if (raw === '' || raw === null || raw === undefined) {
        nextErrors[field.key] = 'Required'
        continue
      }
      const value = Number(raw)
      if (!Number.isFinite(value)) {
        nextErrors[field.key] = 'Invalid number'
        continue
      }
      if (field.min !== undefined && value < field.min) {
        nextErrors[field.key] = 'Out of range'
        continue
      }
      if (field.max !== undefined && value > field.max) {
        nextErrors[field.key] = 'Out of range'
      }
    }

    return {
      valid: Object.keys(nextErrors).length === 0,
      errors: nextErrors,
    }
  }

  const buildPayload = () => ({
    team_encoded: form.team.trim(),
    player_encoded: form.player.trim(),
    champion_encoded: form.champion.trim(),
    side_encoded: form.side.trim(),
    position_encoded: form.position.trim(),
    team_winrate: Number(form.team_winrate),
    player_winrate: Number(form.player_winrate),
    player_kda: Number(form.player_kda),
    champion_winrate: Number(form.champion_winrate),
    player_champ_winrate: Number(form.player_champ_winrate),
    kills: Number(form.kills),
    deaths: Number(form.deaths),
    assists: Number(form.assists),
    teamkills: Number(form.teamkills),
    teamdeaths: Number(form.teamdeaths),
    dragons: Number(form.dragons),
    opp_dragons: Number(form.opp_dragons),
    elders: Number(form.elders),
    opp_elders: Number(form.opp_elders),
    barons: Number(form.barons),
    opp_barons: Number(form.opp_barons),
    towers: Number(form.towers),
    opp_towers: Number(form.opp_towers),
    totalgold: Number(form.totalgold),
  })

  const openConfirm = (config) => {
    setConfirmState(config)
  }

  const closeConfirm = () => {
    setConfirmState(null)
  }

  const confirmAction = () => {
    const action = confirmState?.onConfirm
    closeConfirm()
    action?.()
  }

  const requestPrediction = () => {
    setError('')
    const validation = validateForm()
    setFieldErrors(validation.errors)
    if (!validation.valid) {
      setError('Please review the highlighted fields.')
      setErrorPulse(true)
      setTimeout(() => setErrorPulse(false), 520)
      return
    }

    openConfirm({
      title: 'Run prediction?',
      message: 'This will consume 1 credit.',
      confirmLabel: 'Run prediction',
      onConfirm: runPrediction,
    })
  }

  const runPrediction = async () => {
    setLoading(true)
    try {
      const res = await fetch(`${API_BASE_URL}/predict`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
          'X-API-Key': form.apiKey.trim(),
        },
        body: JSON.stringify(buildPayload()),
      })
      const data = await res.json().catch(() => null)
      if (!res.ok) {
        throw new Error('Prediction failed. Check your API key and inputs.')
      }

      const rawProb = Number(data?.probability ?? 0)
      const probPct = Math.round(rawProb * 10000) / 100
      const victory = data?.result_label === 'Victory' || data?.prediction === 1
      setResult({
        prob: probPct,
        victory,
        label: data?.result_label || (victory ? 'Victory' : 'Defeat'),
        modelVersion: data?.model_version || '1.0.0',
        creditsRemaining: data?.credits_remaining,
      })

      if (typeof data?.credits_remaining === 'number') {
        setCredits(data.credits_remaining)
      } else {
        consumeCredit()
      }

      setTimeout(triggerResultAnimation, 80)
    } catch (err) {
      setError(err.message || 'Prediction failed. Check your API key and inputs.')
    } finally {
      setLoading(false)
    }
  }

  const handleClear = () => {
    setForm(DEFAULT_FORM)
    setResult(null)
    setError('')
    setStatsError('')
    setStatsLoading(false)
    setFieldErrors({})
    localStorage.removeItem(API_KEY_STORAGE)
  }

  const requestClear = () => {
    openConfirm({
      title: 'Clear all fields?',
      message: 'This will reset the form and remove your stored API key.',
      confirmLabel: 'Clear form',
      onConfirm: handleClear,
    })
  }

  const probValue = result?.prob ?? 50
  const blueW = probValue
  const redW = 100 - probValue
  const teamLabel = form.team?.trim() || 'Team'
  const oppLabel = 'Opponent'
  const resultTitle = result?.label || 'Awaiting Prediction'
  const resultColor = result ? (result.victory ? 'var(--teal)' : 'var(--red)') : 'var(--txt-d)'
  const creditsAfter = typeof result?.creditsRemaining === 'number'
    ? result.creditsRemaining
    : Math.max(0, credits - (loading ? 0 : 1))

  return (
    <AppLayout>
      <h1 className="sec-title">Predict Live</h1>
      <p className="sec-sub">In-game state &nbsp;·&nbsp; Neural Network &nbsp;·&nbsp; 1 credit</p>

      <div className={styles.grid}>

        {/* Form column */}
        <div id="pl-left" className={`${styles.formStack} ${errorPulse ? styles.flashErrors : ''}`.trim()}>
          <Panel accent="gold" className="panel">
            <PanelTitle>Player Identity</PanelTitle>
            <SearchSelect
              label="Team"
              value={form.team}
              onChange={value => setField('team', value)}
              options={options.teams}
              placeholder="Search team..."
              invalid={Boolean(fieldErrors.team)}
            />
            <SearchSelect
              label="Player"
              value={form.player}
              onChange={value => setField('player', value)}
              options={options.players}
              placeholder="Search player..."
              invalid={Boolean(fieldErrors.player)}
            />
            <SearchSelect
              label="Champion"
              value={form.champion}
              onChange={value => setField('champion', value)}
              options={options.champions}
              placeholder="Search champion..."
              iconResolver={getChampionIconUrl}
              invalid={Boolean(fieldErrors.champion)}
            />
            <div className={styles.choiceSection}>
              <div className={styles.choiceLabel}>Side</div>
              <div className={styles.sideGrid}>
                {SIDE_OPTIONS.map(option => (
                  <button
                    key={option.value}
                    type="button"
                    className={`${styles.choiceCard} ${styles[`choiceCard-${option.tone}`]} ${form.side === option.value ? styles.choiceCardActive : ''} ${fieldErrors.side ? styles.choiceCardError : ''}`}
                    onClick={() => setField('side', option.value)}
                    aria-pressed={form.side === option.value}
                  >
                    <span className={styles.choiceTitle}>{option.label}</span>
                    <span className={styles.choiceTag}>{option.value}</span>
                  </button>
                ))}
              </div>
            </div>

            <div className={styles.choiceSection}>
              <div className={styles.choiceLabel}>Lane</div>
              <div className={styles.roleGrid}>
                {ROLE_OPTIONS.map(role => (
                  <button
                    key={role.value}
                    type="button"
                    className={`${styles.roleCard} ${form.position === role.value ? styles.roleCardActive : ''} ${fieldErrors.position ? styles.roleCardError : ''}`}
                    onClick={() => setField('position', role.value)}
                    aria-pressed={form.position === role.value}
                  >
                    <RoleIcon role={role.value} />
                    <span className={styles.roleLabel}>{role.label}</span>
                  </button>
                ))}
              </div>
            </div>
            {optionsLoading ? <div className={styles.panelNote}>Loading model options...</div> : null}
            {optionsError ? <div className={styles.panelNote}>{optionsError}</div> : null}
          </Panel>

          <Panel accent="teal" className="panel">
            <PanelTitle>Live Match Stats</PanelTitle>
            <div className={styles.panelTag}>Player Combat</div>
            <div className={styles.threeCol}>
              {COMBAT_FIELDS.map(field => (
                <FormField
                  key={field.key}
                  label={field.label}
                  type="number"
                  value={form[field.key]}
                  onChange={event => setField(field.key, event.target.value)}
                  min={field.min}
                  max={field.max}
                  step={field.step}
                  inputMode="numeric"
                  inputClassName={`${styles.numericInput} ${fieldErrors[field.key] ? styles.inputError : ''}`.trim()}
                />
              ))}
            </div>

            <div className={styles.panelTag}>Team Totals</div>
            <div className={styles.threeCol}>
              {TEAM_FIELDS.map(field => (
                <FormField
                  key={field.key}
                  label={field.label}
                  type="number"
                  value={form[field.key]}
                  onChange={event => setField(field.key, event.target.value)}
                  min={field.min}
                  max={field.max}
                  step={field.step}
                  inputMode="decimal"
                  placeholder={field.placeholder}
                  inputClassName={`${styles.numericInput} ${fieldErrors[field.key] ? styles.inputError : ''}`.trim()}
                />
              ))}
            </div>

            <div className={styles.panelTag}>Objectives</div>
            <div className={styles.statsGridTwo}>
              {OBJECTIVE_FIELDS.map(field => (
                <FormField
                  key={field.key}
                  label={field.label}
                  type="number"
                  value={form[field.key]}
                  onChange={event => setField(field.key, event.target.value)}
                  min={field.min}
                  max={field.max}
                  step={field.step}
                  inputMode="numeric"
                  inputClassName={`${styles.numericInput} ${fieldErrors[field.key] ? styles.inputError : ''}`.trim()}
                />
              ))}
            </div>
          </Panel>
        </div>

        {/* Result column */}
        <div>
          <div className={styles.resultCard} id="pl-result">
            <div id="predict-burst" className={styles.burst} />
            <div className={styles.resultHeader}>
              <div className={styles.resultLabel}>NEURAL NETWORK PREDICTION</div>
              <button
                type="button"
                className={styles.trashButton}
                onClick={requestClear}
                aria-label="Clear form"
              >
                <svg viewBox="0 0 24 24" aria-hidden="true">
                  <path d="M9 3h6l1 2h4v2H4V5h4l1-2zm1 6h2v8h-2V9zm4 0h2v8h-2V9zM7 9h2v8H7V9zm2 12h6a2 2 0 0 0 2-2V7H7v12a2 2 0 0 0 2 2z" />
                </svg>
              </button>
            </div>
            <div className={styles.resultTeam} id="r-team-name" style={{ color: resultColor }}>
              {resultTitle}
            </div>
            <div className={styles.resultProb}>
              {result ? `${result.prob}% win probability` : 'Awaiting input'}
            </div>

            <div className={styles.vsTrack}>
              <div className={styles.vsBlue} style={{ flex: blueW }} />
              <div className={styles.vsRed} style={{ flex: redW }} />
            </div>
            <div className={styles.vsLabels}>
              <span style={{ color: 'var(--teal)' }}>{teamLabel} {blueW.toFixed(1)}%</span>
              <span style={{ color: 'var(--red)' }}>{oppLabel} {redW.toFixed(1)}%</span>
            </div>

            <div className={styles.chips}>
              <div className={styles.chip}>
                <div className={styles.chipLabel}>MODEL</div>
                <div className={styles.chipVal}>{result?.modelVersion || 'Neural Net v1.0'}</div>
              </div>
              <div className={styles.chip}>
                <div className={styles.chipLabel}>CREDITS AFTER</div>
                <div className={styles.chipVal} style={{ color: 'var(--gold)' }}>{creditsAfter}</div>
              </div>
            </div>
          </div>

          <div className={styles.actions}>
            <Button fullWidth onClick={requestPrediction} disabled={loading || statsLoading}>
              {loading ? 'Running...' : 'Run Prediction'}
            </Button>
          </div>
          {error ? <div className={styles.errorText}>{error}</div> : null}

          <Panel accent="gold" className={`${styles.secondaryPanel} ${styles.compactPanel}`}>
            <PanelTitle>API Key</PanelTitle>
            <FormField
              label="X-API-Key"
              type="password"
              value={form.apiKey}
              onChange={event => setField('apiKey', event.target.value)}
              placeholder="lol_xxxxxxxxxxxxx"
              autoComplete="off"
              inputClassName={fieldErrors.apiKey ? styles.inputError : ''}
            />
            <div className={styles.panelNote}>Stored locally in this browser.</div>
          </Panel>

          <Panel accent="none" className={`${styles.secondaryPanel} ${styles.compactPanel} ${styles.mutedPanel}`}>
            <PanelTitle>Pre-Game Performance</PanelTitle>
            {statsLoading ? <div className={styles.panelNote}>Loading historical stats...</div> : null}
            {statsError ? <div className={styles.errorText}>{statsError}</div> : null}
            <div className={styles.statsGridCompact}>
              {PERFORMANCE_FIELDS.map(field => (
                <FormField
                  key={field.key}
                  label={field.label}
                  type="number"
                  value={form[field.key]}
                  onChange={event => setField(field.key, event.target.value)}
                  min={field.min}
                  max={field.max}
                  step={field.step}
                  inputMode="decimal"
                  placeholder={field.placeholder}
                  readOnly
                  inputClassName={`${styles.numericInput} ${styles.lockedInput} ${fieldErrors[field.key] ? styles.inputError : ''}`.trim()}
                />
              ))}
            </div>
          </Panel>
        </div>

      </div>
      {confirmState ? (
        <div className={styles.modalOverlay} role="dialog" aria-modal="true">
          <div className={styles.modalCard}>
            <div className={styles.modalTitle}>{confirmState.title}</div>
            <div className={styles.modalText}>{confirmState.message}</div>
            <div className={styles.modalActions}>
              <Button variant="ghost" size="sm" onClick={closeConfirm}>Cancel</Button>
              <Button size="sm" onClick={confirmAction}>{confirmState.confirmLabel}</Button>
            </div>
          </div>
        </div>
      ) : null}
    </AppLayout>
  )
}
