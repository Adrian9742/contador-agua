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
      <section className="relative mx-auto flex max-w-5xl flex-col items-center px-6 pt-20 pb-16 text-center md:pt-28 overflow-hidden">
        {/* Background layers */}
        <div className="pointer-events-none absolute inset-0 -z-10">
          <img src="/hero-bg.png" alt="" className="h-full w-full object-cover opacity-30" />
        </div>
        <div className="pointer-events-none absolute inset-0 -z-10 opacity-40">
          <img src="/waves-bg.svg" alt="" className="h-full w-full object-cover" />
        </div>
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
            Começar grátis em 30s
          </Link>
          <p className="-mt-2 text-xs text-muted-foreground">
            🥤 Sem cartão. Sem compromisso.
          </p>
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
        <div className="mt-16 w-full max-w-xs mx-auto">
          <img
            src="/phone-mockup.jpg"
            alt="App Contador de Água rodando no celular"
            className="w-full rounded-3xl border border-border shadow-2xl shadow-[#2563eb]/10"
          />
          <p className="mt-3 text-center text-xs text-muted-foreground">
            📱 App rodando — 2.500 ml de meta, 70% concluído
          </p>
        </div>
      </section>

      {/* ── Features ──────────────────────────────────── */}
      <section className="mx-auto max-w-5xl px-6 py-20">
        <h2 className="mb-4 text-center text-3xl font-bold">Por que usar?</h2>
        <p className="mb-12 text-center text-lg text-muted-foreground">
          Mais de 70% do seu corpo é água. O app que te ajuda a manter o hábito.
        </p>

        {/* Foto + depoimento */}
        <div className="mb-16 flex flex-col items-center gap-8 md:flex-row md:gap-12">
          <div className="w-full max-w-sm overflow-hidden rounded-2xl border border-border md:w-1/2">
            <img
              src="/man-drinking.jpg"
              alt="Pessoa bebendo água no escritório"
              className="h-full w-full object-cover"
            />
          </div>
          <div className="flex flex-col gap-4 md:w-1/2">
            <div className="inline-flex w-fit rounded-full bg-[#38bdf8]/10 px-3 py-1 text-xs text-[#38bdf8]">
              📊 Segundo a ciência
            </div>
            <p className="text-lg leading-relaxed text-muted-foreground md:text-xl">
              "A desidratação leve já prejudica o foco, a memória e o humor. 
              Manter-se hidratado ao longo do dia melhora a produtividade 
              em até <strong className="text-foreground">14%</strong> 
              segundo estudos da Universidade de Harvard."
            </p>
            <p className="text-sm text-muted-foreground">
              <ExternalLink className="inline h-3.5 w-3.5" /> Fonte: 
              <a href="https://www.hsph.harvard.edu/nutritionsource/water/" target="_blank" className="text-[#38bdf8] hover:underline">
                Harvard T.H. Chan School of Public Health
              </a>
            </p>
          </div>
        </div>

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

      {/* ── Como funciona ──────────────────────────────── */}
      <section className="mx-auto max-w-4xl px-6 py-16 text-center">
        <h2 className="mb-4 text-3xl font-bold">Como funciona</h2>
        <p className="mb-10 text-lg text-muted-foreground">
          Em 4 passos simples você cria o hábito de se hidratar.
        </p>

        {/* Passos em HTML direto (mais confiável que SVG) */}
        <div className="flex flex-col items-center gap-6 md:flex-row md:gap-4">

          {/* Passo 1 */}
          <div className="flex flex-col items-center gap-2">
            <div className="flex h-20 w-20 items-center justify-center rounded-2xl border border-border bg-card text-3xl shadow-lg shadow-[#38bdf8]/5">
              🔔
            </div>
            <p className="text-sm font-semibold text-foreground">Lembrete</p>
            <p className="text-xs text-muted-foreground">A cada 30 min</p>
          </div>

          {/* Seta */}
          <div className="hidden text-2xl text-muted-foreground/30 md:block">→</div>
          <div className="block text-2xl text-muted-foreground/30 md:hidden">↓</div>

          {/* Passo 2 */}
          <div className="flex flex-col items-center gap-2">
            <div className="flex h-20 w-20 items-center justify-center rounded-2xl border border-border bg-card text-3xl shadow-lg shadow-[#38bdf8]/5">
              🥤
            </div>
            <p className="text-sm font-semibold text-foreground">Beber</p>
            <p className="text-xs text-muted-foreground">200 / 250 / 500 / 750 ml</p>
          </div>

          {/* Seta */}
          <div className="hidden text-2xl text-muted-foreground/30 md:block">→</div>
          <div className="block text-2xl text-muted-foreground/30 md:hidden">↓</div>

          {/* Passo 3 */}
          <div className="flex flex-col items-center gap-2">
            <div className="flex h-20 w-20 items-center justify-center rounded-2xl border border-border bg-card text-3xl shadow-lg shadow-[#38bdf8]/5">
              🫗
            </div>
            <p className="text-sm font-semibold text-foreground">Garrafa enche</p>
            <p className="text-xs text-muted-foreground">+10% / +20% / +30%</p>
          </div>

          {/* Seta */}
          <div className="hidden text-2xl text-muted-foreground/30 md:block">→</div>
          <div className="block text-2xl text-muted-foreground/30 md:hidden">↓</div>

          {/* Passo 4 */}
          <div className="flex flex-col items-center gap-2">
            <div className="flex h-20 w-20 items-center justify-center rounded-2xl border border-border bg-card text-3xl shadow-lg shadow-[#f59e0b]/5">
              🔥
            </div>
            <p className="text-sm font-semibold text-foreground">Streak</p>
            <p className="text-xs text-muted-foreground">Dias seguidos</p>
          </div>

        </div>

        <p className="mt-6 text-sm font-medium text-[#22c55e]">🎯 Meta!</p>
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
          Criar conta grátis 🚀
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
