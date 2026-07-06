import { STORAGE_KEY, DEFAULT_GOAL_ML, DEFAULT_INTERVAL_MIN } from "./constants"
import type { AppState } from "./types"
import { todayISO } from "./dates"
import { getSupabase } from "./supabase"

const DEFAULTS: AppState = {
  goalMl: DEFAULT_GOAL_ML,
  intervalMin: DEFAULT_INTERVAL_MIN,
  consumedMl: 0,
  lastDrinkTime: 0,
  dailyHistory: {},
  bestStreak: 0,
  lastDate: "",
}

function freshState(): AppState {
  return { ...DEFAULTS, lastDate: todayISO(), lastDrinkTime: Date.now() }
}

export { DEFAULTS }

// ── localStorage (síncrono, sempre funciona) ────────────

function loadLocal(): AppState | null {
  try {
    const raw = localStorage.getItem(STORAGE_KEY)
    return raw ? { ...DEFAULTS, ...JSON.parse(raw) } : null
  } catch {
    return null
  }
}

function saveLocal(s: AppState): void {
  try {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(s))
  } catch { /* quota excedida, ignora */ }
}

// ── Supabase (assíncrono, apenas se logado) ─────────────

async function loadFromSupabase(userId: string): Promise<AppState | null> {
  const supabase = getSupabase()

  // Pega perfil
  const { data: profile } = await supabase
    .from("profiles")
    .select("goal_ml, interval_min, best_streak")
    .eq("id", userId)
    .single()

  if (!profile) return null

  // Pega entradas dos últimos 30 dias
  const thirtyDaysAgo = new Date()
  thirtyDaysAgo.setDate(thirtyDaysAgo.getDate() - 30)
  const from = thirtyDaysAgo.toISOString().slice(0, 10)

  const { data: entries } = await supabase
    .from("water_entries")
    .select("date, consumed_ml, goal_ml")
    .eq("user_id", userId)
    .gte("date", from)
    .order("date", { ascending: false })

  const dailyHistory: Record<string, { consumed: number; goal: number }> = {}
  let todayConsumed = 0
  let lastDate = ""

  if (entries) {
    for (const e of entries) {
      dailyHistory[e.date] = { consumed: e.consumed_ml, goal: e.goal_ml }
      if (!lastDate || e.date > lastDate) lastDate = e.date
    }
    const today = todayISO()
    const todayEntry = entries.find((e) => e.date === today)
    if (todayEntry) todayConsumed = todayEntry.consumed_ml
  }

  return {
    goalMl: profile.goal_ml ?? DEFAULT_GOAL_ML,
    intervalMin: profile.interval_min ?? DEFAULT_INTERVAL_MIN,
    consumedMl: todayConsumed,
    lastDrinkTime: Date.now(),
    dailyHistory,
    bestStreak: profile.best_streak ?? 0,
    lastDate: lastDate || todayISO(),
  }
}

async function saveToSupabase(userId: string, s: AppState): Promise<void> {
  const supabase = getSupabase()
  const today = todayISO()

  // Atualiza perfil (goal, intervalo, streak)
  await supabase.from("profiles").upsert({
    id: userId,
    goal_ml: s.goalMl,
    interval_min: s.intervalMin,
    best_streak: s.bestStreak,
  })

  // Salva entrada de hoje
  await supabase.from("water_entries").upsert({
    user_id: userId,
    date: today,
    consumed_ml: s.consumedMl,
    goal_ml: s.goalMl,
  }, { onConflict: "user_id, date" })
}

// ── Merge: junta dados do servidor com dados locais ─────

function mergeStates(server: AppState, local: AppState | null): AppState {
  if (!local) return server

  // Se o dado local é mais recente (tem consumo hoje), prioriza local
  const today = todayISO()
  const localIsToday = local.lastDate === today
  const serverIsToday = server.lastDate === today

  if (localIsToday && !serverIsToday) {
    // Local tem dado de hoje, servidor não → mescla
    return {
      ...server,
      consumedMl: local.consumedMl,
      lastDrinkTime: local.lastDrinkTime,
      lastDate: today,
      dailyHistory: {
        ...server.dailyHistory,
        ...local.dailyHistory,
        [today]: { consumed: local.consumedMl, goal: local.goalMl },
      },
      bestStreak: Math.max(server.bestStreak, local.bestStreak),
    }
  }

  if (serverIsToday && !localIsToday) return server

  // Ambos têm ou nenhum tem → server wins para configs, local wins para consumo do dia
  return {
    ...server,
    consumedMl: localIsToday ? Math.max(server.consumedMl, local.consumedMl) : server.consumedMl,
    lastDrinkTime: Math.max(server.lastDrinkTime, local.lastDrinkTime),
    dailyHistory: {
      ...server.dailyHistory,
      ...local.dailyHistory,
    },
    bestStreak: Math.max(server.bestStreak, local.bestStreak),
  }
}

// ── API pública ─────────────────────────────────────────

export async function loadState(): Promise<AppState> {
  // 1. Sempre carrega do localStorage primeiro
  const local = loadLocal()

  // 2. Tenta carregar do Supabase (se logado)
  try {
    const supabase = getSupabase()
    const { data: { session } } = await supabase.auth.getSession()
    if (session?.user) {
      const server = await loadFromSupabase(session.user.id)
      if (server) return mergeStates(server, local)
    }
  } catch { /* offline ou erro — segue com localStorage */ }

  return local ?? freshState()
}

export function saveState(s: AppState): void {
  // 1. Sempre salva local (instantâneo)
  saveLocal(s)

  // 2. Fire-and-forget: sincroniza com Supabase em background
  getSupabase().auth.getSession().then(({ data: { session } }) => {
    if (session?.user) {
      saveToSupabase(session.user.id, s).catch(() => {})
    }
  }).catch(() => {})
}
