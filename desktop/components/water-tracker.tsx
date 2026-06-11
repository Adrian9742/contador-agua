"use client"

import { useState } from "react"
import { Droplets, Moon, Sun, Settings, Bell, RefreshCw, BarChart2 } from "lucide-react"
import { WaterBottle }   from "@/components/bottle"
import { Controls }      from "@/components/controls"
import { HistoryModal }  from "@/components/history"
import { SettingsModal } from "@/components/settings"
import { StreakCard }     from "@/components/streak-card"
import { useWaterState } from "@/hooks/useWaterState"

export function WaterTracker() {
  const {
    consumedMl, goalMl, intervalMin,
    percent, remaining, streak, last7Days,
    dailyHistory, goalReached, countdownStr,
    bestStreak, hydrated,
    addWater, resetDay, setGoal, setIntervalMin,
  } = useWaterState()

  const [dark, setDark]               = useState(true)
  const [showSettings, setShowSettings] = useState(false)
  const [showHistory, setShowHistory]   = useState(false)

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

        {showSettings && (
          <SettingsModal
            goalMl={goalMl}
            intervalMin={intervalMin}
            bestStreak={bestStreak}
            onSave={(g, i) => { setGoal(g); setIntervalMin(i) }}
            onClose={() => setShowSettings(false)}
          />
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
            {!goalReached ? (
              <div className="hidden items-center gap-1.5 rounded-full bg-secondary px-3 py-1.5 text-xs text-muted-foreground sm:flex">
                <Bell className="h-3.5 w-3.5" />
                <span>{countdownStr}</span>
              </div>
            ) : (
              <div className="hidden items-center gap-1.5 rounded-full bg-primary/10 px-3 py-1.5 text-xs font-medium text-primary sm:flex">
                🎉 Meta atingida!
              </div>
            )}
            <HeaderBtn onClick={() => setShowHistory(true)}  aria="Histórico"><BarChart2 className="h-4 w-4" /></HeaderBtn>
            <HeaderBtn onClick={() => setDark((d) => !d)}    aria="Alternar tema">{dark ? <Sun className="h-4 w-4" /> : <Moon className="h-4 w-4" />}</HeaderBtn>
            <HeaderBtn onClick={() => setShowSettings(true)} aria="Configurações"><Settings className="h-4 w-4" /></HeaderBtn>
          </div>
        </header>

        <main className="flex flex-col gap-6 px-5 py-6">
          {/* Reminder pill (mobile) */}
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

          <WaterBottle percentage={percent} goal={goalMl} />
          <Controls goalReached={goalReached} onAdd={addWater} />
          <StreakCard days={last7Days} streak={streak} bestStreak={bestStreak} />

          <footer className="flex flex-col items-center gap-2 pb-2">
            <button
              onClick={resetDay}
              className="flex items-center gap-1.5 rounded-lg px-3 py-2 text-sm text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
            >
              <RefreshCw className="h-4 w-4" />
              Resetar dia
            </button>
            <p className="select-none text-[11px] text-muted-foreground/50">
              © {new Date().getFullYear()} Adrian Souza
            </p>
          </footer>
        </main>
      </div>
    </div>
  )
}

function HeaderBtn({ onClick, aria, children }: { onClick: () => void; aria: string; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      className="flex h-9 w-9 items-center justify-center rounded-full border border-border bg-card text-foreground transition-colors hover:bg-secondary"
      aria-label={aria}
    >
      {children}
    </button>
  )
}
