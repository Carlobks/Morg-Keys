# Regras e barreiras

Cada regra do `CLAUDE.md` e o que a obriga. Texto é conselho; o que tem de ser cumprido vira hook, teste ou CI
(Morg Laws, skill `escrevendo-regras-de-agente` §6). O `tests/test_regras.py` exige que cada título do `CLAUDE.md`
tenha aqui uma linha, e que cada caminho citado exista.

**Tipos de barreira:**
- **hook:** um hook do Claude Code em `.claude/hooks/` (trava o agente; um commit feito à mão não passa por ele);
- **git:** um hook do git em `.githooks/` (vale para o agente e para quem commita à mão);
- **teste:** um teste do `scripts/testar.ps1`, que corre em cada commit;
- **permissão:** uma regra em `.claude/settings.json`;
- **CI:** uma verificação no GitHub, em `.github/workflows/ci.yml` (regras em `tests/test_ci.py`); vale também
  para o commit feito à mão sem os hooks do git;
- **texto:** só a regra escrita (não há máquina que a decida; o motivo está ao lado);
- **por fazer:** a barreira tem fase marcada no plano `docs/morg-laws/plano-01.md`.

| Regra | Barreira | Onde |
|---|---|---|
| NUNCA ARRANCAR O AMBIENTE | hook + teste | `.claude/hooks/bloquear_arranque.py`, `tests/test_hooks.py` |
| PLANO ANTES DE MEXER | teste; texto | `tests/test_docs_indices.py`: os planos em `docs/` têm "Fora do escopo" e a prova; o "sim" do dono é texto |
| DECISÃO É DO DONO | texto | nenhuma máquina sabe o que é uma decisão do dono; skill `pondo-o-plano-a-prova` |
| COMMIT SEM PEDIDO, PUSH COM O SIM | hook | `.claude/hooks/perguntar_antes.py` pergunta antes de cada `git push` |
| OS HOOKS SÃO A REDE | hook + teste + CI | `.claude/hooks/guarda_do_git.py` (`--no-verify`, `core.hooksPath`), `tests/test_hooks.py` (`onFailure: block`); quem saltar os hooks à mão é apanhado no `.github/workflows/ci.yml` |
| NÃO PIORAR | teste | catracas: `tests/test_ficheiros_texto.py` (linhas), `tests/test_tamanho_das_funcoes.py`, `tests/test_alarmes.py`, `tests/linha-de-base-pssa.txt` no `scripts/testar.ps1` |
| SEM SILENCIAR ALARME | teste | `tests/test_alarmes.py` (motivo, contagem, só regras ligadas), `RUF100` no `ruff.toml`; regras desligadas do Biome na ADR 0008 |
| BUG TRAZ TESTE | git | `.githooks/commit-msg` → `scripts/portoes/mensagem_commit.py` (fix sem `tests/` exige `Sem-teste:`) |
| PROVAR MEDINDO | git; texto | `.githooks/pre-commit` corre os testes; dizer o que não se verificou é texto |
| NOMES PESQUISÁVEIS | teste; texto | `tests/test_nomes.py` (nenhum ficheiro ou pasta com nome genérico solto); os nomes dentro do código são juízo da revisão |
| TEXTO VIRA BARREIRA | teste | `tests/test_regras.py` (este mapa) |
| SEM DADOS REAIS | teste + git | `tests/test_dados_pessoais.py`; `.githooks/pre-commit` e `commit-msg` com a lista negra |
| SEM SEGREDOS | permissão + hook + git + teste + CI | `.claude/settings.json` (deny e `disableBypassPermissionsMode`), `.claude/hooks/bloquear_segredos.py` (ler segredos e downloads numa shell), `.githooks/pre-push` (gitleaks), `tests/test_permissoes.py`; gitleaks em todo o histórico no `.github/workflows/ci.yml` |
| SÓ O PRÓPRIO TRABALHO | hook | `.claude/hooks/guarda_do_git.py` (`add -A`, `.`, `commit -a`, commit sem caminhos) |
| UM SÓ COMANDO | git + CI | `.githooks/pre-commit` e `.github/workflows/ci.yml` correm `scripts/testar.ps1` |
| COBERTURA 100 % | teste | `scripts/testar.ps1` (`--fail-under=100` no pack, portões, hooks e statusLine; `node --test` a 100 %, Pester a 100 %); a lógica das páginas em `.mjs` e os `<script>` em linha com catraca: `tests/paginas-em-linha.test.mjs` |
| NUNCA ENFRAQUECER UM TESTE | teste; texto | `tests/test_estragos_minimo.py` (os estragos não encolhem); afrouxar uma asserção é juízo da revisão |
| FICHEIROS PEQUENOS | hook + teste | `.claude/hooks/limite_de_linhas.py`, `tests/test_ficheiros_texto.py`; 35 linhas por função: `tests/test_tamanho_das_funcoes.py`, `biome.jsonc`, `tests/paginas-em-linha.test.mjs`, `scripts/testar.ps1` |
| PYTHON ISOLADO | teste | `tests/test_ponto_de_entrada.py` corre o ajudante com `-I` noutra pasta |
| CODIFICAÇÃO | teste | `tests/test_ficheiros_texto.py` (BOM em cada `.ps1`); o `$funcao` da A37 é texto |
| FINS DE LINHA | teste | `.gitattributes` (CRLF só nos `.ps1`, `.psm1`, `.cmd` e `.bat`), `tests/test_fins_de_linha.py` (índice e disco conforme a extensão) |
| SUBSTITUIÇÕES COM CONTAGEM | texto | o `assert` vive em cada script de substituição |
| ESTRUTURA À PARTE | texto | é juízo de quem commita; a revisão do diff apanha |
| COMENTÁRIOS FICAM | texto | é juízo de quem refatora; a revisão do diff apanha |
| DECISÕES EM ADR | teste | `tests/test_docs_indices.py`: números seguidos e cada ADR na tabela do índice |
| ARMADILHAS REGISTADAS | teste | `tests/test_docs_indices.py`: A1…An seguidas, cada uma com a regra |
| ÍNDICE DOS DOCS | teste | `tests/test_docs_indices.py`: cada `.md` e pasta de `docs/` no índice |
| PESQUISA ANTES DE IMPLEMENTAR | texto; teste | pesquisar antes é texto; `tests/test_docs_indices.py` exige cada pesquisa no índice, com data |
| FORMATO DOS COMMITS | git | `.githooks/commit-msg` → `scripts/portoes/mensagem_commit.py` |
| CHANGELOG POR FRAGMENTO | git + teste | `.githooks/commit-msg` → `scripts/portoes/mensagem_commit.py`; `tests/test_changelog.py` confere cada fragmento |
| VERSÃO SÓ NO LANÇAMENTO | git + teste | `.githooks/commit-msg` → `scripts/portoes/versao_lancada.py` (o `VERSION` só muda com a secção nova; uma versão lançada não muda sem `Changelog-corrigido:`); `tests/test_versao.py` (o `VERSION` igual à versão mais recente, as versões só descem, cada tag `v*` com secção) |
| REPOSITÓRIO PARA O PC | texto | o script que copiava do PC para o repositório foi retirado: só há um sentido |
