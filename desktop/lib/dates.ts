import { HISTORY_DAYS } from "./constants"
import type { AppState, DailyHistory } from "./types"

export function todayISO(): string {
  return new Date().toISOString().slice(0, 10)
}

export function trimHistory(history: DailyHistory): DailyHistory {
  const cutoff = new Date()
  cutoff.setDate(cutoff.getDate() - HISTORY_DAYS)
  const cutoffStr = cutoff.toISOString().slice(0, 10)
  const trimmed: DailyHistory = {}
  for (const k in history) {
    if (k >= cutoffStr) trimmed[k] = history[k]
  }
  return trimmed
}

export function applyDayRollover(s: AppState, today: string): AppState {
  if (!s.lastDate || s.lastDate === today) return s

  const history = trimHistory({
    ...s.dailyHistory,
    [s.lastDate]: { consumed: s.consumedMl, goal: s.goalMl },
  })

  // Preenche dias perdidos (PC desligado) com zero
  const start = new Date(s.lastDate)
  start.setDate(start.getDate() + 1)
  const end = new Date(today)
  while (start < end) {
    const key = start.toISOString().slice(0, 10)
    if (!history[key]) history[key] = { consumed: 0, goal: s.goalMl }
    start.setDate(start.getDate() + 1)
  }

  return { ...s, consumedMl: 0, lastDrinkTime: Date.now(), dailyHistory: history, lastDate: today }
}
