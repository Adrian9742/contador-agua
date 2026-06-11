export type DayEntry = { consumed: number; goal: number }
export type DailyHistory = Record<string, DayEntry>
export type DayStatus = "done" | "today" | "failed"

export interface DayInfo {
  date: string
  label: string
  status: DayStatus
  percentage: number
}

export interface AppState {
  goalMl: number
  intervalMin: number
  consumedMl: number
  lastDrinkTime: number
  dailyHistory: DailyHistory
  bestStreak: number
  lastDate: string
}

export interface ElectronAPI {
  platform: string
  loadState:       ()              => Promise<AppState | null>
  saveState:       (data: AppState) => Promise<void>
  notifyGoal:      ()              => Promise<void>
  onReminder:      (cb: () => void) => void
  onMidnightReset: (cb: () => void) => void
}

declare global {
  interface Window {
    electronAPI?: ElectronAPI
  }
}
