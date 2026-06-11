# Contador de Água — Contexto para o Claude Code

## O que é o projeto

App desktop Windows que lembra o usuário de beber água durante o dia.
Criado porque horas longas no PC fazem esquecer a hidratação.

## Estrutura de pastas

```
contador-agua/
├── desktop/          # App atual — Electron 36 + Next.js 16 + React 19 + Tailwind v4
├── legacy-python/    # Versão antiga em customtkinter — SOMENTE LEITURA, nunca editar
├── docs/             # Screenshots do README — não mexer
└── README.md
```

## Comandos

```bash
cd desktop
pnpm install          # instala dependências
pnpm electron:dev     # dev: Next.js (localhost:3000) + Electron juntos
pnpm electron:build   # gera dist-electron/Contador de Água Setup x.x.x.exe
```

## Arquitetura do desktop/

```
desktop/
├── lib/              # lógica pura, sem React, sem Electron
│   ├── constants.ts  # volumes, metas padrão, chaves de storage
│   ├── types.ts      # tipos compartilhados (AppState, DayEntry, etc.)
│   ├── dates.ts      # todayISO, applyDayRollover, trimHistory
│   ├── stats.ts      # computeStreak, computeLast7Days
│   └── storage.ts    # abstração localStorage ↔ Electron IPC
├── hooks/
│   └── useWaterState.ts   # estado React fino — chama lib/
├── components/
│   ├── water-tracker.tsx  # orquestrador principal
│   ├── bottle/            # garrafa animada
│   ├── controls/          # botões de consumo + entrada manual
│   ├── history/           # modal + gráfico SVG + stats 30 dias
│   ├── settings/          # modal de meta/intervalo/tema
│   └── streak-card.tsx    # card de sequência de dias
└── electron/
    ├── main.js       # bootstrap: app.whenReady, instância única
    ├── window.js     # criação e comportamento da BrowserWindow
    ├── tray.js       # ícone, menu e clique na bandeja
    ├── reminders.js  # timer do lembrete + notificação nativa + meia-noite
    ├── store.js      # leitura/escrita do JSON em AppData
    ├── ipc.js        # registro centralizado dos ipcMain.handle
    └── preload.js    # bridge window.electronAPI (NÃO alterar a API pública)
```

## Comportamentos críticos — NUNCA podem quebrar

1. **Lembrete dispara mesmo com a janela minimizada na bandeja**
   - O timer vive em `electron/reminders.js` (processo principal), não no renderer
2. **Fechar a janela minimiza para a bandeja — não encerra o app**
   - `win.on('close')` previne o fechamento; `app.isQuitting` controla o sair real
3. **Reset automático à meia-noite**
   - `scheduleMidnightReset()` em `reminders.js` envia IPC `midnight-reset` ao renderer
4. **Dias com PC desligado aparecem zerados no histórico**
   - `applyDayRollover()` em `lib/dates.ts` detecta gaps entre `lastDate` e hoje
5. **Histórico de 30 dias e stats (streak, recorde, média)**
   - Calculados em `lib/stats.ts` sobre o `dailyHistory` persistido

## Canais IPC (preload.js — não renomear)

| Canal | Direção | O que faz |
|---|---|---|
| `load-state` | renderer → main | carrega JSON do AppData |
| `save-state` | renderer → main | salva JSON + atualiza vars do timer |
| `notify-goal` | renderer → main | dispara notificação nativa de meta atingida |
| `reminder` | main → renderer | sinaliza lembrete disparado |
| `midnight-reset` | main → renderer | sinaliza virada de dia |

## Convenções

- TypeScript no frontend (`desktop/app`, `components`, `hooks`, `lib`)
- JavaScript no Electron (`desktop/electron/*.js`) — sem TypeScript aqui
- Commits em português
- Não adicionar dependências sem perguntar
- Não alterar `legacy-python/` por nenhum motivo
- Não alterar a API pública de `window.electronAPI` sem avisar
