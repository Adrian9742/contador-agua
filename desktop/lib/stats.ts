import { WEEK_LABELS } from "./constants"
import type { AppState, DayInfo } from "./types"

export function computeStreak(s: AppState): number {
  let count = 0
  const d = new Date()
  d.setDate(d.getDate() - 1)
  while (true) {
    const key = d.toISOString().slice(0, 10)
    const entry = s.dailyHistory[key]
    if (!entry || entry.consumed < entry.goal) break
    count++
    d.setDate(d.getDate() - 1)
  }
  if (s.consumedMl >= s.goalMl) count++
  return count
}

export function computeLast7Days(s: AppState): DayInfo[] {
  const today = new Date()
  const result: DayInfo[] = []
  for (let i = 6; i >= 0; i--) {
    const d = new Date(today)
    d.setDate(d.getDate() - i)
    const key = d.toISOString().slice(0, 10)
    const label = WEEK_LABELS[d.getDay()]
    if (i === 0) {
      const pct = Math.min(100, Math.round((s.consumedMl / s.goalMl) * 100))
      result.push({ date: key, label, status: "today", percentage: pct })
    } else {
      const entry = s.dailyHistory[key]
      if (entry && entry.consumed >= entry.goal) {
        result.push({ date: key, label, status: "done", percentage: 100 })
      } else {
        const pct = entry ? Math.min(100, Math.round((entry.consumed / entry.goal) * 100)) : 0
        result.push({ date: key, label, status: "failed", percentage: pct })
      }
    }
  }
  return result
}
