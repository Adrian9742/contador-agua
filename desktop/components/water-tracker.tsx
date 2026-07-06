"use client"

import { useState } from "react"
import Link from "next/link"
import { Droplets, Settings, BarChart2, LogOut, Bell, RefreshCw, LogIn } from "lucide-react"
import { WaterBottle }   from "@/components/bottle"
import { Controls }      from "@/components/controls"
import { HistoryModal }  from "@/components/history"
import { SettingsModal } from "@/components/settings"
import { StreakCard }     from "@/components/streak-card"
import { OnboardingWelcome } from "@/components/onboarding-welcome"
import { useWaterState } from "@/hooks/useWaterState"
import { useAuth }       from "@/hooks/useAuth"

export function WaterTracker() {
  const {
    consumedMl, goalMl, intervalMin,
    percent, remaining, streak, last7Days,
    dailyHistory, goalReached, countdownStr,
    bestStreak, hydrated,
    addWater, resetDay, setGoal, setIntervalMin,
  } = useWaterState()

  const { user, signOut } = useAuth()

  const [showSettings, setShowSettings] = useState(false)
  const [showHistory, setShowHistory]   = useState(false)

  if (!hydrated) {
    return (
      <div className="mx-auto flex min-h-screen w-full max-w-[440px] items-center justify-center bg-background md:max-w-3xl">
        <Droplets className="h-8 w-8 animate-pulse text-primary" />
      </div>
    )
  }

  return (
    <div className="mx-auto min-h-screen w-full max-w-[440px] bg-background text-foreground md:max-w-4xl lg:max-w-6xl md:px-10 lg:px-12">

      {/* Modais */}
      <OnboardingWelcome onFirstDrink={() => addWater(200)} />

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

      {/* ── Header ──────────────────────────────────────── */}
      <header className="sticky top-0 z-10 flex items-center justify-between border-b border-border bg-background/80 px-5 py-4 backdrop-blur md:rounded-b-2xl md:px-6">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-[#38bdf8] to-[#2563eb] shadow-sm">
            <Droplets className="h-5 w-5 text-white" />
          </div>
          <div>
            <h1 className="text-sm font-semibold leading-tight">Contador de Água</h1>
            {user?.email && (
              <p className="text-[11px] text-muted-foreground leading-tight">{user.email}</p>
            )}
          </div>
        </div>
        <div className="flex items-center gap-1.5">
          <HeaderBtn onClick={() => setShowHistory(true)}  title="Histórico"><BarChart2 className="h-4 w-4" /></HeaderBtn>
          <HeaderBtn onClick={() => setShowSettings(true)} title="Configurações"><Settings className="h-4 w-4" /></HeaderBtn>
          {user ? (
            <HeaderBtn onClick={signOut} title="Sair"><LogOut className="h-4 w-4" /></HeaderBtn>
          ) : (
            <Link
              href="/auth"
              className="flex h-9 items-center gap-1.5 rounded-xl bg-gradient-to-r from-[#38bdf8] to-[#2563eb] px-3 text-xs font-semibold text-white transition-opacity hover:opacity-90"
            >
              <LogIn className="h-3.5 w-3.5" />
              Entrar
            </Link>
          )}
        </div>
      </header>

      {!user && (
        <div className="mx-5 mt-3 flex items-center gap-2 rounded-xl border border-[#38bdf8]/20 bg-[#38bdf8]/5 px-4 py-2.5 md:mx-0">
          <span className="text-lg">💾</span>
          <p className="flex-1 text-xs text-muted-foreground">
            <strong className="text-foreground">Dados salvos no navegador.</strong>{" "}
            Crie uma conta para sincronizar seu histórico entre dispositivos.
          </p>
          <Link
            href="/auth"
            className="shrink-0 rounded-lg bg-gradient-to-r from-[#38bdf8] to-[#2563eb] px-3 py-1.5 text-xs font-semibold text-white transition-opacity hover:opacity-90"
          >
            Criar conta
          </Link>
        </div>
      )}

      <main className="flex flex-col gap-5 px-5 py-6 md:px-0 md:py-8">

        {/* ── Banner / Timer ──────────────────────────────── */}
        {goalReached ? (
          <div className="flex items-center gap-3 rounded-2xl bg-gradient-to-r from-green-500/10 to-blue-500/10 border border-green-500/20 px-4 py-3">
            <span className="text-2xl">🎉</span>
            <div>
              <p className="text-sm font-semibold text-green-400">Meta diária atingida!</p>
              <p className="text-xs text-muted-foreground">
                {consumedMl} ml consumidos — parabéns! 🥤
              </p>
            </div>
          </div>
        ) : (
          <div className="flex flex-wrap items-center gap-2">
            <div className="flex items-center gap-1.5 rounded-full bg-secondary px-3 py-1.5 text-xs text-muted-foreground">
              <Bell className="h-3.5 w-3.5" />
              <span>Próximo lembrete: <strong className="text-foreground">{countdownStr}</strong></span>
            </div>
            <div className="flex items-center gap-1.5 rounded-full bg-secondary px-3 py-1.5 text-xs text-muted-foreground">
              🔔 a cada <strong className="text-foreground">{intervalMin} min</strong>
            </div>
          </div>
        )}

        {/* ── Grid responsivo ──────────────────────────────── */}
        <div className="flex flex-col gap-5 md:flex-row md:items-start md:gap-10 lg:gap-16">

          {/* Coluna esquerda — consumo + garrafa */}
          <div className="flex flex-col gap-5 md:w-1/2">
            <div className="flex items-center justify-between">
              <div>
                <p className="text-[40px] font-extrabold leading-none tracking-tight text-foreground md:text-5xl">
                  <span className="text-[#38bdf8]">{consumedMl}</span> ml
                </p>
                <p className="mt-1 text-base text-muted-foreground">
                  de <strong className="text-foreground">{goalMl}</strong> ml
                </p>
                <div className="mt-2 flex items-center gap-2">
                  <div className="h-2 w-24 overflow-hidden rounded-full bg-secondary md:w-32">
                    <div
                      className="h-full rounded-full bg-gradient-to-r from-[#38bdf8] to-[#2563eb] transition-[width] duration-500"
                      style={{ width: `${percent}%` }}
                    />
                  </div>
                  <span className="text-xs font-medium text-[#38bdf8]">{percent}%</span>
                </div>
              </div>
              <div className="flex h-20 w-20 items-center justify-center rounded-2xl bg-gradient-to-br from-[#38bdf8]/20 to-[#2563eb]/10 text-4xl md:h-24 md:w-24 md:text-5xl">
                🫗
              </div>
            </div>
            <WaterBottle percentage={percent} goal={goalMl} />
          </div>

          {/* Coluna direita — controles + streak */}
          <div className="flex flex-col gap-5 md:w-1/2 md:pt-16">
            {!goalReached && (
              <div className="hidden md:flex items-center gap-2 rounded-2xl border border-border bg-card p-4">
                <div className="flex h-12 w-12 items-center justify-center rounded-xl bg-[#38bdf8]/10 text-2xl">⏰</div>
                <div>
                  <p className="text-sm font-medium">Próximo lembrete em</p>
                  <p className="text-2xl font-bold text-[#38bdf8]">{countdownStr}</p>
                </div>
              </div>
            )}
            <Controls goalReached={goalReached} onAdd={addWater} />
            <StreakCard days={last7Days} streak={streak} bestStreak={bestStreak} />
          </div>
        </div>

        {/* ── Footer ──────────────────────────────────────── */}
        <footer className="flex flex-col items-center gap-2 pb-4 pt-2">
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
  )
}

function HeaderBtn({ onClick, title, children }: { onClick: () => void; title: string; children: React.ReactNode }) {
  return (
    <button
      onClick={onClick}
      className="flex h-9 w-9 items-center justify-center rounded-xl border border-border bg-card text-muted-foreground transition-colors hover:bg-secondary hover:text-foreground"
      title={title}
    >
      {children}
    </button>
  )
}
