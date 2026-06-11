# 💧 Contador de Água

App desktop para Windows que te lembra de beber água durante o dia — ideal pra quem passa horas na frente do PC e esquece de se hidratar.

![Tela principal](docs/screenshot-main.png)
![Streak de dias](docs/screenshot-main2.png)
![Histórico 30 dias](docs/screenshot-history.png)

## ✨ Funcionalidades

- **Garrafa animada** que enche conforme você registra o consumo
- **Lembretes nativos do Windows** em intervalos configuráveis (padrão: 30 min)
- **Histórico de 30 dias** com gráfico de barras (meta atingida, parcial, sem registro)
- **Sequência de dias** (streak) e melhor recorde pessoal
- **Minimiza para a bandeja** — fica rodando em segundo plano sem ocupar a barra de tarefas
- **Reset automático à meia-noite** — mesmo se o PC estiver ligado, o dia vira sozinho
- **Detecta dias perdidos** — se você não abriu o app por alguns dias, eles aparecem como zero no histórico
- **Tema claro / escuro**
- **Meta e intervalo de lembrete configuráveis**

## 📥 Download

Baixe o instalador mais recente na página de [Releases](../../releases):

| Arquivo | Descrição |
|---|---|
| `Contador de Água Setup x.x.x.exe` | Instalador — instala o app, cria atalho na área de trabalho e no menu iniciar |
| `Contador de Água x.x.x.exe` | Portable — roda direto, sem precisar instalar |

## 🚀 Como usar

1. Baixe e instale o app
2. Ao abrir, a garrafa começa vazia
3. Clique nos botões (**Copo**, **Gole**, **Dose**, **Garrafa**) ou digite a quantidade manualmente
4. O app fica na bandeja do sistema — fechar a janela não encerra o programa
5. Você receberá notificações quando esquecer de beber água
6. Clique no ícone 📊 no cabeçalho para ver o histórico dos últimos 30 dias

## ⚙️ Configurações

Clique no ícone de engrenagem (⚙️) para ajustar:

- **Meta diária** em ml (padrão: 2000 ml)
- **Intervalo de lembrete** em minutos (padrão: 30 min)

## 🛠️ Tecnologias

| Camada | Stack |
|---|---|
| Interface | Next.js 16 + React 19 + Tailwind CSS v4 |
| Desktop | Electron 36 |
| Ícones | Lucide React |
| Empacotamento | electron-builder (NSIS + Portable) |
| Persistência | JSON em AppData (via IPC bridge) |

## 🧑‍💻 Desenvolvimento local

```bash
# Instalar dependências
cd app-de-agua
pnpm install

# Rodar em modo dev (Next.js + Electron juntos)
pnpm electron:dev

# Gerar instalador Windows
pnpm electron:build
# → dist-electron/Contador de Água Setup 1.0.0.exe
```

**Requisitos:** Node.js 18+, pnpm 11+

## 📁 Estrutura do projeto

```
contador-agua/
├── app-de-agua/          # Frontend Next.js + Electron
│   ├── app/              # Pages (Next.js App Router)
│   ├── components/       # water-tracker, history-modal, water-bottle, streak-card...
│   ├── hooks/            # useWaterState.ts — lógica central + persistência
│   ├── electron/
│   │   ├── main.js       # Processo principal: janela, tray, timer, IPC
│   │   └── preload.js    # Bridge contextBridge → renderer
│   └── assets/           # icon.ico, alert.wav, success.wav
├── assets/               # Ícone fonte (.png → .ico)
├── app.py                # Versão Python (customtkinter) — legado
├── state.py              # Estado e persistência Python
└── history_dialog.py     # Modal de histórico Python
```

## 📝 Licença

MIT © [Adrian Souza](https://github.com/Adrian9742) — use, modifique e distribua à vontade.
