"use client"

import { useState } from "react"
import {
  Droplet,
  Droplets,
  GlassWater,
  Coffee,
  Milk,
  Moon,
  Sun,
  Settings,
  Bell,
  RefreshCw,
  Plus,
  X,
  Target,
  Clock,
  Trophy,
  BarChart2,
} from "lucide-react"
import { Button } from "@/components/ui/button"
import { WaterBottle } from "@/components/water-bottle"
import { StreakCard } from "@/components/streak-card"
import { HistoryModal } from "@/components/history-modal"
import { useWaterState } from "@/hooks/useWaterState"

const quickAdds = [
  { label: "Copo", amount: 200, icon: GlassWater },
  { label: "Gole", amount: 250, icon: Droplet },
  { label: "Dose", amount: 500, icon: Coffee },
  { label: "Garrafa", amount: 750, icon: Milk },
]

export function WaterTracker() {
  const {
    consumedMl,
    goalMl,
    intervalMin,
    percent,
    remaining,
    streak,
    last7Days,
    dailyHistory,
    goalReached,
    countdownStr,
    bestStreak,
    hydrated,
    addWater,
    resetDay,
    setGoal,
    setIntervalMin,
  } = useWaterState()

  const [dark, setDark] = useState(true)
  const [manual, setManual] = useState("")
  const [showSettings, setShowSettings] = useState(false)
  const [showHistory, setShowHistory] = useState(false)
  const [goalInput, setGoalInput] = useState("")
  const [intervalInput, setIntervalInput] = useState("")

  const addManual = () => {
    const value = Number.parseInt(manual, 10)
    if (!Number.isNaN(value) && value > 0) {
      addWater(value)
      setManual("")
    }
  }

  const openSettings = () => {
    setGoalInput(String(goalMl))
    setIntervalInput(String(intervalMin))
    setShowSettings(true)
  }

  const saveSettings = () => {
    const g = Number.parseInt(goalInput, 10)
    const i = Number.parseInt(intervalInput, 10)
    if (!Number.isNaN(g) && g >= 100) setGoal(g)
    if (!Number.isNaN(i) && i >= 1) setIntervalMin(i)
    setShowSettings(false)
  }

  if (!hydrated) {
    return (
      <div className={dark ? "dark" : ""}>
        <div className="mx-auto flex min-h-screen w-full max-w-[440px] items-center justify-center bg-background">
          <Droplets className="h-8 w-8 animate-pulse text-primary" />
        </div>
      </div>
    )
  }

  return (
    <div className={dark ? "dark" : ""}>
      <div className="mx-auto min-h-screen w-full max-w-[440px] bg-background text-foreground">

        {/* History Modal */}
        {showHistory && (
          <HistoryModal
            dailyHistory={dailyHistory ?? {}}
            goalMl={goalMl}
            consumedMl={consumedMl}
            streak={streak}
            bestStreak={bestStreak}
            onClose={() => setShowHistory(false)}
          />
        )}

        {/* Settings Modal */}
        {showSettings && (
          <div
            className="fixed inset-0 z-50 flex items-end justify-center bg-black/60 backdrop-blur-sm sm:items-center"
            onClick={() => setShowSettings(false)}
          >
            <div
              className="w-full max-w-[440px] rounded-t-3xl border border-border bg-card p-6 shadow-2xl sm:rounded-3xl"
              onClick={(e) => e.stopPropagation()}
            >
              <div className="mb-5 flex items-center justify-between">
                <h2 className="text-base font-semibold">Configurações</h2>
                <button
                  onClick={() => setShowSettings(false)}
                  className="flex h-8 w-8 items-center justify-center rounded-full border border-border text-muted-foreground hover:bg-secondary"
                >
                  <X className="h-4 w-4" />
                </button>
              </div>

              <div className="flex flex-col gap-4">
                <label className="flex flex-col gap-1.5">
                  <span className="flex items-center gap-1.5 text-sm font-medium">
                    <Target className="h-4 w-4 text-primary" />
                    Meta diária (ml)
                  </span>
                  <div className="relative">
                    <input
                      value={goalInput}
                      onChange={(e) => setGoalInput(e.target.value.replace(/[^0-9]/g, ""))}
                      inputMode="numeric"
                      className="h-11 w-full rounded-xl border border-border bg-background pl-4 pr-10 text-sm outline-none transition-colors focus:border-primary"
                    />
                    <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">ml</span>
                  </div>
                </label>

                <label className="flex flex-col gap-1.5">
                  <span className="flex items-center gap-1.5 text-sm font-medium">
                    <Clock className="h-4 w-4 text-primary" />
                    Lembrete a cada (minutos)
                  </span>
                  <div className="relative">
                    <input
                      value={intervalInput}
                      onChange={(e) => setIntervalInput(e.target.value.replace(/[^0-9]/g, ""))}
                      inputMode="numeric"
                      className="h-11 w-full rounded-xl border border-border bg-background pl-4 pr-10 text-sm outline-none transition-colors focus:border-primary"
                    />
                    <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">min</span>
                  </div>
                </label>

                <div className="flex flex-col gap-1.5 rounded-xl bg-secondary/60 p-3">
                  <p className="flex items-center gap-1.5 text-xs text-muted-foreground">
                    <Trophy className="h-3.5 w-3.5 text-primary" />
                    Recorde pessoal: <span className="font-semibold text-foreground">{bestStreak} dias</span>
                  </p>
                </div>
              </div>

              <Button onClick={saveSettings} className="mt-5 w-full rounded-xl">
                Salvar
              </Button>
            </div>
          </div>
        )}

        {/* Header */}
        <header className="sticky top-0 z-10 flex items-center justify-between border-b border-border bg-background/80 px-5 py-4 backdrop-blur">
          <div className="flex items-center gap-2">
            <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-primary text-primary-foreground">
              <Droplets className="h-5 w-5" />
            </div>
            <h1 className="text-base font-semibold">Contador de Água</h1>
          </div>
          <div className="flex items-center gap-2">
            {!goalReached && (
              <div className="hidden items-center gap-1.5 rounded-full bg-secondary px-3 py-1.5 text-xs text-muted-foreground sm:flex">
                <Bell className="h-3.5 w-3.5" />
                <span>{countdownStr}</span>
              </div>
            )}
            {goalReached && (
              <div className="hidden items-center gap-1.5 rounded-full bg-primary/10 px-3 py-1.5 text-xs font-medium text-primary sm:flex">
                🎉 Meta atingida!
              </div>
            )}
            <button
              onClick={() => setShowHistory(true)}
              className="flex h-9 w-9 items-center justify-center rounded-full border border-border bg-card text-foreground transition-colors hover:bg-secondary"
              aria-label="Histórico"
            >
              <BarChart2 className="h-4 w-4" />
            </button>
            <button
              onClick={() => setDark((d) => !d)}
              className="flex h-9 w-9 items-center justify-center rounded-full border border-border bg-card text-foreground transition-colors hover:bg-secondary"
              aria-label="Alternar tema"
            >
              {dark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}
            </button>
            <button
              onClick={openSettings}
              className="flex h-9 w-9 items-center justify-center rounded-full border border-border bg-card text-foreground transition-colors hover:bg-secondary"
              aria-label="Configurações"
            >
              <Settings className="h-4 w-4" />
            </button>
          </div>
        </header>

        <main className="flex flex-col gap-6 px-5 py-6">
          {/* Reminder pill on mobile */}
          {!goalReached ? (
            <div className="flex items-center justify-center gap-1.5 rounded-full bg-secondary px-3 py-1.5 text-xs text-muted-foreground sm:hidden">
              <Bell className="h-3.5 w-3.5" />
              <span>Próximo lembrete: {countdownStr}</span>
            </div>
          ) : (
            <div className="flex items-center justify-center gap-1.5 rounded-full bg-primary/10 px-3 py-1.5 text-xs font-medium text-primary sm:hidden">
              🎉 Meta diária atingida! Parabéns!
            </div>
          )}

          {/* Hero */}
          <div className="text-center">
            <p className="text-4xl font-bold tracking-tight text-balance">
              {consumedMl} ml <span className="text-muted-foreground">/ {goalMl} ml</span>
            </p>
            <p className="mt-1.5 text-sm text-muted-foreground">
              {percent}% da meta diária
              {remaining > 0 ? ` · faltam ${remaining} ml` : " · ✅ concluído!"}
            </p>
          </div>

          {/* Bottle */}
          <WaterBottle percentage={percent} goal={goalMl} />

          {/* Quick add chips */}
          <div className="grid grid-cols-4 gap-3">
            {quickAdds.map(({ label, amount, icon: Icon }) => (
              <button
                key={label}
                onClick={() => addWater(amount)}
                disabled={goalReached}
                className="flex flex-col items-center gap-1.5 rounded-2xl border border-border bg-card px-2 py-3 text-foreground transition-colors hover:border-primary disabled:cursor-not-allowed disabled:opacity-50"
              >
                <Icon className="h-5 w-5 text-primary" />
                <span className="text-sm font-medium">{label}</span>
                <span className="text-xs text-muted-foreground">+{amount} ml</span>
              </button>
            ))}
          </div>

          {/* Manual input */}
          <div className="flex items-center gap-3">
            <div className="relative flex-1">
              <Droplet className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
              <input
                value={manual}
                onChange={(e) => setManual(e.target.value.replace(/[^0-9]/g, ""))}
                onKeyDown={(e) => e.key === "Enter" && addManual()}
                inputMode="numeric"
                placeholder="Quantidade"
                disabled={goalReached}
                className="h-11 w-full rounded-xl border border-border bg-card pl-9 pr-10 text-sm text-foreground outline-none transition-colors placeholder:text-muted-foreground focus:border-primary disabled:opacity-50"
              />
              <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">
                ml
              </span>
            </div>
            <Button onClick={addManual} disabled={goalReached} className="h-11 gap-1.5 rounded-xl px-4">
              <Plus className="h-4 w-4" />
              Adicionar
            </Button>
          </div>

          {/* Streak */}
          <StreakCard days={last7Days} streak={streak} bestStreak={bestStreak} />

          {/* Footer */}
          <footer className="flex flex-col items-center gap-2 pb-2">
            <button
              onClick={resetDay}
              className="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
            >
              <RefreshCw className="h-4 w-4" />
              Resetar dia
            </button>
            <p className="text-[11px] text-muted-foreground/50 select-none">
              © {new Date().getFullYear()} Adrian Souza
            </p>
          </footer>
        </main>
      </div>
    </div>
  )
}
