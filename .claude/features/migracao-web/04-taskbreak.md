# 04-TASKBREAK.md — Tarefas da Migração

> Ordem obrigatória. Nunca pular etapas.
> Cada task só começa quando a anterior estiver concluída e verificada.

---

## 🎯 Tarefas

### Fase 1 — Limpeza ✅ CONCLUÍDA
- [x] 1.1 Remover Electron do `package.json` (scripts, deps, build config)
- [x] 1.2 Limpar `pnpm.yaml`
- [x] 1.3 Ajustar `next.config.mjs` para SSR/Vercel
- [x] 1.4 Atualizar `.gitignore`
- [x] 1.5 Remover pasta `electron/`
- [ ] 1.6 Instalar dependências (`pnpm install`)

### Fase 2 — Supabase Setup
- [ ] 2.1 Criar projeto Supabase (pelo dashboard)
- [ ] 2.2 Criar tabela `profiles` + `water_entries`
- [ ] 2.3 Configurar Auth (email + Google)
- [ ] 2.4 Criar `lib/supabase.ts` (cliente browser)
- [ ] 2.5 Criar `.env.local.example`

### Fase 3 — Auth (Login/Cadastro)
- [ ] 3.1 Criar `components/auth/login.tsx`
- [ ] 3.2 Criar `components/auth/auth-guard.tsx`
- [ ] 3.3 Criar `app/auth/page.tsx`
- [ ] 3.4 Criar `app/auth/callback/page.tsx`
- [ ] 3.5 Adaptar `app/layout.tsx` para sessão

### Fase 4 — Storage + Supabase
- [ ] 4.1 Atualizar `lib/types.ts` (remover ElectronAPI, adicionar User)
- [ ] 4.2 Reescrever `lib/storage.ts` (localStorage + Supabase)
- [ ] 4.3 Atualizar `hooks/useWaterState.ts` (substituir electronAPI)

### Fase 5 — Web Lembretes
- [ ] 5.1 Criar `lib/reminders.ts` (polling + notificação)
- [ ] 5.2 Integrar no `useWaterState.ts`

### Fase 6 — Layout
- [ ] 6.1 Melhorar `water-tracker.tsx` (layout novo)
- [ ] 6.2 Ajustar `app/globals.css` (cores, animações)
- [ ] 6.3 Melhorar componentes visuais

### Fase 7 — PWA
- [ ] 7.1 Criar `public/manifest.json`
- [ ] 7.2 Criar `public/sw.js`
- [ ] 7.3 Registrar no `layout.tsx`

### Fase 8 — Deploy
- [ ] 8.1 Criar projeto Vercel
- [ ] 8.2 Configurar env vars
- [ ] 8.3 Deploy
- [ ] 8.4 Testar em produção
