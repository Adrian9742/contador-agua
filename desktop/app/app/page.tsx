import { AuthGuard } from "@/components/auth/auth-guard"
import { WaterTracker } from "@/components/water-tracker"

export default function AppPage() {
  return (
    <AuthGuard>
      <WaterTracker />
    </AuthGuard>
  )
}
