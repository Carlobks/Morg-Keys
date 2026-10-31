# 2.ª verificação contra as regras gerais do Morg Laws — 2026-10-31

Leitura independente, numa sessão nova, do ramo `exp/a` em `26656de`. As contagens abaixo foram fechadas **antes**
de ler a 1.ª verificação, o plano 01, o handoff e o corpo dos commits "ML" (só se viram os títulos, no `git log`).
A comparação com a 1.ª está no fim, escrita depois.

**Fontes das regras:** `AGENTS.md` do Morg Laws (núcleo e "Nunca"), as 7 skills copiadas em `.claude/skills/`
(iguais às do Morg Laws: `diff -rq` sem diferenças nas 7) e os itens de `biblia-akita/nao-faca.md` marcados como
**máquina** que se aplicam a um projeto de código. Não se aplicam: `sql-postgres`, `supabase`, `nextjs-react`, o
banco de produção e as categorias de segurança de Supabase e Next.js.

**Veredictos:** cumprida · em parte (falta uma parte, ou só existe em texto quando podia ter máquina) · falha ·
por validar (não se mede a partir do repositório) · não se aplica.

## Contagens

| Veredicto | Regras |
|---|---|
| Cumprida | 29 |
| Em parte | 11 |
| Falha | 1 |
| Por validar | 3 |
| Não se aplica | 2 |
| **Total** | **46** (44 aplicáveis) |

Contei de novo a tabela abaixo antes de gravar: 29 + 11 + 1 + 3 + 2 = 46.

## Provas corridas

| Comando | Saída |
|---|---|
| `powershell -NoProfile -File scripts/testar.ps1` (sozinho) | `Ran 424 tests` · `OK`; cobertura Python `TOTAL 2269 0 770 0 100%`; `node --test`: `tests 79` · `fail 0`; Pester `Passed: 72, Failed: 0`; `instalar.ps1` 469/469 e `desinstalar.ps1` 109/109 fora das funções excluídas; ruff `All checks passed!`; Biome `Checked 35 files`; `OK: todos os testes passaram.` · saída 0 |
| `C:\Windows\py.exe -I scripts/estragos.py` | `80/80 apanhados` · saída 0; o `git status` voltou limpo no fim |
| `gitleaks git --redact --no-banner .` (8.30.1, pasta do winget) | `92 commits scanned` · `no leaks found` · saída 0 |
| `npm audit --json` | `{'info': 0, 'low': 0, 'moderate': 0, 'high': 0, 'critical': 0, 'total': 0}` |
| `gh run list --limit 5` | último CI: `success`, `ci/teste-ml14`, 2026-10-31 18:36 (Lisboa) |
| Sondas aos hooks do agente (JSON de exemplo no stdin de cada `.claude/hooks/*.py`) | ver N4, V3, O2 |
| Contagens por script (só leitura) sobre os 222 ficheiros versionados e os 94 commits | ver cada linha |

**Cuidado que esta verificação descobriu na própria pele:** a 1.ª corrida do `testar.ps1` foi feita ao mesmo tempo
que os estragos e deu 2 testes vermelhos e a cobertura a 99 %: os estragos trocam o texto dos ficheiros no disco
enquanto correm (o `git status` mostrava `M …/morg_arranjo.py`). Não era um bug do código; é o achado M4.

## Tabela das regras

### Núcleo (`AGENTS.md`)

| # | Regra | Veredicto | Prova | O que falta |
|---|---|---|---|---|
| N1 | Plano antes de mexer | cumprida | `CLAUDE.md:15`; `tests/test_docs_indices.py` exige "Fora do escopo" e a prova nos planos | o "sim" do dono não tem máquina possível |
| N2 | Decisão a meio vai ao dono | por validar | `CLAUDE.md:17`; é comportamento das sessões, não fica no repositório | — |
| N3 | Commitar sem pedido; push **e PR** com o "sim" | em parte | sonda: `git push` → `permissionDecision: ask` (`perguntar_antes.py:23`); `settings.json` `ask` com `git push` | `gh pr create` não está no hook nem no `ask` (B2) |
| N4 | Os hooks são a rede | cumprida | `git config core.hooksPath` = `.githooks`; sondas: `--no-verify` e `core.hooksPath /dev/null` → exit 2; CI corre o mesmo `testar.ps1` | — |
| N5 | O que já viola não piora | cumprida | catracas: `tests/test_tamanho_das_funcoes.py:16` (4 funções antigas), `tests/linha-de-base-pssa.txt` (6 regras), `tests/test_alarmes.py`, `tests/test_ficheiros_texto.py`; 1 ficheiro > 500 linhas (`LICENSE`, 675) | — |
| N6 | Sem silenciar alarme | cumprida | 6 alarmes no código (5 `noqa`/`pragma` + 1 comentário no `testar.ps1`), **6 de 6 com motivo** na linha; `RUF100` no `ruff.toml` | — |
| N7 | Bug corrigido traz o teste | cumprida | `scripts/portoes/mensagem_commit.py` exige `Sem-teste:`; 5 commits `fix`, 0 sem teste e sem `Sem-teste` | — |
| N8 | Provar medindo | cumprida | `pre-commit` e CI correm o `testar.ps1`: 424 + 79 + 72 testes verdes, cobertura 100 % (ver "Provas corridas") | dizer o que não se verificou é texto, sem máquina possível |
| N9 | Nomes únicos e pesquisáveis | em parte | `tests/test_nomes.py`: 0 ficheiros ou pastas com nome genérico | identificadores genéricos sem máquina: `const helper` (`bar.html`), `const data` (`painel/apps-logica.mjs`) (B8) |
| N10 | Texto vira barreira | em parte | `tests/test_regras.py` liga cada título a uma linha de `docs/regras-e-barreiras.md` | mapa desatualizado (FINS DE LINHA "por fazer" já tem `.gitattributes` e `tests/test_fins_de_linha.py`) (B4); buracos das sondas (M2, M3, B2, B3) |

### Nunca (`AGENTS.md`)

| # | Regra | Veredicto | Prova | O que falta |
|---|---|---|---|---|
| V1 | Escrever no banco de produção | não se aplica | o projeto não tem banco | — |
| V2 | Dados reais em testes, exemplos ou commits | em parte | árvore: 0 ocorrências do utilizador do Windows e do e-mail pessoal; `tests/test_dados_pessoais.py`; lista negra no `pre-commit` e `commit-msg`; 94 de 94 commits com e-mail noreply | `git log --all -S<utilizador do Windows>` → **4 commits**, também em `origin/main` (já publicado) (M1); "Joao Silva" no `Tutorial.html:132` em vez de "Ana" (B9) |
| V3 | Ler `.env` e segredos; `curl \| sh`; mudar as próprias permissões | em parte | `settings.json` `deny` em `Read(**/.env)`…; sonda: editar `.claude/settings.json` → `ask` | sondas: `cat .env` e `curl https://x \| sh` passam pelos 3 hooks sem travão nem pergunta (M2, M3) |
| V4 | Commitar trabalho de outra sessão | cumprida | sondas: `git add -A`, `git add .`, `git commit -a`, `git commit -F m` (sem caminhos) → exit 2 | — |

### Commits (`git-e-commits`)

| # | Regra | Veredicto | Prova | O que falta |
|---|---|---|---|---|
| G1 | Mensagem: `tipo(área): …` ≤ 72, corpo com o porquê | cumprida | `mensagem_commit.py`; desde o 1.º commit com o portão (`84a9bb6`), 39 de 39 títulos no formato e ≤ 72; os 54 fora do formato e os 35 longos são todos anteriores | — |
| G2 | Changelog por fragmento | cumprida | `mensagem_commit.py` (`INSTALADO`, `Sem-changelog`); 10 fragmentos em `changelog.d/`; `tests/test_changelog.py` | — |
| G3 | Bugs encontrados e não corrigidos ficam registados | cumprida | `docs/pendentes.md`, `docs/armadilhas.md` (A1…A46, numeração testada) | — |
| G4 | Nada de dados reais na mensagem | cumprida | `commit-msg` passa a mensagem pela lista negra; 0 e-mails pessoais nos 94 commits | — |

### Testes (`testes-e-provas`)

| # | Regra | Veredicto | Prova | O que falta |
|---|---|---|---|---|
| T1 | O teste falha quando o código está errado (mutação, Akita #25) | cumprida | `80/80 apanhados`; `scripts/estragos.py`; `tests/test_estragos_minimo.py` (os estragos não encolhem); CI semanal (`ci.yml`, job `estragos`) | — |
| T2 | Testes sem rede | cumprida | os 2 testes com `socket` abrem um servidor local (`tests/test_bat_tray.py:85`, `tests/test_arranque_casos.py:125`); CI verde | — |
| T3 | Mudar um teste existente pede o porquê (Akita #38, aviso no hook) | em parte | `tests/test_estragos_minimo.py` trava o encolher dos estragos | nenhum hook avisa quando um commit altera um teste existente (B10) |

### Regras de agente (`escrevendo-regras-de-agente`)

| # | Regra | Veredicto | Prova | O que falta |
|---|---|---|---|---|
| E1 | Ficheiro lido sempre curto, com teste | cumprida | `CLAUDE.md`: 94 linhas, a maior com 128 caracteres; `tests/test_regras.py:19` (100 × 160) | — |
| E2 | Forma curta: título único, regra, **motivo** | em parte | 31 regras no `CLAUDE.md`, **12 com motivo** (`· *…*`) | 19 sem motivo escrito (algumas só citam a armadilha) (B6) |
| E3 | Skills de terceiros lidas e fixadas | cumprida | `skills-lock.json` com hash; as 7 cópias iguais ao Morg Laws | — |
| E4 | Fontes e pesquisa com data e estrutura | cumprida | 12 pesquisas em `docs/pesquisa/`, cada uma com data no índice (testado) | — |

### Segurança (`auditoria-de-seguranca`)

| # | Regra | Veredicto | Prova | O que falta |
|---|---|---|---|---|
| S1 | Segredos travados antes do push | cumprida | `.githooks/pre-push` → `antes_do_push.py` (sem gitleaks não sai); gitleaks no CI com hash conferido; corrida local sem achados | — |
| S2 | Bibliotecas com linha de base que só encolhe | cumprida | `.seguranca/audit-linha-de-base.txt` (vazia, 0 avisos); `npm audit` 0; CI com `npm ci --ignore-scripts` | — |
| S3 | Entrada não confiável validada | cumprida | `zpack.json`: cada `argsRegex` ancorado com `^…$` e só os subcomandos que a página precisa (A9) | — |
| S4 | O que se descarrega é conferido | cumprida | `scripts/instalar.ps1:52-61,142-147`: SHA-256 no GlazeWM e no Python, assinatura `O=Microsoft Corporation` exata no VC++ | — |

Medida da skill (achados e cobertura), só nas categorias que existem aqui: **Achados:** 0 críticos · 0 altos ·
3 médios (M1–M3) · ver lista. **Cobertura:** 4 de 4 categorias aplicáveis com prova (segredos, entrada não
confiável, dados pessoais em logs — `uncloak.ps1:71` só regista o nome da app —, dependências); as 8 de Supabase e
Next.js não se aplicam.

### Sessões (`orquestrando-sessoes`)

| # | Regra | Veredicto | Prova | O que falta |
|---|---|---|---|---|
| O1 | Handoff por assunto | cumprida | `.context/HANDOFF-morg-laws.md` (nome com o assunto; o conteúdo não foi lido antes das contagens) | — |
| O2 | Nunca `git stash` | em parte | texto na skill | sonda: `git stash` passa pela guarda (B3) |
| O3 | Várias sessões na mesma pasta sem se atropelar | em parte | commit por caminho travado (V4) | os estragos escrevem nos ficheiros do disco partilhado durante ~10 min (M4) |
| O4 | Leitura independente para o que é de risco | cumprida | 1.ª e 2.ª verificação em sessões novas | — |

### Telas (`desenhando-telas`)

| # | Regra | Veredicto | Prova | O que falta |
|---|---|---|---|---|
| D1 | Contraste ≥ 4,5:1 | cumprida | `tests/test_telas.py:134` (cada texto em cada fundo) | — |
| D2 | Movimento: `prefers-reduced-motion`, ≤ 700 ms | cumprida | as 5 folhas com movimento têm o bloco (`tests/test_telas.py:39`); transições ≤ 700 ms; acima disso só atrasos e laços de estado (vapor 2,7 s, roda 0,8 s em `arranque/splash.html:51,86`) | o teto de 700 ms não tem teste |
| D3 | `tabular-nums` em números | cumprida | `tests/test_telas.py:169` | — |
| D4 | Tamanhos em `rem` | não se aplica | ADR 0009 (decisão escrita: no WebView2 do Zebar `1rem` é sempre 16 px); 61 `font-size` em px, 0 em rem | rever se o teste real mostrar outra coisa (a ADR já o diz) |
| D5 | Superfícies sólidas, sem `z-index` solto | cumprida | 0 fundos `rgba(`; 0 `z-index` nas páginas | — |
| D6 | Ícone de ação com rótulo visível; sem emoji na interface | em parte | — | botões `✕` só com `title` (`guia/guia.html:16`, `painel/apps.html:18`, `painel/apps-logica.mjs:65,126`); `✓`/`✕` como sinais no texto (B7) |
| D7 | Alvos de toque medidos (≥ 24 px) | por validar | as páginas só correm dentro do Zebar e esta sessão não o pode arrancar (Regra n.º 1) | medir a caixa no teste real do dono |

### Itens "máquina" do livro do Akita

| # | Regra | Veredicto | Prova | O que falta |
|---|---|---|---|---|
| K1 | Permissões em três colunas (#76) | cumprida | `settings.json`: 7 `deny`, 15 `ask`, 5 `allow`; `tests/test_permissoes.py` | — |
| K2 | Instalar pacotes pede confirmação (#51) | cumprida | `ask` em `npm install/i/ci`, `npx`, `pip install`, `winget install`, `Install-Module`; `perguntar_antes.py` | — |
| K3 | Desligar o modo que salta as permissões (#50) | falha | `settings.json` não tem `disableBypassPermissionsMode` | uma linha nas definições do projeto (B1) |
| K4 | O push mostra os ficheiros de todos os commits (#78) | cumprida | `antes_do_push.py` (`verificar_commits`) | — |
| K5 | Registo do que se aprendeu no fim da sessão (#68) | em parte | handoff e armadilhas em texto | nenhum hook de fim de sessão (B10) |
| K6 | Backup externo da pasta de trabalho (#74, #75) | por validar | fora do repositório | perguntar ao dono |

## Achados por gravidade (para o dono decidir; nada foi corrigido)

**Alto:** nenhum.

**Médio**
- **M1 — Caminho pessoal no histórico já publicado.** A árvore está limpa, mas 4 commits (de 2026-10-23 e
  2026-10-24, em `origin/main`) ainda têm o nome do utilizador do Windows. Corrigir pede reescrever o histórico
  público (decisão do dono; muda os hashes) ou aceitar e registar como armadilha.
- **M2 — `cat .env` pelo terminal passa.** O `deny` só cobre a ferramenta Read; um `Bash(cat .env)` não passa por
  nenhum hook. Falta a mesma regra para Bash/PowerShell (no `guarda_do_git.py` ou num hook próprio).
- **M3 — `curl … | sh` corre sem pergunta.** Nenhum hook nem `ask` o apanha (Akita #81 pede confirmação).
- **M4 — Os estragos mexem no disco partilhado.** Durante ~10 min o `estragos.py` deixa um ficheiro do pack
  estragado no disco. Outra sessão que corra testes vê-os falhar (aconteceu nesta verificação) e uma que commite
  esse ficheiro por caminho pode levar o mutante (o `pre-commit` apanharia, mas só porque os testes falham).
  Correr os estragos numa cópia (`git worktree`) ou numa pasta temporária fecha isto.

**Baixo**
- **B1** — sem `disableBypassPermissionsMode` no `.claude/settings.json` (K3).
- **B2** — `gh pr create` sem pergunta (N3).
- **B3** — `git stash` sem travão (O2).
- **B4** — `docs/regras-e-barreiras.md` diz FINS DE LINHA "por fazer (ML8)", mas a barreira existe (N10).
- **B5** — `uncloak.ps1` sem BOM e com 32 bytes não ASCII (só em comentários e no texto C# embutido); regra
  CODIFICAÇÃO do projeto; está congelado na catraca do PSScriptAnalyzer (`PSUseBOMForUnicodeEncodedFile 1`), sem
  teste próprio.
- **B6** — 19 de 31 regras do `CLAUDE.md` sem motivo escrito (E2).
- **B7** — botões `✕` só com `title` (D6).
- **B8** — `const helper` em `bar.html` e `const data` em `painel/apps-logica.mjs` (N9).
- **B9** — "Joao Silva" no `Tutorial.html:132`; o nome fictício do projeto é "Ana".
- **B10** — sem aviso quando um commit altera um teste existente, e sem hook de fim de sessão (T3, K5).

## O que não se verificou

- O aspeto das páginas, os alvos de toque e a escala de 125 %: só no PC do dono, com o Zebar a correr.
- O comportamento das sessões (perguntar ao dono, o "sim" do plano): não fica no repositório.
- O CI do ramo `exp/a` com `26656de`: o último CI visto é o do ramo `ci/teste-ml14`.
- O conteúdo dos 4 commits do M1 foi contado, não lido linha a linha.

## Comparação com a 1.ª

Escrita depois do commit `3e85bd9`, que gravou as contagens acima sem ter lido a 1.ª verificação.

| | 1.ª (2026-10-30, 55 commits) | 2.ª (2026-10-31, 94 commits) |
|---|---|---|
| Regras aplicáveis | 41 | 44 (+ 2 que não se aplicam) |
| Cumpridas | 17 (41,5 %) | 29 (65,9 %) |
| Em parte | 11 | 11 |
| Falhas | 9 | 1 |
| Por validar | 4 | 3 |

As duas listas não são iguais (a 2.ª separa as regras das telas e conta à parte os itens "máquina" do livro), por
isso compara-se por assunto e não só pelo total.

**O que mudou para melhor (as 9 falhas da 1.ª):**
1. Portão do git: `.githooks/` com `pre-commit`, `commit-msg` e `pre-push`, ligado (`core.hooksPath`) — N4.
2. `pre-push` com gitleaks (falha fechado) e `npm audit` com linha de base — S1, S2.
3. CI no GitHub: `testar.ps1`, gitleaks em todo o histórico e estragos semanais — N4, N8, T1.
4. e 5. Nomes e caminhos pessoais tirados da árvore, com teste e lista negra — V2 (ver o que ficou, abaixo).
6. Correção sem teste: o `commit-msg` exige `Sem-teste:`; 0 casos desde o portão — N7.
7. Formato das mensagens: 39 de 39 commits desde o portão no formato e ≤ 72 — G1.
8. `deny` para `.env`, chaves e credenciais na ferramenta Read — V3 (ver o que ficou).
9. Changelog por fragmentos, exigido pelo `commit-msg` — G2.

**Dos "em parte" da 1.ª, passaram a cumpridos:** CLAUDE.md com as regras (94 linhas, testado), alarmes (todos com
motivo, só regras ligadas), cobertura 100 % real (statusline, hooks e lógica das páginas dentro), `onFailure:
block` nos hooks, catracas das funções e do PSScriptAnalyzer, fins de linha (`.gitattributes` explícito, 0 ficheiros
fora), handoff no repositório, permissões em três colunas, planos com "fora do escopo" e prova, movimento
(`prefers-reduced-motion`). Os `px` passaram a decisão escrita (ADR 0009). O `comum` foi renomeado.

**Dos "por validar" da 1.ª:** commit por caminho e "teste que falha" passaram a máquina (guarda do git; estragos
80/80); o contraste passou a teste. Ficam por validar os alvos de toque e o backup.

**O que piorou:** nada do que a 1.ª mediu voltou atrás. Uma diferença pequena: a 1.ª contou "0 menções a
`--no-verify`" nos commits; agora 1 corpo de commit (`af01506`) cita a opção, mas para descrever a guarda que a
trava, não para a usar.

**O que a 1.ª não viu e a 2.ª encontrou:** M1 (a limpeza dos dados pessoais ficou só na árvore; 4 commits já
publicados ainda têm o caminho pessoal), M2 (`cat .env` pelo terminal), M3 (`curl | sh`), M4 (estragos no disco
partilhado), B1 (modo que salta permissões), B2 (`gh pr create`), B3 (`git stash`), B4 (mapa das barreiras
desatualizado), B5 (`uncloak.ps1` sem BOM), B6 (regras sem motivo), B7 (botões `✕` só com `title`) e B9
("Joao Silva"). A 1.ª dava "push e PR" como cumprida; esta leitura é mais estrita e põe-na em parte por causa do
`gh pr create`.
