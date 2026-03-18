import { useEffect, useRef, useState } from 'react'
import { DRAFT_BLUE, DRAFT_RED } from '../data/content'

const DDRAGON_VERSION = '15.5.1'

const CHAMPION_KEY_MAP = {
  "Kha'Zix": 'Khazix',
  "Kai'Sa": 'Kaisa',
  "Cho'Gath": 'Chogath',
  "Bel'Veth": 'Belveth',
  "Kog'Maw": 'KogMaw',
  "Rek'Sai": 'RekSai',
  "Vel'Koz": 'Velkoz',
  Wukong: 'MonkeyKing',
  'Nunu & Willump': 'Nunu',
  LeBlanc: 'Leblanc',
  'Lee Sin': 'LeeSin',
}

function getChampionIconUrl(championName) {
  const mapped = CHAMPION_KEY_MAP[championName]
  const normalized = (mapped || championName).replace(/[^a-zA-Z]/g, '')
  return `https://ddragon.leagueoflegends.com/cdn/${DDRAGON_VERSION}/img/champion/${normalized}.png`
}

function drawSlot(ctx, slot, x, y, sw, sh, side, alpha, champIcon) {
  ctx.globalAlpha = alpha

  const bgGrad = ctx.createLinearGradient(x, y, x, y + sh)
  bgGrad.addColorStop(0, 'rgba(13,26,46,0.92)')
  bgGrad.addColorStop(1, 'rgba(7,16,30,0.94)')
  ctx.fillStyle = bgGrad
  ctx.fillRect(x, y, sw, sh)

  ctx.fillStyle = side === 'blue' ? '#0AC8B9' : '#C83020'
  if (side === 'blue') ctx.fillRect(x, y, 2.5, sh)
  else ctx.fillRect(x + sw - 2.5, y, 2.5, sh)

  ctx.fillStyle = side === 'blue' ? 'rgba(10,200,185,0.12)' : 'rgba(200,48,32,0.12)'
  if (side === 'blue') ctx.fillRect(x + 3, y + 3, sw * 0.26, sh * 0.28)
  else ctx.fillRect(x + sw * 0.74, y + 3, sw * 0.22, sh * 0.28)

  ctx.font = `bold ${Math.round(sh * 0.13)}px Share Tech Mono, monospace`
  ctx.fillStyle = side === 'blue' ? '#0AC8B9' : '#C83020'
  ctx.textAlign = 'center'
  ctx.fillText(slot.pos, side === 'blue' ? x + sw * 0.15 : x + sw * 0.85, y + sh * 0.2)

  const playerTextSize = Math.round(sh * 0.2)
  ctx.font = `bold ${playerTextSize}px Cinzel, serif`
  ctx.fillStyle = '#C8A96E'
  const iconSize = sh * 0.72
  const iconY = y + sh * 0.5 - iconSize / 2
  if (side === 'blue') {
    const iconX = x - iconSize - 7
    if (champIcon) {
      ctx.fillStyle = '#C8A96E'
      ctx.fillRect(iconX - 1, iconY - 1, iconSize + 2, iconSize + 2)
      ctx.strokeStyle = 'rgba(10,200,185,0.44)'
      ctx.lineWidth = 1
      ctx.strokeRect(iconX - 1, iconY - 1, iconSize + 2, iconSize + 2)
      ctx.drawImage(champIcon, iconX, iconY, iconSize, iconSize)
    }
    ctx.textAlign = 'left'
    ctx.fillText(slot.player, x + 5, y + sh * 0.56)
  } else {
    const iconX = x + sw + 7
    if (champIcon) {
      ctx.fillStyle = '#C8A96E'
      ctx.fillRect(iconX - 1, iconY - 1, iconSize + 2, iconSize + 2)
      ctx.strokeStyle = 'rgba(200,48,32,0.42)'
      ctx.lineWidth = 1
      ctx.strokeRect(iconX - 1, iconY - 1, iconSize + 2, iconSize + 2)
      ctx.drawImage(champIcon, iconX, iconY, iconSize, iconSize)
    }
    ctx.textAlign = 'right'
    ctx.fillText(slot.player, x + sw - 5, y + sh * 0.56)
  }
  ctx.shadowBlur = 0

  ctx.font = `${Math.round(sh * 0.12)}px Rajdhani, sans-serif`
  ctx.fillStyle = 'rgba(200,169,110,0.7)'
  if (side === 'blue') {
    ctx.textAlign = 'left'
    ctx.fillText(slot.champ, x + 5, y + sh * 0.76)
  } else {
    ctx.textAlign = 'right'
    ctx.fillText(slot.champ, x + sw - 5, y + sh * 0.76)
  }

  ctx.strokeStyle = 'rgba(200,169,110,0.17)'
  ctx.lineWidth = 0.8
  ctx.strokeRect(x, y, sw, sh)

  const sheen = ctx.createLinearGradient(x, y, x + sw, y)
  sheen.addColorStop(0, 'rgba(255,255,255,0.05)')
  sheen.addColorStop(1, 'rgba(255,255,255,0)')
  ctx.fillStyle = sheen
  ctx.fillRect(x, y, sw, sh * 0.22)
  ctx.globalAlpha = 1
}

export default function DraftCanvas({ progress }) {
  const canvasRef = useRef(null)
  const championIconCacheRef = useRef({})
  const [iconsReady, setIconsReady] = useState(0)

  useEffect(() => {
    const champions = [...new Set([...DRAFT_BLUE, ...DRAFT_RED].map(slot => slot.champ))]
    const missing = champions.filter(champion => !championIconCacheRef.current[champion])
    if (missing.length === 0) return

    Promise.all(
      missing.map((champion) => new Promise((resolve) => {
        const img = new Image()
        img.crossOrigin = 'anonymous'
        img.onload = () => {
          championIconCacheRef.current[champion] = img
          resolve()
        }
        img.onerror = () => resolve()
        img.src = getChampionIconUrl(champion)
      })),
    ).then(() => setIconsReady((v) => v + 1))
  }, [])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    const W = window.innerWidth
    const H = window.innerHeight
    const p = progress

    ctx.clearRect(0, 0, W, H)
    if (p <= 0) return

    const cx = W / 2
    const cy = H / 2
    const sw = Math.min(W * 0.102, 102)
    const sh = sw * 0.84
    const gap = sh * 0.1
    const totalH = 5 * sh + 4 * gap
    const startY = cy - totalH / 2 - H * 0.035

    DRAFT_BLUE.forEach((slot, i) => {
      const threshold = i / 5.5
      const slotP = Math.max(0, Math.min(1, (p - threshold) / 0.15))
      if (slotP <= 0) return
      const x = cx - sw * 2.45 - (1 - slotP) * 36
      const y = startY + i * (sh + gap)
      drawSlot(ctx, slot, x, y, sw, sh, 'blue', slotP, championIconCacheRef.current[slot.champ])
    })

    DRAFT_RED.forEach((slot, i) => {
      const threshold = 0.07 + i / 5.5
      const slotP = Math.max(0, Math.min(1, (p - threshold) / 0.15))
      if (slotP <= 0) return
      const x = cx + sw * 1.45 + (1 - slotP) * 36
      const y = startY + i * (sh + gap)
      drawSlot(ctx, slot, x, y, sw, sh, 'red', slotP, championIconCacheRef.current[slot.champ])
    })

    const centerP = Math.max(0, Math.min(1, (p - 0.7) / 0.17))
    if (centerP > 0) {
      ctx.globalAlpha = centerP
      ctx.strokeStyle = `rgba(200,169,110,${0.1 * centerP})`
      ctx.lineWidth = 1
      ctx.beginPath()
      ctx.moveTo(cx, startY)
      ctx.lineTo(cx, startY + totalH)
      ctx.stroke()

      ctx.font = `bold ${Math.round(H * 0.028)}px Cinzel, serif`
      ctx.fillStyle = `rgba(200,169,110,${0.17 * centerP})`
      ctx.textAlign = 'center'
      ctx.fillText('VS', cx, cy + Math.round(H * 0.014))

      const predP = Math.max(0, Math.min(1, (p - 0.86) / 0.14))
      if (predP > 0) {
        const bw = sw * 1.74
        const bh = sh * 1.14
        const bx = cx - bw / 2
        const by = cy - bh / 2 + sh * 0.04

        ctx.globalAlpha = predP
        const predGrad = ctx.createLinearGradient(bx, by, bx, by + bh)
        predGrad.addColorStop(0, 'rgba(10,20,38,0.95)')
        predGrad.addColorStop(1, 'rgba(6,15,30,0.92)')
        ctx.fillStyle = predGrad
        ctx.fillRect(bx, by, bw, bh)
        ctx.strokeStyle = `rgba(10,200,185,${0.28 * predP})`
        ctx.lineWidth = 1
        ctx.strokeRect(bx, by, bw, bh)
        ctx.fillStyle = `rgba(10,200,185,${0.55 * predP})`
        ctx.fillRect(bx, by, bw, 2)
        ctx.fillStyle = `rgba(200,169,110,${0.35 * predP})`
        ctx.fillRect(bx, by + bh - 2, bw, 2)

        ctx.font = `bold ${Math.round(bh * 0.16)}px Share Tech Mono, monospace`
        ctx.fillStyle = `rgba(10,200,185,${predP})`
        ctx.textAlign = 'center'
        ctx.fillText('AI PREDICTION', cx, by + bh * 0.26)

        ctx.font = `bold ${Math.round(bh * 0.34)}px Cinzel, serif`
        ctx.fillStyle = `rgba(200,169,110,${predP})`
        ctx.fillText('82.4%', cx, by + bh * 0.64)

        ctx.font = `${Math.round(bh * 0.12)}px Share Tech Mono, monospace`
        ctx.fillStyle = `rgba(200,169,110,${0.5 * predP})`
        ctx.fillText('T1 WIN PROBABILITY', cx, by + bh * 0.85)
      }
      ctx.globalAlpha = 1
    }
  }, [progress, iconsReady])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const resize = () => {
      const dpr = window.devicePixelRatio || 1
      const width = window.innerWidth
      const height = window.innerHeight

      canvas.width = Math.floor(width * dpr)
      canvas.height = Math.floor(height * dpr)
      canvas.style.width = `${width}px`
      canvas.style.height = `${height}px`

      const ctx = canvas.getContext('2d')
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0)
    }
    resize()
    window.addEventListener('resize', resize)
    return () => window.removeEventListener('resize', resize)
  }, [])

  return (
    <canvas
      ref={canvasRef}
      className="absolute inset-0 z-[3] pointer-events-none"
    />
  )
}