import { useEffect, useRef } from 'react'
import { DRAFT_BLUE, DRAFT_RED } from '../data/content'

function drawSlot(ctx, slot, x, y, sw, sh, side, alpha) {
  ctx.globalAlpha = alpha

  ctx.fillStyle = '#0a1525'
  ctx.fillRect(x, y, sw, sh)

  ctx.fillStyle = side === 'blue' ? '#0AC8B9' : '#C83020'
  if (side === 'blue') ctx.fillRect(x, y, 2, sh)
  else ctx.fillRect(x + sw - 2, y, 2, sh)

  ctx.fillStyle = side === 'blue' ? 'rgba(10,200,185,0.08)' : 'rgba(200,48,32,0.08)'
  if (side === 'blue') ctx.fillRect(x + 3, y + 3, sw * 0.26, sh * 0.28)
  else ctx.fillRect(x + sw * 0.74, y + 3, sw * 0.22, sh * 0.28)

  ctx.font = `bold ${Math.round(sh * 0.13)}px Share Tech Mono, monospace`
  ctx.fillStyle = side === 'blue' ? '#0AC8B9' : '#C83020'
  ctx.textAlign = 'center'
  ctx.fillText(slot.pos, side === 'blue' ? x + sw * 0.15 : x + sw * 0.85, y + sh * 0.2)

  ctx.font = `bold ${Math.round(sh * 0.16)}px Cinzel, serif`
  ctx.fillStyle = '#C8A96E'
  if (side === 'blue') {
    ctx.textAlign = 'left'
    ctx.fillText(slot.player, x + 5, y + sh * 0.54)
  } else {
    ctx.textAlign = 'right'
    ctx.fillText(slot.player, x + sw - 5, y + sh * 0.54)
  }

  ctx.font = `${Math.round(sh * 0.12)}px Rajdhani, sans-serif`
  ctx.fillStyle = 'rgba(200,169,110,0.44)'
  if (side === 'blue') {
    ctx.textAlign = 'left'
    ctx.fillText(slot.champ, x + 5, y + sh * 0.76)
  } else {
    ctx.textAlign = 'right'
    ctx.fillText(slot.champ, x + sw - 5, y + sh * 0.76)
  }

  ctx.strokeStyle = 'rgba(200,169,110,0.1)'
  ctx.lineWidth = 0.5
  ctx.strokeRect(x, y, sw, sh)
  ctx.globalAlpha = 1
}

export default function DraftCanvas({ progress }) {
  const canvasRef = useRef(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    const W = canvas.width
    const H = canvas.height
    const p = progress

    ctx.clearRect(0, 0, W, H)
    if (p <= 0) return

    const cx = W / 2
    const cy = H / 2
    const sw = Math.min(W * 0.115, 112)
    const sh = sw * 0.84
    const gap = sh * 0.1
    const totalH = 5 * sh + 4 * gap
    const startY = cy - totalH / 2

    DRAFT_BLUE.forEach((slot, i) => {
      const threshold = i / 5.5
      const slotP = Math.max(0, Math.min(1, (p - threshold) / 0.15))
      if (slotP <= 0) return
      const x = cx - sw * 2.05 - (1 - slotP) * 34
      const y = startY + i * (sh + gap)
      drawSlot(ctx, slot, x, y, sw, sh, 'blue', slotP)
    })

    DRAFT_RED.forEach((slot, i) => {
      const threshold = 0.07 + i / 5.5
      const slotP = Math.max(0, Math.min(1, (p - threshold) / 0.15))
      if (slotP <= 0) return
      const x = cx + sw * 1.05 + (1 - slotP) * 34
      const y = startY + i * (sh + gap)
      drawSlot(ctx, slot, x, y, sw, sh, 'red', slotP)
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
        const bw = sw * 0.98
        const bh = sh * 0.8
        const bx = cx - bw / 2
        const by = startY + totalH + gap * 1.5

        ctx.globalAlpha = predP
        ctx.fillStyle = '#060f1e'
        ctx.fillRect(bx, by, bw, bh)
        ctx.strokeStyle = `rgba(10,200,185,${0.28 * predP})`
        ctx.lineWidth = 1
        ctx.strokeRect(bx, by, bw, bh)
        ctx.fillStyle = `rgba(10,200,185,${0.55 * predP})`
        ctx.fillRect(bx, by, bw, 2)

        ctx.font = `bold ${Math.round(bh * 0.16)}px Share Tech Mono, monospace`
        ctx.fillStyle = `rgba(10,200,185,${predP})`
        ctx.textAlign = 'center'
        ctx.fillText('AI PREDICTION', cx, by + bh * 0.26)

        ctx.font = `bold ${Math.round(bh * 0.34)}px Cinzel, serif`
        ctx.fillStyle = `rgba(200,169,110,${predP})`
        ctx.fillText('82.4%', cx, by + bh * 0.64)

        ctx.font = `${Math.round(bh * 0.12)}px Share Tech Mono, monospace`
        ctx.fillStyle = 'rgba(200,169,110,0.35)'
        ctx.fillText('T1 WIN PROBABILITY', cx, by + bh * 0.85)
      }
      ctx.globalAlpha = 1
    }
  }, [progress])

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const resize = () => {
      canvas.width  = window.innerWidth
      canvas.height = window.innerHeight
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