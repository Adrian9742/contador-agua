import { STORAGE_KEY, DEFAULT_GOAL_ML, DEFAULT_INTERVAL_MIN } from "./constants"
import type { AppState } from "./types"
import { todayISO } from "./dates"

const DEFAULTS: AppState = {
  goalMl: DEFAULT_GOAL_ML,
  intervalMin: DEFAULT_INTERVAL_MIN,
  consumedMl: 0,
  lastDrinkTime: 0,
  dailyHistory: {},
  bestStreak: 0,
  lastDate: "",
}

function freshState(): AppState {
  return { ...DEFAULTS, lastDate: todayISO(), lastDrinkTime: Date.now() }
}

export { DEFAULTS }

export async function loadState(): Promise<AppState> {
  if (typeof window !== "undefined" && window.electronAPI) {
    const data = await window.electronAPI.loadState()
    return data ? { ...DEFAULTS, ...data } : freshState()
  }
  if (typeof window === "undefined") return freshState()
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? { ...DEFAULTS, ...JSON.parse(raw) } : freshState()
  } catch {
    return freshState()
  }
}

export function saveState(s: AppState): void {
  if (typeof window !== "undefined" && window.electronAPI) {
    window.electronAPI.saveState(s)
    return
  }
  if (typeof window === "undefined") return
  localStorage.setItem(STORAGE_KEY, JSON.stringify(s))
}
