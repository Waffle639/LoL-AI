import { useEffect } from 'react'
import { useApp } from '@/context/AppContext'
import anime from 'animejs'

// ─────────────────────────────────────────────────────────────────
// useSidebar
// Handles sidebar collapse animation + state
// ─────────────────────────────────────────────────────────────────

export function useSidebar() {
  const { sidebarOpen, setSidebarOpen } = useApp()

  const toggle = () => {
    const sidebars = document.querySelectorAll('.sidebar')
    const next = !sidebarOpen

    sidebars.forEach(sb => {
      sb.classList.toggle('col', !next)
      anime({
        targets: sb,
        width: next
          ? [parseInt(getComputedStyle(document.documentElement).getPropertyValue('--sb-w-c')), 220]
          : [220, parseInt(getComputedStyle(document.documentElement).getPropertyValue('--sb-w-c'))],
        duration: 300,
        easing: 'cubicBezier(.4,0,.2,1)',
      })
    })

    setSidebarOpen(next)
  }

  return { sidebarOpen, toggle }
}
