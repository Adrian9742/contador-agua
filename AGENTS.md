# AGENTS.md — Contador de Água

> **Documento principal do repositório.** Qualquer agente de IA DEVE ler este arquivo antes de tocar em qualquer coisa.

## 1. O que é este projeto

**Contador de Água** — app desktop de contagem diária de água com animação, streak de dias e modo dark/light.

## 2. Stack

- **Python + CustomTkinter** (aplicação desktop original)
- Builds Electron gerados (`app-de-agua/dist-electron/`, `desktop/dist-electron/`)

## 3. Estrutura de pastas

```
contador-agua/
├── app-de-agua/                 # Build Electron (dist-electron/)
├── desktop/                     # Build desktop (dist-electron/ + node_modules/)
└── build/                       # Artefatos de build
```

> ⚠️ **Nota:** este repositório contém principalmente **artefatos de build** (`.exe`, `app.asar`, `node_modules`). O código-fonte principal não está versionado aqui.

## 4. Regras de ouro

- **PT-BR** em tudo.
- **NUNCA fabricar dados** — output literal de comandos.
- **NUNCA encerrar sem resumo** — explicar o que foi feito + tabela resumo.
- **Não commitar `node_modules/` nem artefatos de build desnecessários** — manter o repo limpo.
- **Workflow PR** — branch separada, PR para revisão, nunca push na main.

## 5. O que NÃO fazer

- ❌ Commitar `node_modules/`
- ❌ Fabricar resultados de teste
- ❌ Push direto na main

## 6. Documentação relacionada

- `README.md` — visão geral