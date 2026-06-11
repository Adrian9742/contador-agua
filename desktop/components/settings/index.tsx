"use client"

import { useState } from "react"
import { X, Target, Clock, Trophy } from "lucide-react"
import { Button } from "@/components/ui/button"

interface SettingsModalProps {
  goalMl: number
  intervalMin: number
  bestStreak: number
  onSave: (goalMl: number, intervalMin: number) => void
  onClose: () => void
}

export function SettingsModal({ goalMl, intervalMin, bestStreak, onSave, onClose }: SettingsModalProps) {
  const [goalInput, setGoalInput]         = useState(String(goalMl))
  const [intervalInput, setIntervalInput] = useState(String(intervalMin))

  const save = () => {
    const g = Number.parseInt(goalInput, 10)
    const i = Number.parseInt(intervalInput, 10)
    onSave(
      !Number.isNaN(g) && g >= 100  ? g : goalMl,
      !Number.isNaN(i) && i >= 1    ? i : intervalMin,
    )
    onClose()
  }

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-black/60 backdrop-blur-sm sm:items-center"
      onClick={onClose}
    >
      <div
        className="w-full max-w-[440px] rounded-t-3xl border border-border bg-card p-6 shadow-2xl sm:rounded-3xl"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="mb-5 flex items-center justify-between">
          <h2 className="text-base font-semibold">Configurações</h2>
          <button
            onClick={onClose}
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

        <Button onClick={save} className="mt-5 w-full rounded-xl">
          Salvar
        </Button>
      </div>
    </div>
  )
}
