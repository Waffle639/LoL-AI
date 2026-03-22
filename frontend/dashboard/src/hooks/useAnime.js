import { useEffect, useRef } from 'react'
import anime from 'animejs'

// ─────────────────────────────────────────────────────────────────
// useAnime
// Runs an anime.js animation when the component mounts.
// Automatically cleans up (pauses) on unmount.
//
// Usage:
//   const ref = useAnime({
//     targets: '.scard',
//     opacity: [0, 1],
//     translateY: [20, 0],
//     delay: anime.stagger(80),
//     duration: 460,
//     easing: 'easeOutBack',
//   })
// ─────────────────────────────────────────────────────────────────

export function useAnime(config, deps = []) {
  const animRef = useRef(null)

  useEffect(() => {
    // Small timeout so the DOM has rendered
    const timer = setTimeout(() => {
      animRef.current = anime({ ...config })
    }, 16)

    return () => {
      clearTimeout(timer)
      animRef.current?.pause()
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)

  return animRef
}

// ─────────────────────────────────────────────────────────────────
// useAnimeTimeline
// For multi-step animations. Returns a function to build the timeline.
// ─────────────────────────────────────────────────────────────────

export function useAnimeTimeline(buildFn, deps = []) {
  useEffect(() => {
    const timer = setTimeout(() => {
      const tl = anime.timeline({ easing: 'easeOutExpo' })
      buildFn(tl, anime)
    }, 16)

    return () => clearTimeout(timer)
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, deps)
}

// Re-export anime for convenience
export { anime }
