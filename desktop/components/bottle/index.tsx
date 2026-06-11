"use client"

type WaterBottleProps = {
  percentage: number
  goal?: number
}

export function WaterBottle({ percentage, goal = 2000 }: WaterBottleProps) {
  const clamped = Math.min(100, Math.max(0, percentage))
  const mid = Math.round(goal / 2)

  return (
    <div className="flex items-center justify-center gap-4 py-2">
      <div className="relative animate-bob" aria-hidden="true">
        {/* Cap */}
        <div className="mx-auto h-5 w-16 rounded-t-md bg-foreground/20" />
        <div className="mx-auto -mt-1 h-3 w-12 rounded-sm bg-foreground/15" />

        {/* Bottle body */}
        <div className="relative mt-1 h-72 w-40 overflow-hidden rounded-[2rem] border border-border bg-secondary/60 backdrop-blur">
          {/* Water */}
          <div
            className="absolute bottom-0 left-0 right-0 transition-[height] duration-700 ease-out"
            style={{
              height: `${clamped}%`,
              background: "linear-gradient(to bottom, var(--water-from), var(--water-to))",
            }}
          >
            <div className="absolute -top-3 left-0 h-6 w-[200%] animate-wave">
              <Wave className="h-6 w-1/2 text-[var(--water-from)]" />
              <Wave className="absolute left-1/2 top-0 h-6 w-1/2 text-[var(--water-from)]" />
            </div>
            <div className="absolute -top-2 left-0 h-5 w-[200%] animate-wave-slow opacity-60">
              <Wave className="h-5 w-1/2 text-[var(--water-to)]" />
              <Wave className="absolute left-1/2 top-0 h-5 w-1/2 text-[var(--water-to)]" />
            </div>
          </div>

          {/* Shine */}
          <div className="pointer-events-none absolute left-3 top-4 h-56 w-3 rounded-full bg-white/30" />
          <div className="pointer-events-none absolute left-7 top-6 h-40 w-1.5 rounded-full bg-white/20" />

          {/* Percentage badge */}
          <div className="absolute left-1/2 top-5 -translate-x-1/2">
            <span className="rounded-full bg-card/90 px-3 py-1 text-sm font-semibold text-foreground shadow-sm ring-1 ring-border">
              {Math.round(clamped)}%
            </span>
          </div>
        </div>
      </div>

      {/* ml scale */}
      <div className="flex h-72 flex-col justify-between py-1 text-xs text-muted-foreground">
        <ScaleTick label={`${goal} ml`} />
        <ScaleTick label={`${mid} ml`} />
        <ScaleTick label="0 ml" />
      </div>
    </div>
  )
}

function ScaleTick({ label }: { label: string }) {
  return (
    <div className="flex items-center gap-1.5">
      <span className="h-px w-3 bg-border" />
      <span>{label}</span>
    </div>
  )
}

function Wave({ className }: { className?: string }) {
  return (
    <svg viewBox="0 0 120 24" preserveAspectRatio="none" className={className} fill="currentColor">
      <path d="M0 12 C 20 0, 40 0, 60 12 S 100 24, 120 12 L120 24 L0 24 Z" />
    </svg>
  )
}
