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
