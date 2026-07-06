"use client"

import { useState, useEffect, useCallback, useRef } from "react"
import { DEFAULTS, loadState, saveState } from "@/lib/storage"
import { todayISO, applyDayRollover, trimHistory } from "@/lib/dates"
import { computeStreak, computeLast7Days } from "@/lib/stats"
import type { AppState } from "@/lib/types"

// Re-exporta tipos usados pelos componentes
export type { DailyHistory, DayInfo, DayStatus } from "@/lib/types"

export function useWaterState() {
  const [state, setStateRaw] = useState<AppState>(() => ({
    ...DEFAULTS,
    lastDate: todayISO(),
    lastDrinkTime: Date.now(),
  }))
  const [timeRemaining, setTimeRemaining] = useState(0)
  const [hydrated, setHydrated] = useState(false)

  const lastDrinkRef   = useRef(Date.now())
  const intervalMinRef = useRef(30)

  // ── Carga inicial ───────────────────────────────────────
  useEffect(() => {
    loadState().then((s) => {
      const today = todayISO()
      const rolled = applyDayRollover(s, today)
      const next = rolled.lastDate
        ? rolled
        : { ...rolled, lastDate: today, lastDrinkTime: Date.now() }
      const streak = computeStreak(next)
      const final = { ...next, bestStreak: Math.max(next.bestStreak, streak) }
      // Só salva se algo mudou (rollover ou streak)
      if (final.lastDate !== s.lastDate || final.consumedMl !== s.consumedMl || final.bestStreak !== s.bestStreak) {
        saveState(final)
      }
      lastDrinkRef.current   = final.lastDrinkTime
      intervalMinRef.current = final.intervalMin
      setStateRaw(final)
      setHydrated(true)

      // Pede permissão pra notificação (browser)
      if (
        typeof window !== "undefined" &&
        typeof Notification !== "undefined" &&
        Notification.permission === "default"
      ) {
        Notification.requestPermission()
      }
    })
  }, [])

  // ── Polling: lembrete + reset meia-noite (web) ────────
  useEffect(() => {
    let lastDate = todayISO()
    let lastNotified = 0
    let notificationIndex = 0
    const reminderMessages = [
      { title: "Hora de beber água! 💧", body: "Seu corpo agradece. Vai um copo agora?" },
      { title: "💧 Hidratação chegando!", body: "Já passou um tempinho sem beber água. Bora?" },
      { title: "🔥 Streak em risco!", body: "Não deixe o hábito morrer. Beba água agora!" },
      { title: "⏰ Toque pra hidratar", body: "Seu cérebro funciona melhor hidratado. Beba!" },
      { title: "🌊 Hora do copo d'água!", body: "Pare o que está fazendo e beba um gole." },
    ]

    const interval = setInterval(() => {
      const now = Date.now()
      const elapsed = (now - lastDrinkRef.current) / 1000

      // Verifica lembrete
      if (elapsed >= intervalMinRef.current * 60) {
        if (now - lastNotified > 30_000) { // evita spam
          if (typeof Notification !== "undefined" && Notification.permission === "granted") {
            const msg = reminderMessages[notificationIndex % reminderMessages.length]
            notificationIndex++
            new Notification(msg.title, { body: msg.body })
          }
          lastNotified = now
        }
      }

      // Verifica meia-noite (reset automático)
      const today = todayISO()
      if (today !== lastDate) {
        lastDate = today
        setStateRaw((prev) => {
          const next = applyDayRollover(prev, today)
          saveState(next)
          return next
        })
      }

      // Atualiza countdown (redundante com o 1s, só por segurança)
    }, 10_000)

    return () => clearInterval(interval)
  }, [])

  // ── Countdown visível (a cada 1s) ──────────────────────
  useEffect(() => {
    const tick = () => {
      const elapsed = (Date.now() - lastDrinkRef.current) / 1000
      setTimeRemaining(Math.round(Math.max(0, intervalMinRef.current * 60 - elapsed)))
    }
    tick()
    const id = setInterval(tick, 1000)
    return () => clearInterval(id)
  }, [])

  // ── Mutações ────────────────────────────────────────────
  const setState = useCallback((updater: (prev: AppState) => AppState) => {
    setStateRaw((prev) => {
      const next = updater(prev)
      lastDrinkRef.current   = next.lastDrinkTime
      intervalMinRef.current = next.intervalMin
      saveState(next)
      return next
    })
  }, [])

  const addWater = useCallback((ml: number) => {
    setState((prev) => {
      if (prev.consumedMl >= prev.goalMl) return prev
      const consumed = Math.min(prev.goalMl, prev.consumedMl + Math.max(0, ml))
      const goalJustReached = consumed >= prev.goalMl && prev.consumedMl < prev.goalMl
      if (goalJustReached) {
        if (typeof Notification !== "undefined" && Notification.permission === "granted") {
          new Notification("Meta diária atingida! 🎉", {
            body: `Você bebeu ${prev.goalMl} ml hoje!`,
          })
        }
      }
      return { ...prev, consumedMl: consumed, lastDrinkTime: Date.now() }
    })
  }, [setState])

  const resetDay = useCallback(() => {
    setState((prev) => {
      const today = todayISO()
      const history = trimHistory({ ...prev.dailyHistory, [today]: { consumed: prev.consumedMl, goal: prev.goalMl } })
      const next = { ...prev, consumedMl: 0, lastDrinkTime: Date.now(), dailyHistory: history, lastDate: today }
      return { ...next, bestStreak: Math.max(prev.bestStreak, computeStreak(next)) }
    })
  }, [setState])

  const setGoal        = useCallback((ml: number)  => setState((p) => ({ ...p, goalMl: Math.max(100, ml) })), [setState])
  const setIntervalMin = useCallback((min: number) => setState((p) => ({ ...p, intervalMin: Math.max(1, min), lastDrinkTime: Date.now() })), [setState])

  // ── Valores derivados ───────────────────────────────────
  const percent     = Math.min(100, Math.round((state.consumedMl / Math.max(1, state.goalMl)) * 100))
  const remaining   = Math.max(0, state.goalMl - state.consumedMl)
  const streak      = computeStreak(state)
  const last7Days   = computeLast7Days(state)
  const goalReached = state.consumedMl >= state.goalMl
  const mins        = Math.floor(timeRemaining / 60)
  const secs        = timeRemaining % 60
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
