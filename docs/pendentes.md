# Pendentes (por ordem)

Trabalho combinado com o utilizador e ainda não feito. Quando um item começa, ganha plano próprio (ou ADR);
quando acaba, sai daqui.

1. **Experiência 0001 — cobertura A contra C** (em curso): `experiencias/0001-cobertura-a-vs-c.md`.

A fazer agora, no `exp/a`, antes da fase 4 da experiência (pedido de 2026-10-24). Ordem: 2, 3 (as correções
pequenas e a bateria na barra já estão feitas).

2. **Quota do Claude Code na barra** (pedido de 2026-10-23): melhorar a ligação ou, em alternativa, dar
   opção de a ocultar. Hoje o `claude_usage.py` só lê `~/.claude/rate_limits.json`, que o
   `~/.claude/statusline.py` escreve quando uma sessão do Claude Code **no terminal** recebe `rate_limits`;
   a aplicação de ambiente de trabalho não corre a statusLine, por isso os valores ficam desatualizados
   (a barra mostra a idade). Investigar uma fonte mais direta; se não houver, opção de ocultar.
   **Pedido de 2026-10-23:** ver se dá para usar o projeto de código aberto do Fabio Akita
   https://github.com/akitaonrails/ai-usagebar no Morg Keys, ou aprender como ele obtém o uso do Claude e
   replicar. Verificar: licença (compatível com GPL-3.0?), de onde lê os dados (API oficial, ficheiros locais
   do Claude Code, sessão do claude.ai), se corre no Windows, dependências, e como encaixaria na barra do Zebar
   (o `claude_usage.py` só pode usar a biblioteca padrão do Python).
3. **Fundo à vista no arranque** (9,3 s = 3,3 s até a tarefa criar o `pythonw` + 5,8 s do Python a frio):
   decidir fundo preto e/ou cortina sem Python.
