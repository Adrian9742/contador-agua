import Link from "next/link"
import { Droplets, BarChart2, Bell, Flame, Smartphone, Globe, ExternalLink } from "lucide-react"

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-[#0d1424] via-[#111827] to-[#0d1424] text-foreground">

      {/* ── Hero ─────────────────────────────────────── */}
      <header className="mx-auto flex max-w-5xl items-center justify-between px-6 py-5">
        <div className="flex items-center gap-2.5">
          <div className="flex h-9 w-9 items-center justify-center rounded-xl bg-gradient-to-br from-[#38bdf8] to-[#2563eb]">
            <Droplets className="h-5 w-5 text-white" />
          </div>
          <span className="text-lg font-bold">Contador de Água</span>
        </div>
        <nav className="flex items-center gap-4">
          <Link
            href="/auth"
            className="text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            Entrar
          </Link>
          <Link
            href="/auth"
            className="rounded-xl bg-gradient-to-r from-[#38bdf8] to-[#2563eb] px-4 py-2 text-sm font-semibold text-white transition-opacity hover:opacity-90"
          >
            Começar grátis
          </Link>
        </nav>
      </header>

      {/* ── Hero Section ──────────────────────────────── */}
      <section className="mx-auto flex max-w-5xl flex-col items-center px-6 pt-20 pb-16 text-center md:pt-28">
        <div className="mb-6 rounded-full bg-[#38bdf8]/10 px-4 py-1.5 text-sm text-[#38bdf8]">
          🚀 App gratuito &bull; Open source
        </div>
        <h1 className="mb-4 text-4xl font-extrabold leading-tight tracking-tight md:text-6xl md:leading-[1.1]">
          Nunca mais esqueça<br />
          de <span className="bg-gradient-to-r from-[#38bdf8] to-[#818cf8] bg-clip-text text-transparent">beber água</span>
        </h1>
        <p className="mb-8 max-w-2xl text-lg text-muted-foreground md:text-xl">
          Um app simples que te lembra de se hidratar durante o dia.
          Acompanhe seu consumo, veja seu histórico e crie o hábito saudável.
        </p>
        <div className="flex gap-3">
          <Link
            href="/auth"
            className="rounded-xl bg-gradient-to-r from-[#38bdf8] to-[#2563eb] px-6 py-3 text-base font-semibold text-white transition-all hover:opacity-90 hover:scale-105"
          >
            Começar agora 🥤
          </Link>
          <a
            href="https://github.com/Adrian9742/contador-agua"
            target="_blank"
            className="flex items-center gap-2 rounded-xl border border-border bg-card px-5 py-3 text-sm text-muted-foreground transition-colors hover:text-foreground"
          >
            <ExternalLink className="h-4 w-4" />
            GitHub
          </a>
        </div>

        {/* Mockup / Screenshot */}
        <div className="mt-16 w-full max-w-sm rounded-3xl border border-border bg-card p-2 shadow-2xl shadow-[#2563eb]/5">
          <div className="rounded-2xl bg-[#111827] p-5">
            <div className="flex items-center justify-between border-b border-border pb-3">
              <div className="flex items-center gap-2">
                <div className="h-8 w-8 rounded-lg bg-gradient-to-br from-[#38bdf8] to-[#2563eb]" />
                <span className="text-sm font-semibold">Contador de Água</span>
              </div>
              <div className="flex gap-1.5">
                <div className="h-7 w-7 rounded-lg border border-border" />
                <div className="h-7 w-7 rounded-lg border border-border" />
              </div>
            </div>
            <div className="mt-4 flex items-end justify-between">
              <div>
                <p className="text-3xl font-extrabold"><span className="text-[#38bdf8]">1.500</span> ml</p>
                <p className="text-sm text-muted-foreground">de 2.000 ml</p>
                <div className="mt-2 h-2 w-24 rounded-full bg-secondary">
                  <div className="h-full w-3/4 rounded-full bg-gradient-to-r from-[#38bdf8] to-[#2563eb]" />
                </div>
              </div>
              <div className="text-4xl">🫗</div>
            </div>
            <div className="mt-4 grid grid-cols-4 gap-2">
              {["🥛", "🫗", "🧃", "🧴"].map((icon, i) => (
                <div key={i} className="rounded-xl border border-border bg-card p-2 text-center text-lg">{icon}</div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* ── Features ──────────────────────────────────── */}
      <section className="mx-auto max-w-5xl px-6 py-20">
        <h2 className="mb-12 text-center text-3xl font-bold">Por que usar?</h2>
        <div className="grid gap-6 md:grid-cols-3">
          <FeatureCard
            icon={<Bell className="h-6 w-6 text-[#38bdf8]" />}
            title="Lembretes inteligentes"
            desc="Notificações no navegador no intervalo que você escolher. Nunca passa sede."
          />
          <FeatureCard
            icon={<BarChart2 className="h-6 w-6 text-[#38bdf8]" />}
            title="Histórico de 30 dias"
            desc="Veja seu progresso com gráficos, streak de dias e média diária de consumo."
          />
          <FeatureCard
            icon={<Flame className="h-6 w-6 text-[#38bdf8]" />}
            title="Streak & Recorde"
            desc="Mantenha a sequência de dias batendo a meta. Seu recorde pessoal te motiva."
          />
          <FeatureCard
            icon={<Smartphone className="h-6 w-6 text-[#38bdf8]" />}
            title="Funciona em qualquer lugar"
            desc="Use no PC, no celular ou no tablet. Seus dados sincronizam automaticamente."
          />
          <FeatureCard
            icon={<Globe className="h-6 w-6 text-[#38bdf8]" />}
            title="100% gratuito"
            desc="Sem anúncios, sem planos pagos. Código aberto no GitHub."
          />
          <FeatureCard
            icon={<Droplets className="h-6 w-6 text-[#38bdf8]" />}
            title="Garrafa animada"
            desc="Encha a garrafa virtual a cada gole. Visual satisfatório que motiva a beber mais."
          />
        </div>
      </section>

      {/* ── CTA ────────────────────────────────────────── */}
      <section className="mx-auto max-w-3xl px-6 py-20 text-center">
        <h2 className="mb-4 text-3xl font-bold">Pronto pra se hidratar?</h2>
        <p className="mb-8 text-lg text-muted-foreground">
          2 minutos para criar sua conta. Grátis para sempre.
        </p>
        <Link
          href="/auth"
          className="inline-block rounded-xl bg-gradient-to-r from-[#38bdf8] to-[#2563eb] px-8 py-3 text-lg font-semibold text-white transition-all hover:opacity-90 hover:scale-105"
        >
          Criar minha conta 🚀
        </Link>
      </section>

      {/* ── Footer ────────────────────────────────────── */}
      <footer className="border-t border-border py-8 text-center text-sm text-muted-foreground">
        <p>© {new Date().getFullYear()} Adrian Souza &mdash; Feito com 💧</p>
        <a href="https://github.com/Adrian9742/contador-agua" target="_blank" className="mt-2 inline-flex items-center gap-1 hover:text-foreground">
          <ExternalLink className="h-4 w-4" /> Código aberto no GitHub
        </a>
      </footer>
    </div>
  )
}

function FeatureCard({ icon, title, desc }: { icon: React.ReactNode; title: string; desc: string }) {
  return (
    <div className="rounded-2xl border border-border bg-card p-6 transition-all hover:border-[#38bdf8]/30 hover:shadow-lg hover:shadow-[#2563eb]/5">
      <div className="mb-3 flex h-12 w-12 items-center justify-center rounded-xl bg-[#38bdf8]/10">
        {icon}
      </div>
      <h3 className="mb-2 text-lg font-semibold">{title}</h3>
      <p className="text-sm leading-relaxed text-muted-foreground">{desc}</p>
    </div>
  )
}
