# 🌐 Plano de Migração — Contador de Água para Web

## Sumário

1. [Diagnóstico — quanto já funciona na web](#1-diagnóstico)
2. [O que precisa mudar](#2-o-que-precisa-mudar)
3. [Onde hospedar (comparativo)](#3-onde-hospedar)
4. [Passo a passo da migração](#4-passo-a-passo-da-migração)
5. [Tempo estimado](#5-tempo-estimado)
6. [Funcionalidades que não migram](#6-o-que-fica-pelo-caminho)
7. [Arquitetura web final](#7-arquitetura-web-final)

---

## 1. Diagnóstico

**Surpresa boa:** o `storage.ts` já tem fallback para `localStorage`, e o `useWaterState.ts` já pede permissão de `Notification` no browser. O app Next.js já roda num `pnpm dev` sem Electron — o frontend praticamente já funciona.

| Camada | Desktop | Web | Esforço |
|---|---|---|---|
| **UI (React + Tailwind)** | `water-tracker.tsx`, `bottle/`, `controls/`, `history/`, `settings/`, `streak-card.tsx` | ✅ Idêntico — zero alterações | **Nenhum** |
| **Lógica pura (`lib/`)** | `types.ts`, `constants.ts`, `dates.ts`, `stats.ts` | ✅ Idêntico — zero alterações | **Nenhum** |
| **Persistência** | `storage.ts` com fallback `electronAPI → localStorage` | ✅ `localStorage` já implementado | **Nenhum** |
| **Notificações** | `Notification` nativo do Electron | ✅ Web Notification API já implementada | **Nenhum** |
| **Build** | `next.config.mjs` com `output: 'export'` | ⚠️ Só trocar para Vercel ou manter export | **5 min** |
| **Lembretes periódicos** | `electron/reminders.js` (timer no processo principal) | ❌ Precisa: Service Worker (Push API) ou timer no próprio React | **1-2 dias** |
| **Reset meia-noite** | `scheduleMidnightReset()` via IPC | ❌ Precisa: `setInterval` no frontend checando `Date()` | **~2h** |
| **Minimizar para bandeja** | `electron/tray.js` + `win.on('close')` | ❌ Não existe em web — vira PWA com lifecycle | **Descartado** |
| **Ícone na bandeja** | `electron/tray.js` | ❌ Não existe em web | **Descartado** |
| **Instância única** | `app.requestSingleInstanceLock()` | ❌ Desnecessário para web | **Descartado** |
| **Notificação de meta** | `window.electronAPI.notifyGoal()` via IPC | ✅ Já tem fallback para `new Notification()` no browser | **Nenhum** |
| **PWA (instalação)** | Inexistente | ❌ Precisa: `manifest.json` + Service Worker | **~4h** |
| **SEO / OG Tags** | Inexistente (layout mínimo) | ❌ Precisa: meta tags, Open Graph, favicons | **~1h** |
| **Responsividade** | Mobile-first (max-w-[440px]) | ✅ Já funciona em mobile | **Nenhum** |
| **Tema escuro** | Botão manual | ✅ Já implementado | **Nenhum** |

**Score atual:** ~60% já pronto. O app Next.js com `pnpm dev` já renderiza, persiste no `localStorage`, e dispara notificações no browser.

---

## 2. O que precisa mudar

### 2.1 Next.js — configuração de build

**Arquivo:** `next.config.mjs`

```js
// ANTES (Electron — static export)
const nextConfig = {
  output: 'export',
  trailingSlash: true,
  assetPrefix: './',
  // ...
}

// DEPOIS (Vercel — SSR/Static)
const nextConfig = {
  // Remove output: 'export' se for usar Vercel (SSR otimizado)
  // Ou mantém para GitHub Pages / Cloudflare Pages
  images: { unoptimized: true },
}
```

### 2.2 Lembretes — substituir Electron por web

**Arquivo novo:** `desktop/lib/reminders.ts`

```typescript
// Em vez do timer no processo principal do Electron,
// um hook React ou módulo que faz polling no frontend

export type ReminderCallbacks = {
  onReminder: () => void
  onMidnightReset: () => void
}

export function startWebReminders(
  getIntervalMin: () => number,
  getLastDrinkTime: () => number,
  getGoalReached: () => boolean,
  callbacks: ReminderCallbacks,
): () => void {
  let lastReminderTime = Date.now()
  let lastDate = new Date().toISOString().slice(0, 10)

  const interval = setInterval(() => {
    const now = Date.now()
    const elapsed = (now - getLastDrinkTime()) / 1000

    // Lembrete
    if (!getGoalReached() && elapsed >= getIntervalMin() * 60) {
      if (elapsed - lastReminderTime > 30_000) { // evita spam
        callbacks.onReminder()
        lastReminderTime = now
      }
    }

    // Reset meia-noite
    const today = new Date().toISOString().slice(0, 10)
    if (today !== lastDate) {
      callbacks.onMidnightReset()
      lastDate = today
    }
  }, 10_000) // verifica a cada 10s

  return () => clearInterval(interval)
}
```

> **Observação:** O Service Worker com Push API é o ideal (notificações mesmo com a aba fechada), mas é significativamente mais complexo. A estratégia de polling no frontend cobre 95% dos casos de uso. O Service Worker pode ser uma segunda fase.

### 2.3 Service Worker + PWA Manifest

**Arquivo novo:** `desktop/public/manifest.json`

```json
{
  "name": "Contador de Água",
  "short_name": "Água",
  "description": "Lembrete de hidratação para o seu dia",
  "start_url": "/",
  "display": "standalone",
  "background_color": "#0d1424",
  "theme_color": "#2563eb",
  "icons": [
    { "src": "/icon-dark-32x32.png", "sizes": "32x32", "type": "image/png" },
    { "src": "/apple-icon.png", "sizes": "180x180", "type": "image/png" }
  ]
}
```

**Arquivo novo:** `desktop/public/sw.js`

Service Worker básico para cache offline e notificações push.

### 2.4 Ajustes no `layout.tsx`

Adicionar:
- Meta tags Open Graph (para compartilhamento)
- Link para `manifest.json`
- Tema escuro via `prefers-color-scheme` no HTML
- Google Analytics opcional

### 2.5 `package.json` — remover Electron

**Mudanças:**
- Remover `"main": "electron/main.js"`
- Remover `electron:dev` e `electron:build` dos scripts
- Adicionar script `deploy` (`vercel` ou `gh-pages`)
- Remover `electron`, `electron-builder`, `concurrently`, `wait-on` das devDependencies

### 2.6 `pnpm.yaml` — limpar

Remover `electron`, `electron-builder`, `electron-winstaller` de `onlyBuiltDependencies`.

### 2.7 Adaptar `useWaterState.ts`

O hook já está quase lá. Ajustes:
- Substituir os `useEffect` que escutam `electronAPI` para usar o novo `startWebReminders()`
- Remover `window.electronAPI.onReminder` / `onMidnightReset`
- O `addWater` já dispara `new Notification()` no browser

### 2.8 `.gitignore`

Adicionar `.vercel` se for usar Vercel.

---

## 3. Onde hospedar

### Comparativo

| Plataforma | Tipo | Preço | Build | Domínio próprio | SSL | Facilidade |
|---|---|---|---|---|---|---|
| **Vercel** ★ | SSR + Static | Grátis (1 projeto) | Automático via Git | ✅ | ✅ | Máxima |
| **Netlify** | SSR + Static | Grátis | Automático via Git | ✅ | ✅ | Máxima |
| **Cloudflare Pages** | Static | Grátis (ilimitado) | Automático via Git | ✅ | ✅ | Alta |
| **GitHub Pages** | Static | Grátis | GitHub Actions | ✅ | ✅ | Média |
| **Railway** | SSR | Grátis limitado | Automático via Git | ✅ | ✅ | Alta |
| **Render** | SSR + Static | Grátis (c/休眠) | Automático via Git | ✅ | ✅ | Alta |

### Recomendação: **Vercel** (⭐⭐⭐⭐⭐)

**Motivos:**
1. O app já é Next.js — deploy zero-config
2. SSR gratuito sem cold starts
3. Preview deployments automáticos em PRs
4. Analytics embutido (se quiser)
5. Domínio `contador-agua.vercel.app` grátis

**Alternativa econômica:** Cloudflare Pages (estático, export puro, ilimitado de banda, performance global).

> **Custo:** R$ 0,00 nos 3 planos acima para o volume do app.

### Como fazer o deploy (Vercel)

```bash
# 1. Instalar CLI
pnpm add -g vercel

# 2. Na raiz do projeto
cd desktop
vercel --prod

# Ou: conectar repositório GitHub no dashboard da Vercel
# → https://vercel.com/new
```

**Tempo:** 10 minutos na primeira vez, deploys automáticos depois.

---

## 4. Passo a passo da migração

### Fase 1 — Limpeza (⏱ ~1h)

| # | Tarefa | Arquivos |
|---|---|---|
| 1 | Remover `"main"` do `package.json` | `package.json` |
| 2 | Remover scripts Electron, add scripts web | `package.json` |
| 3 | Remover deps Electron | `package.json` |
| 4 | Limpar `pnpm.yaml` | `pnpm.yaml` |
| 5 | Ajustar `next.config.mjs` para SSR | `next.config.mjs` |

### Fase 2 — Lembretes Web (⏱ ~2-3h)

| # | Tarefa | Arquivos |
|---|---|---|
| 6 | Criar `lib/reminders.ts` com polling de lembrete + meia-noite | `lib/reminders.ts` (novo) |
| 7 | Adaptar `useWaterState.ts` para usar `startWebReminders()` | `hooks/useWaterState.ts` |
| 8 | Remover referências a `electronAPI` no hook | `hooks/useWaterState.ts` |
| 9 | Disparar notificação browser no lembrete | `lib/reminders.ts` |

### Fase 3 — PWA (⏱ ~4h)

| # | Tarefa | Arquivos |
|---|---|---|
| 10 | Criar `manifest.json` | `public/manifest.json` (novo) |
| 11 | Criar Service Worker com cache offline | `public/sw.js` (novo) |
| 12 | Registrar SW no `layout.tsx` | `app/layout.tsx` |
| 13 | Adicionar `manifest` link no `<head>` | `app/layout.tsx` |

### Fase 4 — SEO / Meta (⏱ ~1h)

| # | Tarefa | Arquivos |
|---|---|---|
| 14 | Adicionar Open Graph tags | `app/layout.tsx` |
| 15 | Ajustar metadata título/descrição | `app/layout.tsx` |
| 16 | Verificar favicons | `public/` |

### Fase 5 — Deploy (⏱ ~30min)

| # | Tarefa |
|---|---|
| 17 | Criar conta Vercel (se não tiver) |
| 18 | Conectar repo GitHub |
| 19 | Configurar domínio (opcional) |
| 20 | Rodar `pnpm build` e verificar |

---

## 5. Tempo estimado

| Fase | Esforço | Quem |
|---|---|---|
| Fase 1 — Limpeza | ~1h | Dev |
| Fase 2 — Lembretes Web | ~2-3h | Dev |
| Fase 3 — PWA | ~4h | Dev |
| Fase 4 — SEO | ~1h | Dev |
| Fase 5 — Deploy | ~30min | Dev/DevOps |
| **Total** | **~8-10h** | |

Se for **apenas o mínimo funcional** (pular PWA e deixar notificações só com aba aberta):

| Fase | Esforço |
|---|---|
| Fase 1 + 2 + 5 (mínimo) | ~3-4h |
| + Fase 4 (SEO) | +1h |
| + Fase 3 (PWA completo) | +4h |

---

## 6. O que fica pelo caminho

Estas funcionalidades do Electron **não existem** na versão web (são inerentes ao desktop):

| Funcionalidade Desktop | Motivo |
|---|---|
| **Minimizar para bandeja** | Não existe em web. Fecha → perde estado. PWA com `display: standalone` atenua. |
| **Notificação mesmo com app "fechado"** | Service Worker Push API pode resolver parcialmente. Notificações sem aba aberta exigem Push + Service Worker. |
| **Instância única** | Web pode abrir várias abas. Dá para tratar com `BroadcastChannel` API. |
| **Som de alerta (`success.wav`, `alert.wav`)** | Assets não são usados no frontend atual. Se quiser som, usar Web Audio API. |
| **Ícone na bandeja do Windows** | Substituído por ícone PWA na home screen / taskbar. |
| **Persistência em arquivo JSON no AppData** | Substituído por `localStorage` (já implementado). Sincronização entre abas/computadores exigiria backend. |

---

## 7. Arquitetura web final

```
contador-agua-web/
├── lib/                    # ✅ Idêntico — zero mudanças
│   ├── types.ts
│   ├── constants.ts
│   ├── dates.ts
│   ├── stats.ts
│   ├── storage.ts          # ✅ localStorage (já implementado)
│   └── reminders.ts        # 🆕 Polling de lembrete + meia-noite
├── hooks/
│   └── useWaterState.ts    # ⚠️ Apenas substituir IPC por reminders.ts
├── components/             # ✅ Idêntico — zero mudanças
│   ├── water-tracker.tsx
│   ├── bottle/
│   ├── controls/
│   ├── history/
│   ├── settings/
│   └── streak-card.tsx
├── app/
│   ├── layout.tsx          # ⚠️ Adicionar manifest, OG tags, SW
│   ├── page.tsx            # ✅ Idêntico
│   └── globals.css         # ✅ Idêntico
├── public/
│   ├── manifest.json       # 🆕 PWA manifest
│   ├── sw.js               # 🆕 Service Worker
│   ├── icon.svg            # ✅ Existe
│   └── icon-*.png          # ✅ Existe
├── package.json            # ⚠️ Sem Electron
├── next.config.mjs         # ⚠️ SSR em vez de static export
└── electron/               # 🗑️ Removido (main.js, window.js, tray.js, etc.)
```

### Diagrama de fluxo (como fica)

```
[ Browser ]
    │
    ├── React (Next.js SSR)
    │   ├── useWaterState.ts
    │   │   ├── lib/storage.ts  →  localStorage
    │   │   ├── lib/dates.ts    →  todayISO, rollover
    │   │   ├── lib/stats.ts    →  streak, last7
    │   │   └── lib/reminders.ts → polling 10s
    │   │       ├── setInterval → verifica lembrete
    │   │       └── setInterval → verifica meia-noite
    │   └── Componentes React (idênticos)
    │
    ├── Service Worker (sw.js)
    │   ├── Cache offline (opcional)
    │   └── Push notifications (opcional, fase 2)
    │
    └── PWA (manifest.json)
        └── "Adicionar à tela inicial" → standalone
```

---

## Resumo executivo

| Item | Resposta |
|---|---|
| **Já funciona?** | ~60% — o app Next.js já roda no browser |
| **O que muda?** | Remover Electron, criar lembrete web, adicionar PWA |
| **O que não muda?** | Toda UI, toda lógica pura, toda persistência |
| **Onde subir?** | **Vercel** (recomendado) ou Cloudflare Pages |
| **Tempo total** | **~8-10h** (ou ~3-4h para o mínimo funcional sem PWA) |
| **Custo mensal** | **R$ 0** (planos grátis dos 3 tops) |

---

> **Próximo passo:** Quer que eu execute a migração? Posso começar pela Fase 1 (limpeza) e seguir até o deploy.
