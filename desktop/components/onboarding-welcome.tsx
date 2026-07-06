"use client"

import { useEffect, useState } from "react"
import { Droplets, GlassWater } from "lucide-react"

const ONBOARDING_KEY = "agua_onboarding_v1"

type Props = {
  onFirstDrink: () => void
}

export function OnboardingWelcome({ onFirstDrink }: Props) {
  const [visible, setVisible] = useState(false)

  useEffect(() => {
    const seen = localStorage.getItem(ONBOARDING_KEY)
    if (!seen) setVisible(true)
  }, [])

  const dismiss = () => {
    localStorage.setItem(ONBOARDING_KEY, "1")
    setVisible(false)
  }

  const handleFirstDrink = () => {
    onFirstDrink()
    dismiss()
  }

  if (!visible) return null

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm p-4">
      <div className="w-full max-w-sm rounded-3xl border border-border bg-card p-6 shadow-2xl text-center animate-in fade-in zoom-in duration-300">
        {/* Ícone animado */}
        <div className="mx-auto mb-4 flex h-20 w-20 items-center justify-center rounded-full bg-gradient-to-br from-[#38bdf8] to-[#2563eb] shadow-lg shadow-blue-500/30 animate-bob">
          <Droplets className="h-10 w-10 text-white" />
        </div>

        <h2 className="mb-2 text-xl font-bold text-foreground">
          Bem-vindo ao seu novo hábito! 💧
        </h2>
        <p className="mb-6 text-sm text-muted-foreground leading-relaxed">
          Beber água regularmente melhora sua energia, foco e saúde.
          Vamos começar com o primeiro gole?
        </p>

        {/* Botão principal */}
        <button
          onClick={handleFirstDrink}
          className="flex w-full items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-[#38bdf8] to-[#2563eb] px-6 py-4 text-base font-semibold text-white transition-all hover:opacity-90 hover:scale-[1.02] active:scale-100"
        >
          <GlassWater className="h-5 w-5" />
          Beber primeiro copo! 🥛
        </button>

        {/* Pular */}
        <button
          onClick={dismiss}
          className="mt-4 w-full text-sm text-muted-foreground transition-colors hover:text-foreground"
        >
          Agora não, obrigado
        </button>

        {/* Mini-métrica */}
        <p className="mt-4 text-xs text-muted-foreground/60">
          ☝️ 76% dos brasileiros bebem menos água do que deveriam. Você está prestes a mudar isso.
        </p>
      </div>
    </div>
  )
}
