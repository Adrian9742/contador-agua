"use client"

import { useState, useEffect, useCallback, useRef } from "react"

const STORAGE_KEY = "agua_v1"

type DayEntry = { consumed: number; goal: number }
type DailyHistory = Record<string, DayEntry>

export type DayStatus = "done" | "today" | "failed"

export interface DayInfo {
  date: string
  label: string
  status: DayStatus
  percentage: number
}

interface State {
  goalMl: number
  intervalMin: number
  consumedMl: number
  lastDrinkTime: number
  dailyHistory: DailyHistory
  bestStreak: number
  lastDate: string
}

const WEEK_LABELS = ["Dom", "Seg", "Ter", "Qua", "Qui", "Sex", "Sáb"]

function todayISO(): string {
  return new Date().toISOString().slice(0, 10)
}

const DEFAULTS: State = {
  goalMl: 2000,
  intervalMin: 30,
  consumedMl: 0,
  lastDrinkTime: 0,
  dailyHistory: {},
  bestStreak: 0,
  lastDate: "",
}

function loadState(): State {
  if (typeof window === "undefined") return { ...DEFAULTS, lastDate: todayISO(), lastDrinkTime: Date.now() }
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    if (!raw) return { ...DEFAULTS, lastDate: todayISO(), lastDrinkTime: Date.now() }
    return { ...DEFAULTS, ...JSON.parse(raw) }
  } catch {
    return { ...DEFAULTS, lastDate: todayISO(), lastDrinkTime: Date.now() }
  }
}

function saveState(s: State) {
  if (typeof window === "undefined") return
  localStorage.setItem(STORAGE_KEY, JSON.stringify(s))
}

function trimHistory(history: DailyHistory): DailyHistory {
  const cutoff = new Date()
  cutoff.setDate(cutoff.getDate() - 30)
  const cutoffStr = cutoff.toISOString().slice(0, 10)
  const trimmed: DailyHistory = {}
  for (const k in history) {
    if (k >= cutoffStr) trimmed[k] = history[k]
  }
  return trimmed
}

function computeStreak(state: State): number {
  let count = 0
  const d = new Date()
  d.setDate(d.getDate() - 1)
  while (true) {
    const key = d.toISOString().slice(0, 10)
    const entry = state.dailyHistory[key]
    if (!entry || entry.consumed < entry.goal) break
    count++
    d.setDate(d.getDate() - 1)
  }
  if (state.consumedMl >= state.goalMl) count++
  return count
}

function computeLast7Days(state: State): DayInfo[] {
  const today = new Date()
  const result: DayInfo[] = []
  for (let i = 6; i >= 0; i--) {
    const d = new Date(today)
    d.setDate(d.getDate() - i)
    const key = d.toISOString().slice(0, 10)
    const label = WEEK_LABELS[d.getDay()]
    if (i === 0) {
      const pct = Math.min(100, Math.round((state.consumedMl / state.goalMl) * 100))
      result.push({ date: key, label, status: "today", percentage: pct })
    } else {
      const entry = state.dailyHistory[key]
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

export function useWaterState() {
  const [state, setStateRaw] = useState<State>(() => ({ ...DEFAULTS, lastDate: todayISO(), lastDrinkTime: Date.now() }))
  const [timeRemaining, setTimeRemaining] = useState(0)
  const [hydrated, setHydrated] = useState(false)

  // Refs for the timer so interval doesn't need to restart on state changes
  const lastDrinkRef = useRef(Date.now())
  const intervalMinRef = useRef(30)

  // Load from localStorage on mount + auto-reset if new day
  useEffect(() => {
    let s = loadState()
    const today = todayISO()

    if (s.lastDate !== today && s.lastDate !== "") {
      // New day: save yesterday to history
      const history = trimHistory({
        ...s.dailyHistory,
        [s.lastDate]: { consumed: s.consumedMl, goal: s.goalMl },
      })
      const streak = computeStreak({ ...s, dailyHistory: history })
      s = {
        ...s,
        consumedMl: 0,
        lastDrinkTime: Date.now(),
        dailyHistory: history,
        lastDate: today,
        bestStreak: Math.max(s.bestStreak, streak),
      }
      saveState(s)
    } else if (!s.lastDate) {
      s = { ...s, lastDate: today, lastDrinkTime: Date.now() }
      saveState(s)
    }

    lastDrinkRef.current = s.lastDrinkTime
    intervalMinRef.current = s.intervalMin
    setStateRaw(s)
    setHydrated(true)

    // Request notification permission silently
    if (typeof Notification !== "undefined" && Notification.permission === "default") {
      Notification.requestPermission()
    }
  }, [])

  // Countdown timer — ticks every second
  useEffect(() => {
    const tick = () => {
      const elapsed = (Date.now() - lastDrinkRef.current) / 1000
      const total = intervalMinRef.current * 60
      const rem = Math.max(0, total - elapsed)
      setTimeRemaining(Math.round(rem))
    }
    tick()
    const id = setInterval(tick, 1000)
    return () => clearInterval(id)
  }, [])

  const setState = useCallback((updater: (prev: State) => State) => {
    setStateRaw(prev => {
      const next = updater(prev)
      lastDrinkRef.current = next.lastDrinkTime
      intervalMinRef.current = next.intervalMin
      saveState(next)
      return next
    })
  }, [])

  const addWater = useCallback((ml: number) => {
    setState(prev => {
      if (prev.consumedMl >= prev.goalMl) return prev
      const consumed = Math.min(prev.goalMl, prev.consumedMl + Math.max(0, ml))
      const now = Date.now()
      // Notify when goal reached
      if (consumed >= prev.goalMl && typeof Notification !== "undefined" && Notification.permission === "granted") {
        new Notification("Meta diária atingida! 🎉", { body: `Você bebeu ${prev.goalMl} ml hoje!` })
      }
      return { ...prev, consumedMl: consumed, lastDrinkTime: now }
    })
  }, [setState])

  const resetDay = useCallback(() => {
    setState(prev => {
      const today = todayISO()
      const history = trimHistory({
        ...prev.dailyHistory,
        [today]: { consumed: prev.consumedMl, goal: prev.goalMl },
      })
      const next = { ...prev, consumedMl: 0, lastDrinkTime: Date.now(), dailyHistory: history, lastDate: today }
      const streak = computeStreak(next)
      return { ...next, bestStreak: Math.max(prev.bestStreak, streak) }
    })
  }, [setState])

  const setGoal = useCallback((ml: number) => {
    setState(prev => ({ ...prev, goalMl: Math.max(100, ml) }))
  }, [setState])

  const setIntervalMin = useCallback((min: number) => {
    setState(prev => ({ ...prev, intervalMin: Math.max(1, min), lastDrinkTime: Date.now() }))
  }, [setState])

  const percent = Math.min(100, Math.round((state.consumedMl / Math.max(1, state.goalMl)) * 100))
  const remaining = Math.max(0, state.goalMl - state.consumedMl)
  const streak = computeStreak(state)
  const last7Days = computeLast7Days(state)
  const goalReached = state.consumedMl >= state.goalMl

  // Format MM:SS
  const mins = Math.floor(timeRemaining / 60)
  const secs = timeRemaining % 60
  const countdownStr = `${String(mins).padStart(2, "0")}:${String(secs).padStart(2, "0")}`

  return {
    ...state,
    percent,
    remaining,
    streak,
    last7Days,
    goalReached,
    timeRemaining,
    countdownStr,
    hydrated,
    addWater,
    resetDay,
    setGoal,
    setIntervalMin,
  }
}
