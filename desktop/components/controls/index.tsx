"use client"

import { useState } from "react"
import { Droplet, GlassWater, Coffee, Milk, Plus } from "lucide-react"
import { Button } from "@/components/ui/button"
import { QUICK_ADDS } from "@/lib/constants"

const ICONS = [GlassWater, Droplet, Coffee, Milk]

interface ControlsProps {
  goalReached: boolean
  onAdd: (ml: number) => void
}

export function Controls({ goalReached, onAdd }: ControlsProps) {
  const [manual, setManual] = useState("")

  const addManual = () => {
    const value = Number.parseInt(manual, 10)
    if (!Number.isNaN(value) && value > 0) {
      onAdd(value)
      setManual("")
    }
  }

  return (
    <>
      {/* Quick add chips */}
      <div className="grid grid-cols-4 gap-3">
        {QUICK_ADDS.map(({ label, amount }, i) => {
          const Icon = ICONS[i]
          return (
            <button
              key={label}
              onClick={() => onAdd(amount)}
              disabled={goalReached}
              className="flex flex-col items-center gap-1.5 rounded-2xl border border-border bg-card px-2 py-3 text-foreground transition-colors hover:border-primary disabled:cursor-not-allowed disabled:opacity-50"
            >
              <Icon className="h-5 w-5 text-primary" />
              <span className="text-sm font-medium">{label}</span>
              <span className="text-xs text-muted-foreground">+{amount} ml</span>
            </button>
          )
        })}
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
          <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">ml</span>
        </div>
        <Button onClick={addManual} disabled={goalReached} className="h-11 gap-1.5 rounded-xl px-4">
          <Plus className="h-4 w-4" />
          Adicionar
        </Button>
      </div>
    </>
  )
}
