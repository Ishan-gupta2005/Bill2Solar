import { useEffect, useRef, useState } from 'react'

/** Animates from 0 to `target` with an ease-out curve. Re-runs when target changes. */
export function useCountUp(target: number, durationMs = 1400, delayMs = 0): number {
  const [value, setValue] = useState(0)
  const raf = useRef<number | null>(null)
  useEffect(() => {
    let start: number | null = null
    const from = 0
    const to = Number.isFinite(target) ? target : 0
    const tick = (t: number) => {
      if (start === null) start = t
      const p = Math.min(1, (t - start) / durationMs)
      const eased = 1 - Math.pow(1 - p, 3)
      setValue(from + (to - from) * eased)
      if (p < 1) raf.current = requestAnimationFrame(tick)
    }
    const timer = window.setTimeout(() => {
      raf.current = requestAnimationFrame(tick)
    }, delayMs)
    return () => {
      window.clearTimeout(timer)
      if (raf.current) cancelAnimationFrame(raf.current)
    }
  }, [target, durationMs, delayMs])
  return value
}

export const inr = (n: number, digits = 0) =>
  '₹' + Math.round(n).toLocaleString('en-IN', { maximumFractionDigits: digits })

export const num = (n: number, digits = 0) =>
  n.toLocaleString('en-IN', { maximumFractionDigits: digits, minimumFractionDigits: digits })
