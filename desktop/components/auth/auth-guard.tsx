"use client"

import { useAuth } from "@/hooks/useAuth"
import { useRouter } from "next/navigation"
import { useEffect } from "react"
import { Droplets } from "lucide-react"

export function AuthGuard({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth()
  const router = useRouter()

  useEffect(() => {
    if (!loading && !user) {
      router.push("/auth")
    }
  }, [user, loading, router])

  if (loading) {
    return (
      <div className="mx-auto flex min-h-screen w-full max-w-[440px] items-center justify-center bg-background">
        <Droplets className="h-8 w-8 animate-pulse text-primary" />
      </div>
    )
  }

  if (!user) return null

  return <>{children}</>
}
