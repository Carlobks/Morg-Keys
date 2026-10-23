# 0004 — Um só pack do Zebar com subpastas

- **Estado:** aceite (2026-10-22)
- **Contexto:** havia 3 packs, cada um com uma cópia igual do `vendor/zebar-3.3.1.mjs`, porque o Zebar só serve
  ficheiros de dentro da pasta do pack (código do Zebar 3.3.1, `asset_server.rs`).
- **Decisão:** um pack `omarchy-catppuccin` com `guia\`, `arranque\` e `painel\`, e um só `vendor\`. A
  alternativa "uma cópia no repositório, o instalador distribui" (menos risco) foi recusada pelo utilizador.
- **Consequências:** títulos das janelas `Zebar - omarchy-catppuccin / <widget>` (A23); a junction
  `Documentos\Guia de Atalhos` aponta para `guia\`. Pesquisa: `docs/pesquisa/zebar-webview2.md`.
