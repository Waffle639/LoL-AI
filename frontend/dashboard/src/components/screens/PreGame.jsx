import { useState, useEffect, useCallback, useMemo, useRef } from 'react'
import anime from 'animejs'
import Topbar from '@/components/layout/Topbar'
import { useApp } from '@/context/AppContext'
import { getChampionIconUrl } from '@/utils/championIcons'
import { CHAMPIONS, POSITIONS } from '@/constants/champions'
import styles from './PreGame.module.css'

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'
const EMPTY_SLOT = { player: '', champion: '' }
const makeTeam = (side) => ({
  team_name: '',
  side,
  players: POSITIONS.map(() => ({ ...EMPTY_SLOT })),
})
const ROLES = ['ALL', 'top', 'jng', 'mid', 'bot', 'sup']

export default function PreGame() {
  const { getAccessToken, consumeCredit, credits } = useApp()

  const [options, setOptions] = useState({ teams: [], players: [], champions: [] })
  const [blue, setBlue] = useState(makeTeam('Blue'))
  const [red, setRed] = useState(makeTeam('Red'))

  const [activeSlot, setActiveSlot] = useState(null)       // { team, index }
  const [searchingSlot, setSearchingSlot] = useState(null)  // { team, index }
  const [playerSearch, setPlayerSearch] = useState('')
  const [roleFilter, setRoleFilter] = useState('ALL')
  const [champSearch, setChampSearch] = useState('')
  const [searchingTeam, setSearchingTeam] = useState(null)  // 'blue' | 'red'
  const [teamSearch, setTeamSearch] = useState('')

  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [result, setResult] = useState(null)

  const dropdownRef = useRef(null)
  const searchInputRef = useRef(null)
  const teamDropdownRef = useRef(null)
  const teamSearchInputRef = useRef(null)

  // ── Load options ──
  useEffect(() => {
    let active = true
    ;(async () => {
      try {
        const res = await fetch(`${API_BASE_URL}/predict/options`)
        if (!res.ok) throw new Error('Failed to load')
        const data = await res.json()
        if (!active) return
        setOptions({
          teams: Array.isArray(data?.teams) ? data.teams : [],
          players: Array.isArray(data?.players) ? data.players : [],
          champions: Array.isArray(data?.champions) ? data.champions : [],
        })
      } catch {
        if (active) setError('Could not load data from server.')
      }
    })()
    return () => { active = false }
  }, [])

  // ── Focus search inputs when dropdowns open ──
  useEffect(() => {
    if (searchingSlot && searchInputRef.current) {
      searchInputRef.current.focus()
    }
  }, [searchingSlot])
  useEffect(() => {
    if (searchingTeam && teamSearchInputRef.current) {
      teamSearchInputRef.current.focus()
    }
  }, [searchingTeam])

  // ── Close player dropdown on outside click ──
  useEffect(() => {
    if (!searchingSlot) return
    const handler = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setSearchingSlot(null)
        setPlayerSearch('')
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [searchingSlot])

  // ── Close team dropdown on outside click ──
  useEffect(() => {
    if (!searchingTeam) return
    const handler = (e) => {
      if (teamDropdownRef.current && !teamDropdownRef.current.contains(e.target)) {
        setSearchingTeam(null)
        setTeamSearch('')
      }
    }
    document.addEventListener('mousedown', handler)
    return () => document.removeEventListener('mousedown', handler)
  }, [searchingTeam])

  // ── Animations ──
  useEffect(() => {
    anime({ targets: '.pg-panel', opacity:[0,1], translateX:(el,i)=>[i===0?-30:30,0], delay: anime.stagger(80), duration:560, easing:'easeOutExpo' })
    anime({ targets: '.pg-slot', opacity:[0,1], translateY:[10,0], delay: anime.stagger(50,{start:200}), duration:380, easing:'easeOutExpo' })
    anime({ targets: '.pg-champ', opacity:[0,1], scale:[.85,1], delay: anime.stagger(8,{from:'center'}), duration:300, easing:'easeOutBack' })
  }, [])

  // ── Helpers ──
  const teamSetter = useCallback((teamKey) => teamKey === 'blue' ? setBlue : setRed, [])

  const isComplete = useCallback(() => {
    const ok = (t) => t.players.every((p) => p.player && p.champion)
    return ok(blue) && ok(red) && blue.team_name && red.team_name
  }, [blue, red])

  // ── Single click handler for entire slot ──
  const handleSlotClick = useCallback((team, index) => {
    const t = team === 'blue' ? blue : red
    const slot = t.players[index]

    // Slot already active? → toggle off
    if (activeSlot?.team === team && activeSlot?.index === index) {
      setActiveSlot(null)
      setSearchingSlot(null)
      return
    }

    // Slot empty (no player)? → open player search AND activate
    if (!slot.player) {
      setSearchingSlot({ team, index })
      setActiveSlot({ team, index })
      setPlayerSearch('')
      return
    }

    // Slot has player → just activate for champion selection
    setActiveSlot({ team, index })
    setSearchingSlot(null)
  }, [blue, red, activeSlot])

  const selectPlayer = useCallback((name) => {
    if (!searchingSlot) return
    const setter = teamSetter(searchingSlot.team)
    setter((prev) => {
      const next = { ...prev, players: [...prev.players] }
      next.players[searchingSlot.index] = { ...next.players[searchingSlot.index], player: name }
      return next
    })
    // Close the search dropdown, but KEEP the slot active (gold border)
    setSearchingSlot(null)
    setPlayerSearch('')
  }, [searchingSlot, teamSetter])

  const selectChampion = useCallback((id) => {
    if (!activeSlot) return
    const setter = teamSetter(activeSlot.team)
    setter((prev) => {
      const next = { ...prev, players: [...prev.players] }
      next.players[activeSlot.index] = { ...next.players[activeSlot.index], champion: id }
      return next
    })
    // Champion selected → deactivate slot
    setActiveSlot(null)
  }, [activeSlot, teamSetter])

  const setTeamName = useCallback((key, name) => {
    const setter = key === 'blue' ? setBlue : setRed
    setter((p) => ({ ...p, team_name: name }))
  }, [])

  const openTeamSearch = useCallback((teamKey) => {
    setSearchingTeam((prev) => prev === teamKey ? null : teamKey)
    setTeamSearch('')
  }, [])

  const selectTeam = useCallback((teamKey, name) => {
    setTeamName(teamKey, name)
    setSearchingTeam(null)
    setTeamSearch('')
  }, [setTeamName])

  // ── Filtered data ──
  const filteredPlayers = useMemo(() => {
    const q = playerSearch.toLowerCase().trim()
    if (!q) return options.players.slice(0, 20)
    return options.players.filter((p) => p.toLowerCase().includes(q)).slice(0, 20)
  }, [playerSearch, options.players])

  const filteredTeams = useMemo(() => {
    const q = teamSearch.toLowerCase().trim()
    if (!q) return options.teams.slice(0, 15)
    return options.teams.filter((t) => t.toLowerCase().includes(q)).slice(0, 15)
  }, [teamSearch, options.teams])

  const filteredChampions = useMemo(() => {
    const q = champSearch.toLowerCase().trim()
    return CHAMPIONS.filter((c) => {
      const roleOk = roleFilter === 'ALL' || c.role === roleFilter
      const searchOk = !q || c.id.toLowerCase().includes(q)
      return roleOk && searchOk
    })
  }, [champSearch, roleFilter])

  // ── Prediction ──
  const runPrediction = async () => {
    if (!isComplete()) { setError('Complete all 10 slots and both team names.'); return }
    setLoading(true); setError(''); setResult(null)
    try {
      const token = await getAccessToken()
      if (!token) throw new Error('Not authenticated.')
      const build = (t) => ({
        team_name: t.team_name,
        side: t.side,
        players: t.players.map((p, i) => ({ player: p.player, champion: p.champion, position: POSITIONS[i].toLowerCase() })),
      })
      const res = await fetch(`${API_BASE_URL}/predict/pregame`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
        body: JSON.stringify({ team1: build(blue), team2: build(red) }),
      })
      const data = await res.json().catch(() => null)
      if (!res.ok) throw new Error(data?.detail || 'Prediction failed.')
      setResult({ team1: data.team1, team2: data.team2, predicted_winner: data.predicted_winner, confidence: data.confidence, model_version: data.model_version })
      consumeCredit()
      setTimeout(() => {
        anime({ targets: '#pg-result', opacity:[0,1], translateY:[20,0], duration:600, easing:'easeOutExpo' })
        anime({ targets: '.pg-prob-fill', width:(el)=>el.dataset.w, duration:900, easing:'easeOutExpo' })
      }, 50)
    } catch (err) { setError(err.message) }
    finally { setLoading(false) }
  }

  // ── Render slot ──
  const renderSlot = (team, idx) => {
    const t = team === 'blue' ? blue : red
    const slot = t.players[idx]
    const pos = POSITIONS[idx]
    const filled = slot.player && slot.champion
    const isActive = activeSlot?.team === team && activeSlot?.index === idx
    const isSearching = searchingSlot?.team === team && searchingSlot?.index === idx

    const handlePortraitClick = (e) => {
      e.stopPropagation()
      // Always open player search when clicking portrait (change player)
      setSearchingSlot({ team, index: idx })
      setPlayerSearch('')
      // If slot was active, keep it active after player change
      if (isActive) {
        // keep active
      } else if (slot.player) {
        // has player, just open search
      } else {
        // empty slot, also activate
        setActiveSlot({ team, index: idx })
      }
    }

    const handleInfoClick = (e) => {
      e.stopPropagation()
      if (!slot.player) {
        // empty slot → same as portrait click
        setSearchingSlot({ team, index: idx })
        setActiveSlot({ team, index: idx })
        setPlayerSearch('')
        return
      }
      // has player → toggle active for champion selection
      if (isActive) {
        setActiveSlot(null)
      } else {
        setActiveSlot({ team, index: idx })
        setSearchingSlot(null)
      }
    }

    return (
      <div key={pos}
        className={`${styles.slot} pg-slot ${isActive ? styles.slotActive : ''} ${filled ? styles.slotFilled : ''} ${isSearching ? styles.slotSearching : ''}`}>

        <div className={styles.portrait} onClick={handlePortraitClick}>
          {slot.champion ? (
            <img src={getChampionIconUrl(slot.champion)} alt={slot.champion} className={styles.portraitImg}
              onError={(e) => { e.currentTarget.style.display = 'none' }} />
          ) : (
            <div className={styles.portraitPlus}>+</div>
          )}
        </div>

        <div className={`${styles.slotInfo} ${team === 'red' ? styles.slotInfoRight : ''}`} onClick={handleInfoClick}>
          <div className={styles.slotPos}>{pos}</div>
          <div className={`${styles.slotPlayer} ${!slot.player ? styles.slotPlaceholder : ''}`}>
            {slot.player || 'Select player'}
          </div>
          {slot.champion && <div className={styles.slotChamp}>{slot.champion}</div>}
          {isActive && !slot.champion && <div className={styles.activeIndicator}>Select champion ↓</div>}
        </div>

        {/* Inline player search dropdown */}
        {isSearching && (
          <div className={styles.playerDropdown} ref={dropdownRef}
            onClick={(e) => e.stopPropagation()}>
            <input
              ref={searchInputRef}
              className={styles.playerInput}
              placeholder="Search pro player..."
              value={playerSearch}
              onChange={(e) => setPlayerSearch(e.target.value)}
            />
            <div className={styles.playerList}>
              {filteredPlayers.length === 0 && (
                <div className={styles.playerEmpty}>No players found</div>
              )}
              {filteredPlayers.map((p) => (
                <div key={p}
                  className={`${styles.playerItem} ${slot.player === p ? styles.playerItemSelected : ''}`}
                  onClick={() => selectPlayer(p)}>
                  {p}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    )
  }

  // ── Render team panel ──
  const renderPanel = (teamKey) => {
    const t = teamKey === 'blue' ? blue : red
    const prob = result?.[teamKey === 'blue' ? 'team1' : 'team2']?.victory_prob
    const accent = teamKey === 'blue' ? 'var(--teal)' : 'var(--red)'
    const isRight = teamKey === 'red'

    return (
      <div className={`${styles.teamPanel} ${isRight ? styles.teamRight : ''} pg-panel`}>
        {/* Team name */}
        <div className={styles.teamHeader}>
          <span className={`${styles.dot} ${teamKey === 'blue' ? styles.dotBlue : styles.dotRed}`} />
          <div className={styles.teamInputWrap}>
            <input
              className={styles.teamInput}
              value={t.team_name}
              onClick={() => openTeamSearch(teamKey)}
              onChange={(e) => setTeamName(teamKey, e.target.value)}
              placeholder="Click to search team..."
              readOnly
            />
            {searchingTeam === teamKey && (
              <div className={styles.teamDropdown} ref={teamDropdownRef}
                onClick={(e) => e.stopPropagation()}>
                <input
                  ref={teamSearchInputRef}
                  className={styles.teamSearchInput}
                  placeholder="Search team..."
                  value={teamSearch}
                  onChange={(e) => setTeamSearch(e.target.value)}
                />
                <div className={styles.teamList}>
                  {filteredTeams.length === 0 && (
                    <div className={styles.teamEmpty}>No teams found</div>
                  )}
                  {filteredTeams.map((name) => (
                    <div key={name}
                      className={`${styles.teamItem} ${t.team_name === name ? styles.teamItemSelected : ''}`}
                      onClick={() => selectTeam(teamKey, name)}>
                      {name}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
          <span className={styles.sideLabel}>{t.side.toUpperCase()}</span>
        </div>

        {/* Slots */}
        {Array.from({ length: 5 }, (_, i) => renderSlot(teamKey, i))}

        {/* Probability */}
        <div className={styles.probArea}>
          <div className={styles.probLabel}>WIN PROBABILITY</div>
          <div className={styles.probVal} style={{ color: accent }}>
            {prob != null ? `${prob.toFixed(1)}%` : '—'}
          </div>
          {prob != null && (
            <div className={styles.probBar}>
              <div className={`${styles.probFill} pg-prob-fill`}
                data-w={`${prob}%`}
                style={{
                  width: 0,
                  background: teamKey === 'blue'
                    ? 'linear-gradient(90deg,var(--teal),rgba(10,200,185,.3))'
                    : 'linear-gradient(90deg,var(--red),rgba(200,48,32,.3))',
                }} />
            </div>
          )}
        </div>
      </div>
    )
  }

  return (
    <div className={styles.page}>
      <Topbar>
        <div className={styles.pickerTitle}>
          <div className={styles.pickerName}>PICK YOUR CHAMPION</div>
          <div className={styles.pickerSub}>Pre-Game Prediction · Random Forest · 1 credit</div>
        </div>
      </Topbar>

      <div className={styles.layout}>
        {renderPanel('blue')}

        {/* ── Center: Champion Grid ── */}
        <div className={styles.center}>
          {/* Role filters */}
          <div className={styles.filterRow}>
            {ROLES.map((r) => (
              <button key={r}
                className={`${styles.roleBtn} ${roleFilter === r ? styles.roleBtnActive : ''}`}
                onClick={() => setRoleFilter(r)}>
                {r === 'ALL' ? 'ALL' : r.toUpperCase()}
              </button>
            ))}
            <input className={styles.champSearchInput}
              placeholder="Search champion..."
              value={champSearch}
              onChange={(e) => setChampSearch(e.target.value)} />
          </div>

          {/* Status */}
          <div className={styles.statusBar}>
            <span className={styles.statusText}>
              {activeSlot
                ? `Click a champion for ${activeSlot.team === 'blue' ? 'Blue' : 'Red'} ${POSITIONS[activeSlot.index]}`
                : `${filteredChampions.length} champions · Click a slot to start`}
            </span>
            {credits != null && <span className={styles.creditBadge}>{credits} credits</span>}
          </div>

          {/* Grid */}
          <div className={styles.champGrid}>
            {filteredChampions.map((c) => (
              <div key={c.id}
                className={`${styles.champCell} pg-champ ${activeSlot ? styles.champCellReady : ''}`}
                onClick={() => selectChampion(c.id)}>
                <img src={getChampionIconUrl(c.id)} alt={c.id}
                  className={styles.champImg} loading="lazy"
                  onError={(e) => { e.currentTarget.style.display = 'none' }} />
                <div className={styles.champName}>{c.id}</div>
              </div>
            ))}
            {filteredChampions.length === 0 && (
              <div className={styles.champEmpty}>No champions match</div>
            )}
          </div>

          {/* Bottom: result + lock */}
          {result && (
            <div className={styles.resultBar} id="pg-result">
              <span className={styles.resultLabel}>PREDICTED WINNER</span>
              <span className={styles.resultWinner}>{result.predicted_winner}</span>
              <span className={styles.resultConf}>{result.confidence.toFixed(1)}% confidence</span>
            </div>
          )}

          <div className={styles.lockWrap}>
            <button
              className={`${styles.lockBtn} ${(!isComplete() || loading) ? styles.lockBtnOff : ''}`}
              onClick={runPrediction}
              disabled={!isComplete() || loading}>
              {loading ? 'Predicting...' : 'Lock In & Predict'}
            </button>
            {error && <div className={styles.errorText}>{error}</div>}
          </div>
        </div>

        {renderPanel('red')}
      </div>
    </div>
  )
}
