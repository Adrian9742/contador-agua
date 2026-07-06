"use client"

import { useState, useRef } from "react"
import { useRouter } from "next/navigation"
import { Droplets, Mail, Lock, Eye, EyeOff, Loader2, AlertTriangle } from "lucide-react"
import { getSupabase } from "@/lib/supabase"

const MAX_ATTEMPTS = 5
const LOCKOUT_SECONDS = 30

export function LoginPage() {
  const [email, setEmail] = useState("")
  const [password, setPassword] = useState("")
  const [showPw, setShowPw] = useState(false)
  const [mode, setMode] = useState<"login" | "register">("login")
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)
  const [success, setSuccess] = useState<string | null>(null)
  const [attempts, setAttempts] = useState(0)
  const [lockout, setLockout] = useState(0)
  const lockTimer = useRef<NodeJS.Timeout | null>(null)
  const router = useRouter()

  const startLockout = () => {
    setLockout(LOCKOUT_SECONDS)
    lockTimer.current = setInterval(() => {
      setLockout((prev) => {
        if (prev <= 1) {
          if (lockTimer.current) clearInterval(lockTimer.current)
          setAttempts(0)
          return 0
        }
        return prev - 1
      })
    }, 1000)
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setError(null)
    setSuccess(null)

    // Rate limit check
    if (lockout > 0) {
      setError(`Muitas tentativas. Tente novamente em ${lockout}s.`)
      return
    }

    setLoading(true)

    const supabase = getSupabase()

    if (mode === "login") {
      const { error } = await supabase.auth.signInWithPassword({ email, password })
      if (error) {
        const newAttempts = attempts + 1
        setAttempts(newAttempts)
        if (newAttempts >= MAX_ATTEMPTS) {
          startLockout()
          setError(`Muitas tentativas. Aguarde ${LOCKOUT_SECONDS}s para tentar novamente.`)
        } else {
          setError(`Email ou senha incorretos. Restam ${MAX_ATTEMPTS - newAttempts} tentativas.`)
        }
      } else {
        router.push("/app")
      }
    } else {
      const { error } = await supabase.auth.signUp({ email, password })
      if (error) {
        setError(error.message)
      } else {
        setSuccess("Conta criada! Verifique seu email para confirmar o cadastro.")
      }
    }
    setLoading(false)
  }

  return (
    <div className="mx-auto flex min-h-screen w-full max-w-[440px] flex-col items-center justify-center bg-background px-6">
      {/* Logo */}
      <div className="mb-8 flex flex-col items-center gap-3">
        <div className="flex h-16 w-16 items-center justify-center rounded-2xl bg-gradient-to-br from-[#38bdf8] to-[#2563eb] shadow-lg shadow-blue-500/20">
          <Droplets className="h-8 w-8 text-white" />
        </div>
        <h1 className="text-2xl font-bold text-foreground">Contador de Água</h1>
        <p className="text-sm text-muted-foreground">
          {mode === "login" ? "Entre na sua conta" : "Crie sua conta"}
        </p>
      </div>

      {/* Form */}
      <form onSubmit={handleSubmit} className="flex w-full flex-col gap-4">
        {/* Email */}
        <label className="flex flex-col gap-1.5">
          <span className="text-sm font-medium text-foreground">Email</span>
          <div className="relative">
            <Mail className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              placeholder="seu@email.com"
              required
              className="h-11 w-full rounded-xl border border-border bg-card pl-10 pr-4 text-sm text-foreground outline-none transition-colors placeholder:text-muted-foreground focus:border-primary"
            />
          </div>
        </label>

        {/* Senha */}
        <label className="flex flex-col gap-1.5">
          <span className="text-sm font-medium text-foreground">Senha</span>
          <div className="relative">
            <Lock className="pointer-events-none absolute left-3 top-1/2 h-4 w-4 -translate-y-1/2 text-muted-foreground" />
            <input
              type={showPw ? "text" : "password"}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              placeholder="mínimo 6 caracteres"
              minLength={6}
              required
              className="h-11 w-full rounded-xl border border-border bg-card pl-10 pr-10 text-sm text-foreground outline-none transition-colors placeholder:text-muted-foreground focus:border-primary"
            />
            <button
              type="button"
              onClick={() => setShowPw(!showPw)}
              className="absolute right-3 top-1/2 -translate-y-1/2 text-muted-foreground hover:text-foreground"
            >
              {showPw ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
            </button>
          </div>
        </label>

        {/* Error / Success */}
        {error && (
          <p className="rounded-xl bg-red-500/10 px-4 py-3 text-sm text-red-400">{error}</p>
        )}
        {success && (
          <p className="rounded-xl bg-green-500/10 px-4 py-3 text-sm text-green-400">{success}</p>
        )}

        {/* Lockout warning */}
        {lockout > 0 && (
          <div className="flex items-center gap-2 rounded-xl bg-amber-500/10 border border-amber-500/20 px-4 py-3 text-sm text-amber-400">
            <AlertTriangle className="h-4 w-4 shrink-0" />
            <span>Muitas tentativas. Aguarde <strong>{lockout}s</strong> para tentar novamente.</span>
          </div>
        )}

        {/* Submit */}
        <button
          type="submit"
          disabled={loading || lockout > 0}
          className="flex h-11 items-center justify-center gap-2 rounded-xl bg-gradient-to-r from-[#38bdf8] to-[#2563eb] text-sm font-semibold text-white transition-all hover:opacity-90 disabled:opacity-50"
        >
          {loading && <Loader2 className="h-4 w-4 animate-spin" />}
          {mode === "login" ? "Entrar" : "Criar conta"}
        </button>
      </form>

      {/* Toggle mode */}
      <p className="mt-6 text-sm text-muted-foreground">
        {mode === "login" ? "Não tem conta? " : "Já tem conta? "}
        <button
          onClick={() => { setMode(mode === "login" ? "register" : "login"); setError(null); setSuccess(null) }}
          className="font-medium text-primary hover:underline"
        >
          {mode === "login" ? "Cadastre-se" : "Fazer login"}
        </button>
      </p>
    </div>
  )
}
