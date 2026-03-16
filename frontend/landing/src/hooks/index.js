import { useEffect, useRef, useState, useCallback } from 'react'

export function useCursor() {
  useEffect(() => {
    const hex = document.getElementById('cursor-hex')
    const dot = document.getElementById('cursor-dot')
    if (!hex || !dot) return

    let mx = 0, my = 0, tx = 0, ty = 0
    let raf

    const onMove = (e) => {
      mx = e.clientX; my = e.clientY
      hex.style.left = mx + 'px'
      hex.style.top  = my + 'px'
    }

    const loop = () => {
      tx += (mx - tx) * 0.12
      ty += (my - ty) * 0.12
      dot.style.left = tx + 'px'
      dot.style.top  = ty + 'px'
      raf = requestAnimationFrame(loop)
    }

    const onEnter = () => hex.classList.add('hovered')
    const onLeave = () => hex.classList.remove('hovered')

    document.addEventListener('mousemove', onMove)
    document.querySelectorAll('a, button, [data-cursor-hover]')
      .forEach(el => {
        el.addEventListener('mouseenter', onEnter)
        el.addEventListener('mouseleave', onLeave)
      })

    raf = requestAnimationFrame(loop)
    return () => {
      document.removeEventListener('mousemove', onMove)
      cancelAnimationFrame(raf)
    }
  }, [])
}

export function useScrollReveal(threshold = 0.1) {
  const ref = useRef(null)
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const el = ref.current
    if (!el) return
    const obs = new IntersectionObserver(
      ([entry]) => { if (entry.isIntersecting) { setVisible(true); obs.unobserve(el) } },
      { threshold }
    )
    obs.observe(el)
    return () => obs.disconnect()
  }, [threshold])

  return { ref, visible }
}

export function useCountUp(target, decimals = 0, duration = 1700) {
  const [value, setValue] = useState(0)
  const triggered = useRef(false)

  const start = useCallback(() => {
    if (triggered.current) return
    triggered.current = true

    const startTime = performance.now()
    const tick = (now) => {
      const elapsed = now - startTime
      const progress = Math.min(elapsed / duration, 1)
      const eased = progress === 1 ? 1 : 1 - Math.pow(2, -10 * progress)
      setValue(parseFloat((target * eased).toFixed(decimals)))
      if (progress < 1) requestAnimationFrame(tick)
    }
    requestAnimationFrame(tick)
  }, [target, decimals, duration])

  return { value, start }
}

export function useHeroScroll(wrapperRef) {
  const [progress, setProgress] = useState(0)

  useEffect(() => {
    const onScroll = () => {
      const el = wrapperRef.current
      if (!el) return
      const top     = -el.getBoundingClientRect().top
      const total   = el.offsetHeight - window.innerHeight
      const p       = Math.max(0, Math.min(1, top / total))
      setProgress(p)
    }

    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [wrapperRef])

  return progress
}

export function useNavScroll(threshold = 60) {
  const [scrolled, setScrolled] = useState(false)

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > threshold)
    window.addEventListener('scroll', onScroll, { passive: true })
    return () => window.removeEventListener('scroll', onScroll)
  }, [threshold])

  return scrolled
}