"use client"

import { Flame, Check } from "lucide-react"
import type { DayInfo } from "@/hooks/useWaterState"

interface StreakCardProps {
  days: DayInfo[]
  streak: number
  bestStreak: number
}

export function StreakCard({ days, streak, bestStreak }: StreakCardProps) {
  const subtitle =
    streak === 0
      ? "Beba água para começar!"
      : streak === 1
        ? "Primeiro dia — continue!"
        : `${streak} dias seguidos!`

  return (
    <div className="rounded-2xl border border-border bg-card p-5">
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-3">
          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-primary/10 text-primary">
            <Flame className="h-5 w-5" />
          </div>
          <div>
            <p className="text-lg font-semibold leading-tight text-foreground">
              {streak} {streak === 1 ? "dia seguido" : "dias seguidos"}
            </p>
            <p className="text-sm text-muted-foreground">{subtitle}</p>
          </div>
        </div>
        <div className="text-right">
          <p className="text-xs text-muted-foreground">Recorde</p>
          <p className="text-sm font-semibold text-foreground">
            {bestStreak} {bestStreak === 1 ? "dia" : "dias"}
          </p>
        </div>
      </div>

      <div className="mt-5 flex items-center justify-between">
        {days.map((day) => (
          <div key={day.date} className="flex flex-col items-center gap-2">
            <DayCircle day={day} />
            <span className="text-xs text-muted-foreground">{day.label}</span>
          </div>
        ))}
      </div>
    </div>
  )
}

function DayCircle({ day }: { day: DayInfo }) {
  if (day.status === "done") {
    return (
      <div className="flex h-9 w-9 items-center justify-center rounded-full bg-primary text-primary-foreground">
        <Check className="h-4 w-4" />
      </div>
    )
  }

  if (day.status === "today") {
    const pct = day.percentage ?? 0
    return (
      <div
        className="flex h-9 w-9 items-center justify-center rounded-full"
        style={{
          background: `conic-gradient(var(--primary) ${pct}%, var(--secondary) ${pct}% 100%)`,
        }}
      >
        <div className="flex h-7 w-7 items-center justify-center rounded-full bg-card text-[10px] font-semibold text-foreground">
          {pct}%
        </div>
      </div>
    )
  }

  // failed — empty circle
  return <div className="h-9 w-9 rounded-full border border-border bg-secondary/50" />
}
