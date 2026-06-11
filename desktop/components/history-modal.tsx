"use client"

import { X, TrendingUp, Target, Flame, Trophy } from "lucide-react"
import type { DailyHistory } from "@/hooks/useWaterState"

interface Props {
  dailyHistory: DailyHistory
  goalMl: number
  consumedMl: number
  streak: number
  bestStreak: number
  onClose: () => void
}

function buildLast30(dailyHistory: DailyHistory, goalMl: number, consumedMl: number) {
  const days: { date: string; label: string; consumed: number; goal: number }[] = []
  const today = new Date()
  for (let i = 29; i >= 0; i--) {
    const d = new Date(today)
    d.setDate(d.getDate() - i)
    const key = d.toISOString().slice(0, 10)
    const dd = String(d.getDate()).padStart(2, "0")
    const mm = String(d.getMonth() + 1).padStart(2, "0")
    const label = `${dd}/${mm}`
    if (i === 0) {
      days.push({ date: key, label, consumed: consumedMl, goal: goalMl })
    } else {
      const entry = dailyHistory[key]
      days.push({ date: key, label, consumed: entry?.consumed ?? 0, goal: entry?.goal ?? goalMl })
    }
  }
  return days
}

export function HistoryModal({ dailyHistory, goalMl, consumedMl, streak, bestStreak, onClose }: Props) {
  const days = buildLast30(dailyHistory, goalMl, consumedMl)
  const todayKey = new Date().toISOString().slice(0, 10)

  // Stats
  const metDays   = days.filter((d) => d.consumed >= d.goal).length
  const knownDays = days.filter((d) => d.consumed > 0).length
  const totalConsumed = days.reduce((s, d) => s + d.consumed, 0)
  const avgMl = knownDays > 0 ? Math.round(totalConsumed / knownDays) : 0

  // SVG chart dimensions
  const W = 380
  const H = 160
  const barW = Math.floor(W / 30) - 2
  const maxVal = Math.max(goalMl * 1.1, ...days.map((d) => d.consumed), 1)

  const barX = (i: number) => i * (W / 30) + (W / 30 - barW) / 2

  const barColor = (d: typeof days[0]) => {
    if (d.date === todayKey) return d.consumed >= d.goal ? "#22c55e" : "#3b82f6"
    if (d.consumed === 0) return "#374151"
    if (d.consumed >= d.goal) return "#22c55e"
    return "#f97316"
  }

  const goalY = H - (goalMl / maxVal) * H

  // Show only every 5th label to avoid crowding
  const xLabels = days.filter((_, i) => i === 0 || (i + 1) % 5 === 0)

  return (
    <div
      className="fixed inset-0 z-50 flex items-end justify-center bg-black/70 backdrop-blur-sm sm:items-center"
      onClick={onClose}
    >
      <div
        className="w-full max-w-[440px] rounded-t-3xl border border-border bg-card pb-6 shadow-2xl sm:rounded-3xl"
        onClick={(e) => e.stopPropagation()}
      >
        {/* Handle */}
        <div className="flex justify-center pt-3">
          <div className="h-1.5 w-10 rounded-full bg-border" />
        </div>

        {/* Title bar */}
        <div className="flex items-center justify-between px-5 pt-4 pb-2">
          <h2 className="text-base font-semibold">Histórico — 30 dias</h2>
          <button
            onClick={onClose}
            className="flex h-8 w-8 items-center justify-center rounded-full border border-border text-muted-foreground hover:bg-secondary"
          >
            <X className="h-4 w-4" />
          </button>
        </div>

        {/* Stats grid */}
        <div className="grid grid-cols-2 gap-3 px-5 pt-2 pb-4">
          <StatCard icon={<Target className="h-4 w-4 text-green-500" />} label="Meta atingida" value={`${metDays}/30 dias`} />
          <StatCard icon={<TrendingUp className="h-4 w-4 text-blue-400" />} label="Média diária" value={avgMl > 0 ? `${avgMl} ml` : "—"} />
          <StatCard icon={<Flame className="h-4 w-4 text-orange-400" />} label="Sequência atual" value={`${streak} dia${streak !== 1 ? "s" : ""}`} />
          <StatCard icon={<Trophy className="h-4 w-4 text-yellow-400" />} label="Melhor sequência" value={`${bestStreak} dia${bestStreak !== 1 ? "s" : ""}`} />
        </div>

        {/* Chart */}
        <div className="px-5">
          <div className="overflow-x-auto rounded-2xl border border-border bg-background p-3">
            <svg width={W} height={H + 28} style={{ display: "block" }}>
              {/* Goal line */}
              <line
                x1={0}
                y1={goalY}
                x2={W}
                y2={goalY}
                stroke="#3b82f6"
                strokeWidth={1}
                strokeDasharray="4 3"
                opacity={0.5}
              />

              {/* Bars */}
              {days.map((d, i) => {
                const barH = Math.max(3, (d.consumed / maxVal) * H)
                const y = H - barH
                const x = barX(i)
                const isToday = d.date === todayKey
                return (
                  <g key={d.date}>
                    {/* Background slot */}
                    <rect x={x} y={0} width={barW} height={H} rx={3} fill="transparent" />
                    {/* Bar */}
                    <rect
                      x={x}
                      y={y}
                      width={barW}
                      height={barH}
                      rx={3}
                      fill={barColor(d)}
                      opacity={isToday ? 1 : 0.85}
                    />
                    {/* Today highlight ring */}
                    {isToday && (
                      <rect
                        x={x - 1}
                        y={y - 1}
                        width={barW + 2}
                        height={barH + 2}
                        rx={4}
                        fill="none"
                        stroke="#fff"
                        strokeWidth={1}
                        opacity={0.4}
                      />
                    )}
                  </g>
                )
              })}

              {/* X-axis labels (every 5 days) */}
              {days.map((d, i) => {
                if (i !== 0 && (i + 1) % 5 !== 0) return null
                return (
                  <text
                    key={d.date}
                    x={barX(i) + barW / 2}
                    y={H + 18}
                    textAnchor="middle"
                    fontSize={9}
                    fill="#6b7280"
                  >
                    {d.label}
                  </text>
                )
              })}
            </svg>
          </div>
        </div>

        {/* Legend */}
        <div className="mt-3 flex items-center justify-center gap-4 px-5 text-xs text-muted-foreground">
          <LegendDot color="#22c55e" label="Meta atingida" />
          <LegendDot color="#f97316" label="Parcial" />
          <LegendDot color="#374151" label="Sem registro" />
          <LegendDot color="#3b82f6" border label="Meta" dashed />
        </div>
      </div>
    </div>
  )
}

function StatCard({ icon, label, value }: { icon: React.ReactNode; label: string; value: string }) {
  return (
    <div className="flex flex-col gap-1 rounded-xl bg-secondary/60 px-3 py-3">
      <span className="flex items-center gap-1.5 text-xs text-muted-foreground">
        {icon}
        {label}
      </span>
      <span className="text-sm font-semibold">{value}</span>
    </div>
  )
}

function LegendDot({
  color,
  label,
  border,
  dashed,
}: {
  color: string
  label: string
  border?: boolean
  dashed?: boolean
}) {
  if (dashed) {
    return (
      <span className="flex items-center gap-1">
        <svg width={16} height={8}>
          <line x1={0} y1={4} x2={16} y2={4} stroke={color} strokeWidth={1.5} strokeDasharray="3 2" />
        </svg>
        {label}
      </span>
    )
  }
  return (
    <span className="flex items-center gap-1">
      <span
        className="inline-block h-2.5 w-2.5 rounded-sm"
        style={{ background: color, border: border ? `1.5px solid ${color}` : undefined }}
      />
      {label}
    </span>
  )
}
