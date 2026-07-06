# 01-RESEARCH.md — Migração Contador de Água para Web

## Objetivo
Migrar o app desktop Contador de Água (Electron + Next.js) para uma aplicação web pública com autenticação, persistência em nuvem e deploy na Vercel.

## Stack atual (Desktop)
- Next.js 16 + React 19 + Tailwind CSS v4
- Electron 36 (desktop wrapper)
- shadcn/ui (componentes)
- Lucide React (ícones)
- localStorage (persistência, já com fallback para web)
- Notifications API (já implementada no browser como fallback)

## Stack alvo (Web)
- Next.js 16 + React 19 + Tailwind CSS v4 (mantido)
- Supabase (autenticação + banco PostgreSQL)
- PWA (Service Worker + manifest.json)
- Vercel (deploy)

## Descobertas da análise de código

### Já funciona na web (0 esforço)
- ✅ `lib/storage.ts` — já tem fallback para `localStorage` quando `electronAPI` não existe
- ✅ `useWaterState.ts` — já pede permissão `Notification` no browser
- ✅ Toda UI (`components/`, `app/`, `hooks/`) — React puro, sem dependência de Electron
- ✅ Toda lógica pura (`lib/`) — zero dependência de runtime
- ✅ Build Next.js já existe

### Precisa mudar
| Item | Arquivos | Esforço |
|---|---|---|
| Remover Electron | `electron/*`, `package.json`, `pnpm.yaml`, `next.config.mjs` | ✅ Feito |
| Adicionar Supabase | `lib/supabase.ts` (novo) | ~1h |
| Auth (login/cadastro) | `app/auth/`, `components/auth/` | ~3h |
| Substituir storage | `lib/storage.ts`, `hooks/useWaterState.ts` | ~2h |
| Lembretes web | `lib/reminders.ts` (novo) | ~1h |
| PWA | `public/manifest.json`, `public/sw.js` | ~2h |
| Layout melhorado | `components/`, `app/globals.css` | ~3h |
| Deploy | Vercel | ~30min |

### Decisões de projeto
1. **Login obrigatório** — o app será público, cada usuário vê seu histórico
2. **Supabase Auth** — email + Google OAuth
3. **Dados na nuvem** — histórico sincronizado entre dispositivos
4. **Fallback localStorage** — manter para experiência offline básica
5. **Sem backend próprio** — Supabase BaaS resolve

## Riscos identificados
- Sincronização entre localStorage e Supabase em modo offline
- Conflito de dados se usuário usar dois dispositivos simultaneamente
- Perda de notificações se Service Worker não for configurado corretamente
