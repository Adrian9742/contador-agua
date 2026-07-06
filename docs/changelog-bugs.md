# 🐞 Registro de Bugs e Erros

> Log de todos os problemas encontrados durante o desenvolvimento,
> com causa raiz, solução e prevenção.

## Formato

```
## [YYYY-MM-DD] Título do bug
- **Onde:** arquivo/pasta, linha
- **O que:** descrição do comportamento inesperado
- **Causa:** por que aconteceu
- **Solução:** o que foi feito pra corrigir
- **Prevenção:** como evitar que aconteça de novo
```

---

## [2025-07-06] Lint falso-positivo no @supabase/ssr
- **Onde:** `node_modules/@supabase/ssr/dist/main/createBrowserClient.d.ts`
- **O que:** Linter apontou erro de tipo `SchemaName does not satisfy constraint` no código do pacote instalado
- **Causa:** Incompatibilidade de versão entre `@supabase/ssr@0.6.1` e `@supabase/supabase-js@2.110.0` nos tipos internos
- **Solução:** Nenhuma necessária — `tsconfig.json` tem `skipLibCheck: true` e `ignoreBuildErrors: true`, o build compila sem erros
- **Prevenção:** Se um dia remover `ignoreBuildErrors`, atualizar `@supabase/ssr` pra versão mais recente
