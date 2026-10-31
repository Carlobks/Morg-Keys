# 0008 — Duas regras do Biome desligadas no projeto inteiro

- **Estado:** aceite (2026-10-31, ML9 do plano Morg Laws)
- **Contexto:** a regra SEM SILENCIAR ALARME do `CLAUDE.md` (e o Morg Laws) pede o motivo escrito de cada regra
  desligada: uma regra desligada para calar o passivo antigo deixa passar os erros novos. Em `biome.jsonc` há duas
  desligadas desde a fase 2d da experiência 0001, com o motivo só num comentário.
- **Decisão:** ficam desligadas, porque corrigi-las muda a cascata do CSS e portanto o aspeto, que as impressões
  digitais da fase 2c provaram estar certo:
  - `style/noDescendingSpecificity`: nas folhas do pack a ordem é de propósito (ex.: `body.sending .key` depois de
    `.key.has`); reordenar muda qual regra ganha;
  - `complexity/noImportantStyles`: `.hidden { display: none !important }` e `body.busy * { cursor: progress
    !important }` têm de ganhar a qualquer outra regra.
- **Consequências:** o `tests/test_alarmes.py` não conta regras desligadas no `biome.jsonc`; uma terceira regra
  desligada pede uma ADR nova. Revê-se quando a ML11b passar a lógica das páginas para `.mjs` e houver testes do
  aspeto que provem uma reordenação.
