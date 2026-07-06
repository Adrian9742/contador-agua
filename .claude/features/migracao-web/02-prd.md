# 02-PRD.md — Product Requirements Document

## Escopo
Migrar o app desktop para web, adicionando autenticação para múltiplos usuários e persistência em nuvem.

## Casos de uso

### UC1 — Primeiro acesso
- Usuário acessa `contador-agua.vercel.app`
- Vê tela de login/cadastro
- Pode criar conta com email+senha ou Google
- Após login, é redirecionado ao app com estado vazio

### UC2 — Registro de consumo
- Usuário logado vê a garrafa, os botões de consumo e o streak
- Cada gole é registrado no Supabase + localStorage (fallback)
- Meta diária, streak e histórico são calculados em tempo real

### UC3 — Sessões em múltiplos PCs
- Usuário bebe 2L no trabalho, salva automaticamente na nuvem
- Abre o app em casa, vê que já consumiu 2L (faltam 1L pra meta de 3L)
- Histórico de 30 dias sincronizado entre dispositivos

### UC4 — Lembretes
- App envia notificação quando usuário fica sem beber água no intervalo configurado
- Notificação funciona com a aba aberta (Service Worker futuramente)

### UC5 — Offline
- Se ficar sem internet, app continua funcionando com localStorage
- Ao voltar online, dados são sincronizados com o servidor

## Métricas de sucesso
- [ ] Deploy na Vercel funcionando
- [ ] Login com email e Google operacional
- [ ] Consumo registrado no Supabase
- [ ] Histórico sincronizado entre abas/dispositivos
- [ ] Lembretes disparando corretamente
- [ ] Streak e estatísticas mantidos
