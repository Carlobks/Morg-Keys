# Regras e barreiras

Cada regra do `CLAUDE.md` e o que a obriga. Texto é conselho; o que tem de ser cumprido vira hook, teste ou CI
(Morg Laws, skill `escrevendo-regras-de-agente` §6). O `tests/test_regras.py` exige que cada título do `CLAUDE.md`
tenha aqui uma linha, e que cada caminho citado exista.

**Tipos de barreira:**
- **hook:** um hook do Claude Code em `.claude/hooks/` (trava o agente; um commit feito à mão não passa por ele);
- **git:** um hook do git em `.githooks/` (vale para o agente e para quem commita à mão);
- **teste:** um teste do `scripts/testar.ps1`, que corre em cada commit;
- **permissão:** uma regra em `.claude/settings.json`;
- **CI:** uma verificação no GitHub (ainda por fazer, ML14);
- **texto:** só a regra escrita (não há máquina que a decida; o motivo está ao lado);
- **por fazer:** a barreira tem fase marcada no plano `docs/morg-laws/plano-01.md`.

| Regra | Barreira | Onde |
|---|---|---|
| NUNCA ARRANCAR O AMBIENTE | hook + teste | `.claude/hooks/bloquear_arranque.py`, `tests/test_hooks.py` |
| PLANO ANTES DE MEXER | por fazer (ML7) | teste das secções "Fora do escopo" e "Prova" nos planos copiados para docs/planos |
| DECISÃO É DO DONO | texto | nenhuma máquina sabe o que é uma decisão do dono; skill `pondo-o-plano-a-prova` |
| COMMIT SEM PEDIDO, PUSH COM O SIM | hook | `.claude/hooks/perguntar_antes.py` pergunta antes de cada `git push` |
| OS HOOKS SÃO A REDE | hook + teste; CI por fazer (ML14) | `.claude/hooks/guarda_do_git.py` (`--no-verify`, `core.hooksPath`), `tests/test_hooks.py` (`onFailure: block`) |
| NÃO PIORAR | teste; por fazer (ML9) | `tests/test_ficheiros_texto.py` (linhas por ficheiro); funções e PSScriptAnalyzer na ML9 |
| SEM SILENCIAR ALARME | por fazer (ML9) | `RUF100` e contagem de `noqa`/`pragma` com motivo |
| BUG TRAZ TESTE | git | `.githooks/commit-msg` → `scripts/portoes/mensagem_commit.py` (fix sem `tests/` exige `Sem-teste:`) |
| PROVAR MEDINDO | git; texto | `.githooks/pre-commit` corre os testes; dizer o que não se verificou é texto |
| NOMES PESQUISÁVEIS | por fazer (ML10) | teste dos nomes proibidos nos ficheiros |
| TEXTO VIRA BARREIRA | teste | `tests/test_regras.py` (este mapa) |
| SEM DADOS REAIS | teste + git | `tests/test_dados_pessoais.py`; `.githooks/pre-commit` e `commit-msg` com a lista negra |
| SEM SEGREDOS | permissão + git + teste | `.claude/settings.json` (deny), `.githooks/pre-push` (gitleaks), `tests/test_permissoes.py` |
| SÓ O PRÓPRIO TRABALHO | hook | `.claude/hooks/guarda_do_git.py` (`add -A`, `.`, `commit -a`, commit sem caminhos) |
| UM SÓ COMANDO | git | `.githooks/pre-commit` corre `scripts/testar.ps1` |
| COBERTURA 100 % | teste | `scripts/testar.ps1` (`--fail-under=100`, `node --test` a 100 %, Pester a 100 %) |
| NUNCA ENFRAQUECER UM TESTE | texto; por fazer (ML9) | `scripts/estragos.py` mostra se os testes apanham erros; catraca dos estragos na ML9 |
| FICHEIROS PEQUENOS | hook + teste; por fazer (ML9) | `.claude/hooks/limite_de_linhas.py`, `tests/test_ficheiros_texto.py`; 35 linhas por função na ML9 |
| PYTHON ISOLADO | teste | `tests/test_ponto_de_entrada.py` corre o ajudante com `-I` noutra pasta |
| CODIFICAÇÃO | por fazer (F4) | teste do BOM nos `.ps1` (F4 da auditoria) |
| FINS DE LINHA | por fazer (ML8) | `.gitattributes` explícito e teste |
| SUBSTITUIÇÕES COM CONTAGEM | texto | o `assert` vive em cada script de substituição |
| ESTRUTURA À PARTE | texto | é juízo de quem commita; a revisão do diff apanha |
| COMENTÁRIOS FICAM | texto | é juízo de quem refatora; a revisão do diff apanha |
| DECISÕES EM ADR | por fazer (ML7) | teste dos números únicos e da tabela do índice |
| ARMADILHAS REGISTADAS | por fazer (ML7) | teste da numeração A1…An |
| ÍNDICE DOS DOCS | por fazer (ML7) | teste: cada `.md` de `docs/` no índice |
| PESQUISA ANTES DE IMPLEMENTAR | texto; por fazer (ML7) | o índice de `docs/pesquisa/README.md` com data passa a ter teste |
| FORMATO DOS COMMITS | git | `.githooks/commit-msg` → `scripts/portoes/mensagem_commit.py` |
| REPOSITÓRIO PARA O PC | texto | o script que copiava do PC para o repositório foi retirado: só há um sentido |
