"use client"

import { useState } from "react"
import { Plus, Droplet } from "lucide-react"
import { Button } from "@/components/ui/button"
import { QUICK_ADDS } from "@/lib/constants"

const ICONS = ["🥛", "🫗", "🧃", "🧴"]

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
      <div className="grid grid-cols-4 gap-2.5">
        {QUICK_ADDS.map(({ label, amount }, i) => (
          <button
            key={label}
            onClick={() => onAdd(amount)}
            disabled={goalReached}
            className="flex flex-col items-center gap-1 rounded-2xl border border-border bg-card px-2 py-3 text-foreground transition-all hover:border-[#38bdf8] hover:bg-[#38bdf8]/5 hover:-translate-y-0.5 active:translate-y-0 disabled:cursor-not-allowed disabled:opacity-50"
          >
            <span className="text-xl">{ICONS[i]}</span>
            <span className="text-sm font-medium">{label}</span>
            <span className="text-[11px] text-muted-foreground">+{amount} ml</span>
          </button>
        ))}
      </div>

      {/* Manual input */}
      {!goalReached && (
        <div className="flex items-center gap-2.5">
          <div className="relative flex-1">
            <Droplet className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input
              value={manual}
              onChange={(e) => setManual(e.target.value.replace(/[^0-9]/g, ""))}
              onKeyDown={(e) => e.key === "Enter" && addManual()}
              inputMode="numeric"
              placeholder="Quantidade em ml"
              className="h-11 w-full rounded-xl border border-border bg-card pl-9 pr-10 text-sm text-foreground outline-none transition-colors placeholder:text-muted-foreground focus:border-[#38bdf8]"
            />
            <span className="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 text-xs text-muted-foreground">ml</span>
          </div>
          <Button onClick={addManual} className="h-11 gap-1.5 rounded-xl px-4">
            <Plus className="h-4 w-4" />
            Adicionar
          </Button>
        </div>
      )}
    </>
  )
}
