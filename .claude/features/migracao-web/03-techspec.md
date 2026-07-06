# 03-TECHSPEC.md — Arquitetura Técnica

## Arquivos impactados

### 🆕 Criados
| Arquivo | Função |
|---|---|
| `lib/supabase.ts` | Cliente Supabase (server + browser) |
| `lib/reminders.ts` | Polling de lembrete + reset meia-noite |
| `components/auth/login.tsx` | Tela de login/cadastro |
| `components/auth/auth-guard.tsx` | Protetor de rota (redireciona se não logado) |
| `app/auth/page.tsx` | Página de login |
| `app/auth/callback/page.tsx` | Callback OAuth do Supabase |
| `public/manifest.json` | PWA manifest |
| `public/sw.js` | Service Worker |
| `.env.local.example` | Template de variáveis de ambiente |

### 🔁 Modificados
| Arquivo | Mudança |
|---|---|
| `lib/storage.ts` | Adicionar sync com Supabase, manter localStorage como fallback |
| `lib/types.ts` | Remover tipo ElectronAPI, adicionar tipo User |
| `hooks/useWaterState.ts` | Substituir electronAPI por chamadas Supabase |
| `components/water-tracker.tsx` | Adicionar verificação de auth, melhorias de layout |
| `app/layout.tsx` | Adicionar metadata, manifest, tema |
| `app/page.tsx` | Adicionar AuthGuard |
| `app/globals.css` | Ajustes de cor e animação |

### 🗑️ Removidos
| Arquivo | Motivo |
|---|---|
| `electron/` (pasta inteira) | Só servia pro Electron |
| `pnpm-workspace.yaml` | Só tinha config de Electron |
| `assets/icon.ico`, `assets/convert_icon.py` | Só para build Electron |

## Contratos de API

### Supabase — Tabelas

```sql
-- profiles: estende auth.users com config do usuário
create table profiles (
  id          uuid primary key references auth.users(id),
  email       text,
  goal_ml     integer not null default 2000,
  interval_min integer not null default 30,
  best_streak integer not null default 0,
  created_at  timestamptz default now()
);

-- water_entries: 1 linha por dia por usuário
create table water_entries (
  id          uuid primary key default gen_random_uuid(),
  user_id     uuid references profiles(id) not null,
  date        date not null,
  consumed_ml integer not null default 0,
  goal_ml     integer not null default 2000,
  created_at  timestamptz default now(),
  updated_at  timestamptz default now(),
  unique(user_id, date)
);
```

### Supabase — Storage Adapter

```typescript
// lib/supabase.ts — cliente singleton
createBrowserClient(supabaseUrl, supabaseAnonKey)

// lib/storage.ts — interface unificada
loadState(): Promise<AppState>
  → 1. Tenta Supabase (buscar profile + última entry)
  → 2. Fallback: localStorage
  → 3. Retorna defaults se ambos vazios

saveState(s: AppState): void
  → 1. Salva no Supabase (upsert water_entries)
  → 2. Salva no localStorage (fallback offline)
```

## Fluxo de dados

```
Usuário clica "Copo (+200ml)"
  → useWaterState.addWater(200)
    → setState (React)
    → lib/storage.ts saveState()
      → Supabase: upsert water_entries (se logado)
      → localStorage: save (sempre)
```

## Variáveis de ambiente

```bash
NEXT_PUBLIC_SUPABASE_URL=       # Supabase project URL
NEXT_PUBLIC_SUPABASE_ANON_KEY=  # Supabase anon key
```
