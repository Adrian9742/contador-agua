# 💧 Contador de Água

App web que te lembra de beber água durante o dia — ideal pra quem passa horas na frente do PC e esquece de se hidratar.

🌐 **https://contador-agua.vercel.app**

---

## ✨ Funcionalidades

- **Garrafa animada** que enche conforme você registra o consumo
- **Lembretes no navegador** em intervalos configuráveis (padrão: 30 min)
- **Histórico de 30 dias** com gráfico de barras (meta atingida, parcial, sem registro)
- **Sequência de dias** (streak) e melhor recorde pessoal
- **Sincronia na nuvem** — faça login e seus dados acompanham você em qualquer PC
- **Landing page pública** com SEO
- **Design responsivo** — funciona no celular e no desktop
- **Reset automático à meia-noite** — mesmo se o PC estiver ligado, o dia vira sozinho
- **Detecta dias perdidos** — se você não abriu o app por alguns dias, eles aparecem como zero no histórico
- **Tema escuro**
- **Meta e intervalo de lembrete configuráveis**

---

## 🛠️ Tecnologias

| Camada | Stack |
|---|---|
| Interface | Next.js 16 + React 19 + Tailwind CSS v4 |
| Ícones | Lucide React |
| Autenticação | Supabase Auth (email + senha) |
| Banco de dados | Supabase PostgreSQL |
| Persistência | localStorage + Supabase (sync) |
| PWA | manifest.json + Service Worker |
| Deploy | Vercel |

---

## 🚀 Como usar

1. Acesse **https://contador-agua.vercel.app**
2. Crie sua conta (ou use sem login — dados salvos no navegador)
3. Ao abrir, a garrafa começa vazia
4. Clique nos botões **🥛 Copo**, **🫗 Gole**, **🧃 Dose**, **🧴 Garrafa** ou digite a quantidade manualmente
5. Você receberá notificações quando esquecer de beber água
6. Clique no ícone 📊 no cabeçalho para ver o histórico dos últimos 30 dias

---

## 🧑‍💻 Desenvolvimento local

```bash
# 1. Clonar
git clone https://github.com/Adrian9742/contador-agua.git
cd contador-agua/desktop

# 2. Instalar dependências
pnpm install

# 3. Configurar variáveis de ambiente
cp .env.local.example .env.local
# Preencha NEXT_PUBLIC_SUPABASE_URL e NEXT_PUBLIC_SUPABASE_ANON_KEY

# 4. Rodar em modo dev
pnpm dev
# → http://localhost:3000

# 5. Build
pnpm build
```

### Requisitos
- Node.js 18+
- pnpm 9+
- Conta no [Supabase](https://supabase.com) (grátis)

---

## 🏗️ Arquitetura

```
contador-agua/
├── desktop/                    # 🖥 App web (Next.js + Supabase)
│   ├── lib/                    # Lógica pura (types, constants, dates, stats, storage, supabase)
│   ├── hooks/                  # useWaterState.ts + useAuth.tsx
│   ├── components/
│   │   ├── auth/               # Login, AuthGuard
│   │   ├── bottle/             # Garrafa animada
│   │   ├── controls/           # Botões rápidos + entrada manual
│   │   ├── history/            # Modal + gráfico SVG 30 dias
│   │   ├── settings/           # Modal de meta/intervalo
│   │   └── streak-card.tsx     # Card de sequência de dias
│   ├── app/                    # Next.js App Router
│   │   ├── page.tsx            # Landing page (pública)
│   │   ├── app/page.tsx        # App (protegido)
│   │   └── auth/page.tsx       # Login/Cadastro
│   ├── public/                 # Ícones, PWA, Service Worker
│   └── electron/               # 🗑️ Removido na migração web
├── legacy-python/              # 🐍 Versão original (somente referência)
└── docs/                       # Screenshots, migração, changelog
```

---

## 📝 Licença

MIT © [Adrian Souza](https://github.com/Adrian9742) — use, modifique e distribua à vontade.
