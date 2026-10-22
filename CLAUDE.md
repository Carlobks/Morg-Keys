# CLAUDE.md — Morg Keys

Antes de mudar qualquer coisa, ler `COMO-FOI-FEITO.md` (sobretudo §1, decisões fixas, e §8, armadilhas).

## Regra n.º 1: nunca arrancar o ambiente a partir daqui

Não correr, a partir deste terminal ou de qualquer agente:
- `glazewm.exe` / `zebar.exe` (nem `zebar startup` / `start-widget-preset`);
- `bar_helper.py boot`, `layout-restore`, `animacao next|<nome>` com o Zebar fechado.

Os processos lançados herdam `CLAUDECODE`, `CLAUDE_CODE_*` e `ANTHROPIC_BASE_URL` deste terminal, e o Claude
Code aberto depois pelos atalhos passa a cobrar pela API (armadilha A2). Para testar o arranque, pedir ao
utilizador que corra a tarefa agendada ou reinicie a sessão. Seguro daqui: `glazewm command …` (incl.
`wm-reload-config`), ler ficheiros e logs.
