# Morg Keys: cumprir o Morg Laws a 100 % (plano 01, 2026-10-30)

> Cópia do plano aprovado (o original vive na aba Plano do Claude). Atualizada no fim de cada fase,
> no mesmo commit que fecha a fase.

## Contexto

A 1.ª verificação (`docs/morg-laws/verificacao-01-2026-10-30.md`, commit `84a9bb6`) deu 41 regras aplicáveis:
17 cumpridas, 11 em parte, 9 falhas e 4 por validar. Este plano:
- dá a cada acerto uma barreira, para continuarmos a acertar;
- põe as parciais a 100 %;
- corrige as falhas.

**Decisões do dono do projeto (2026-10-30):**
- as fases Morg Laws vêm **antes** da F1;
- commits no formato `tipo(área): …`, obrigados por um hook;
- changelog com fragmentos em `changelog.d/`;
- instalar só as 7 skills que servem;
- **sem `AGENTS.md`**: só usamos o Claude, por isso as regras vivem no `CLAUDE.md`.

**Regras de todas as fases:**
- primeiro um teste que falha (mostrar a corrida vermelha), depois a correção (corrida verde);
- `testar.ps1` verde a 100 %;
- 1 fase = 1 ou mais commits pequenos, por caminho, no `exp/a`;
- sem push;
- nada destrutivo sem OK;
- `get_usage` antes de cada fase: a 90 % não se começa nada grande, a 95 % para-se com uma nota A-RETOMAR;
- os testes de hooks e de push correm num **clone descartável no scratchpad**, nunca neste repositório.

## Fora do escopo

- As fases F1–F7 da auditoria (só saem de lá os itens marcados "→ ML"), a experiência 0001, os jogos em ecrã
  inteiro e a A38.
- O push para o GitHub, até à ML15 e com o OK do dono.
- Reescrever o histórico já publicado (o nome antigo, o `17ce46f`, os títulos longos ficam como exceção).
- Mexer no PC instalado (`~\.glzr`, tarefas, registo): tudo se prova no repositório e num clone descartável.

**Efeito no plano da auditoria (F1–F7):** saem da F4 o `CLAUDE.md`, as 35 linhas, a cobertura do `statusline.py` e
dos hooks, o `onFailure` e os `noqa`; saem da F5 os fins de linha e os caminhos pessoais; sai da F6 a lógica das
páginas em `.mjs`. Ficam lá, marcados "→ plano Morg Laws".

## A. Os acertos: estão escritos? Há uma barreira que obrigue?

| Acerto | Onde está escrito hoje | Barreira hoje | Barreira nova (fase) |
|---|---|---|---|
| Plano antes de mexer | CLAUDE.md global, proposta | nenhuma | Cópia do plano em `docs/planos/` + teste que exige "Fora do escopo" e "Prova" (ML7) |
| Decisão vai ao dono | CLAUDE.md global | nenhuma | **Só texto** (não há máquina que saiba o que é "decisão do dono") |
| Push só com o "sim" | proposta | nenhuma | Permissão `ask` para `git push` em `.claude/settings.json` (ML4) |
| Nunca saltar hooks | não está escrito | nenhuma | Hook do Claude recusa `--no-verify`/`-n` e mexer no `core.hooksPath`; CI apanha quem saltar à mão (ML3, ML14) |
| Bug traz teste | proposta | nenhuma | `commit-msg`: um `fix` sem ficheiro em `tests/` exige `Sem-teste: <motivo>` (ML2–ML3) |
| Provar medindo, 100 % | proposta, `testar.ps1` | hook do Claude no commit | Hook `pre-commit` do git (vale também à mão) + CI (ML3, ML14) |
| Teste de mutação | docstring do `estragos.py` | nenhuma (corre-se à mão) | Catraca: o número de `MUTANTES` não desce; o CI corre os estragos 1×/semana (ML9, ML14) |
| Texto vira barreira | não está escrito | — | Mapa `docs/regras-e-barreiras.md` + teste: cada regra do CLAUDE.md tem uma linha no mapa e a barreira citada existe (ML6) |
| Hooks testados | `test_hooks.py` | fora da cobertura | Hooks e portões entram na medida dos 100 % (ML11) |
| E-mail noreply | não está escrito | nenhuma | `pre-commit` recusa outro e-mail (ML2–ML3) |
| Mensagem com o porquê | não está escrito | nenhuma | `commit-msg` exige corpo em `fix`/`feat`/`refactor` (ML2) |
| Mensagem por ficheiro `-F` | memória | hook bloqueia palavras | Hook do Claude recusa `git commit -m` com várias linhas ou heredoc (ML3) |
| Armadilhas registadas | docs/README | nenhuma | Teste: numeração A1…An seguida e sem repetidos, cada uma com a regra (ML7) |
| Pesquisa com data | `pesquisa/README.md` | nenhuma | Teste: cada ficheiro de `pesquisa/` está no índice, com data (ML7) |
| ADR em ficheiro | docs/README | nenhuma | Teste: números únicos e todos na tabela do índice (ML7). Já falhou: a `auditoria-2026-10-24.md` não está no índice |
| Leitura independente | experiência 0001 | — | **Só texto** (skill `orquestrando-sessoes`); a ML15 usa-a |
| Dependências sem falhas | — | nenhuma | `pre-push` com `npm audit` e linha de base + CI (ML5, ML14) |
| Achados de fora são dados | — | — | **Só texto** (skill `auditoria-de-seguranca`) |

## B. As parciais: como chegam a 100 %

| Regra | Como | Fase |
|---|---|---|
| Regras no ficheiro lido sempre | `CLAUDE.md` novo (≤ 100 linhas, ≤ 160 caracteres) a partir da `docs/proposta-CLAUDE.md` + núcleo Morg Laws. Teste do tamanho. A proposta vai para `docs/arquivo/` | ML6 |
| Sem silenciar alarme | Ligar o `RUF100` (`noqa` sem uso); tirar os `noqa` de regras inativas; teste: cada `noqa`/`pragma`/`node:coverage disable` tem motivo depois de `—`, e a contagem não sobe (catraca). As 2 regras do Biome desligadas ficam com uma ADR (mudam a cascata do CSS) | ML9 |
| Cobertura 100 % real | `statusline.py`, `.claude/hooks/` e `scripts/portoes/` entram no `--source`. A lógica dos `<script>` de `bar`/`splash`/`sistema` passa para `.mjs` testados; nas páginas fica só a cola com o DOM | ML11a, ML11b |
| Hooks são a rede | `onFailure: block` em todos os hooks do Claude; teste que lê o `settings.json` e o exige | ML3 |
| Nomes pesquisáveis | `comum/comum.mjs` → nome pela função (ex.: `paginas-texto.mjs`, a decidir ao ler); `tests/*.Comum.ps1` → `*.Preparacao.ps1`; teste: nenhum ficheiro chamado `comum`, `utils`, `helper(s)`, `common`, `data`, `misc`. O `bar_helper.py` fica: é único no grep e mudá-lo parte os PCs instalados e o hook A2 (exceção numa ADR) | ML10 |
| Catracas | 35 linhas por função: Python por `ast`, PowerShell pelo AST, JS pela regra `noExcessiveLinesPerFunction` do Biome 2.6 (confirmada no schema). As violações de hoje ficam numa linha de base que só desce. PSScriptAnalyzer com um ficheiro de definições e uma linha de base por regra (49 avisos) | ML9 |
| Fins de linha | `.gitattributes` explícito (`*.ps1`, `*.cmd`, `*.bat` em CRLF; o resto em LF), `git add --renormalize` num commit só disso; teste: o disco bate com o `.gitattributes` | ML8 |
| Handoff no repositório | `.context/HANDOFF-<assunto>.md` (o A-RETOMAR sai da memória para lá; a memória só aponta). Teste: secções obrigatórias e hashes que existem no git | ML7 |
| Permissões em 3 colunas | `.claude/settings.json`: `deny` Read de `.env*`, `*.pem`, `*.key`, `~/.ssh`, `~/.claude/.credentials*`; `ask` para `git push`, `npm install`, `npx`, `winget`, `pip install`; `allow` só o que é leitura. Teste do JSON | ML4 |
| Plano com "fora do escopo" e "prova" | `docs/planos/NNNN-*.md` (cópia aprovada da aba Plano) + teste das secções | ML7 |
| Telas | `prefers-reduced-motion` no `splash.html` e no `sistema.html` (o sinal fica, a animação sai); `tabular-nums` na hora e na bateria; teste de contraste ≥ 4,5:1 calculado a partir dos tokens Catppuccin usados em texto. `px` → `rem`: ver a secção D | ML12 |

## C. As falhas: análise e solução

| Falha | Análise | Solução | Fase |
|---|---|---|---|
| Sem portão do git | Os hooks do Claude só travam o agente | `.githooks/` (sh finos que chamam `py -I scripts/portoes/*.py`, testados a 100 %); `core.hooksPath`; o teste do commit sai do hook do Claude para o `pre-commit` (sem correr duas vezes; a guarda `MORG_A_TESTAR` da A30 mantém-se) | ML2, ML3 |
| Sem gitleaks no push | Os segredos só foram procurados por leitura | Instalar o gitleaks 8.30.1 por `winget` (Gitleaks LLC; **pede o OK na hora**); varrer todo o histórico 1×; `pre-push` a partir do `modelos/pre-push` (gitleaks + `npm audit` com linha de base + a lista dos ficheiros de cada commit, Akita #78) | ML5 |
| Sem CI | Nada corre no GitHub | `.github/workflows/`: `testar.ps1` em `windows-latest` (Python, coverage, ruff, Pester 6, PSSA, node, versões fixas) + gitleaks + estragos semanais; actions fixadas por SHA; `permissions: contents: read`. O `testar.ps1` aceita `MORG_PY` em vez do caminho fixo `C:\Windows\py.exe` | ML14 |
| Nome real em testes e exemplos | O primeiro nome do utilizador aparece em 7 ficheiros | Trocar por um nome fictício; `{{NOME}}` de exemplo fictício. Lista negra **fora** do repositório (`git config morg.listaNegra`), lida no `pre-commit` e no `commit-msg` | ML1, ML2 |
| Nomes e caminhos nos docs | Auditoria, pendentes, experiência, pesquisa | "o utilizador"/"o dono"; `<pasta do repositório>`. Teste por padrão (`C:\Users\<nome>`, sem dizer nomes) | ML1 |
| `fix` sem teste nem `Sem-teste:` | `17ce46f` | Daqui para a frente, o `commit-msg` obriga. O antigo fica como exceção registada (não se reescreve o histórico) | ML2 |
| Formato das mensagens | 37 de 55 títulos > 72 caracteres | `commit-msg`: `^(fix\|feat\|docs\|test\|refactor\|chore\|build\|ci\|perf\|style)(\([a-z0-9-]+\))?: ` e ≤ 72; aceita `Merge …` | ML2 |
| `.env` legível | Sem `deny` | Ver B, permissões | ML4 |
| Sem changelog | Produto instalado por outros | `changelog.d/AAAA-MM-DD-assunto.md`; teste do formato; o `commit-msg` exige um fragmento (ou `Sem-changelog: motivo`) num `feat`/`fix` que toque em `2-configuracao/`, `scripts/instalar*` ou `scripts/desinstalar*`; fragmentos do que mudou desde o último envio; `scripts/juntar_changelog.py` testado | ML13 |

## D. O que não dá para seguir a 100 % (fica dito, com o motivo)

1. **Ver o teste a falhar antes da correção:** o git guarda o teste, não a corrida vermelha. A máquina obriga ao
   teste ou ao `Sem-teste:`; os estragos provam que os testes apanham erros; a corrida vermelha fica no texto.
2. **Decisões do dono, leitura independente, achados como dados:** só texto (skills).
3. **Commits por caminho:** o hook trava o agente (`git add -A`, `git add .`, `commit -a`); à mão fica o texto.
4. **Aparência, alvos de toque, daltonismo:** só uma pessoa, no teu teste real. O contraste dos tokens mede-se.
5. **`rem` em vez de `px`:** no Zebar ninguém escolhe o tamanho da letra da página e a barra é medida ao pixel. Proposta:
   uma ADR "não se aplica", a confirmar no teu teste com a escala do Windows a 125 %.
6. **Backup externo da pasta (Akita #74):** está fora do repositório. Fica como recomendação para ti (Histórico de
   Ficheiros ou OneDrive).
7. **Histórico antigo** (o nome nos testes já enviados, o `17ce46f`, os títulos longos): não se reescreve o histórico
   público; fica como exceção registada.
8. **Lista negra no CI:** só com um secret do GitHub (opcional); sem ele, o CI só corre o gitleaks.
9. **O CI só se prova depois de um push** (que pede o teu OK).

## Fases (cada uma termina com uma prova)

- [x] **ML0 Preparação** (2026-10-30):
  - `get_usage`: semanal 3 %, 5 h 21 %;
  - plano antigo marcado (itens "→ ML" nas F3–F6);
  - cópia em `docs/morg-laws/plano-01.md`;
  - `testar.ps1` em **21,5 s**, verde: Python 258 testes a 100 % (1713 linhas, 554 ramos), JS 45, Pester 72, lint ok.
    Chega para o `pre-commit` correr tudo em cada commit.
  - *Prova:* os números acima.
- [x] **ML1 Dados pessoais fora** (2026-10-30):
  - nome fictício nos testes e exemplos ("Ana"; "Bruno" na conta simulada do Pester): 7 ficheiros, 14 linhas;
  - docs sem nomes nem caminhos: 5 ficheiros (auditoria, pendentes, armadilhas, experiência 0001, pesquisa do arranque);
  - `tests/test_dados_pessoais.py`: caminhos `C:\Users\<conta>` fora das contas de exemplo, e-mails que não sejam
    noreply/exemplo, e a lista negra de 5 termos, fora do repositório (`git config morg.listaNegra`);
  - fins de linha mantidos (trocas em bytes, com a contagem certa).
  - *Prova:* vermelho com 3 falhas (4 caminhos, 9 ficheiros com o nome, 3 com a conta) → verde com 4 testes;
    `testar.ps1` verde.
- [x] **ML2 Portões testados** (2026-10-30): `scripts/portoes/` com:
  - `mensagem_commit.py` (formato `tipo(área): `, ≤ 72, sem ponto final, linha em branco, corpo em fix/feat/refactor,
    `Sem-teste:` com motivo; aceita os `Merge`/`Revert` do git);
  - `identidade.py` (noreply + nome contra a lista negra);
  - `lista_negra.py` (sem lista avisa; lista em falta recusa).
  - Mais `tests/test_portoes_*.py` (39 testes) e `tests/carregar_portoes.py`; os portões entram na cobertura do
    `testar.ps1`.
  - O `Sem-changelog:` fica para a ML13 (sem o `changelog.d/`, recusaria todos os feat/fix).
  - *Prova:* vermelho (3 módulos em falta) → verde; `testar.ps1` com 301 testes Python e 100 % (1827 linhas,
    596 ramos). O teste da ML1 apanhou um e-mail de exemplo inventado nestes testes, corrigido.
- [x] **ML3 Ligar o git** (2026-10-30):
  - `.githooks/pre-commit` (identidade, lista negra nos ficheiros, `testar.ps1` com a guarda A30) e `commit-msg`
    (formato e lista negra na mensagem); `core.hooksPath = .githooks`;
  - `.claude/hooks/guarda_do_git.py` substitui o `testes_antes_do_commit.py` (os testes passaram para o git): recusa
    `--no-verify`, `add -A/./--all/:/`, `commit -a` ou `-- .`, `-m` com várias linhas ou heredoc, mudar o
    `hooksPath`, e um commit com o `hooksPath` errado;
  - `onFailure: block` nos 3 hooks; `test_hooks.py` exige-o e exige que cada hook da pasta esteja ligado;
  - README "Para quem contribui"; armadilha A44 (um clone novo usa a identidade global do git).
  - *Prova:* `git add -A -n` recusado pela guarda ao vivo. No clone descartável foram recusados:
    - o e-mail pessoal e o nome real da configuração global (apanhados sem os procurar: ver A44);
    - um título sem tipo;
    - um `fix` sem teste;
    - um nome da lista num ficheiro e na mensagem;
    - o commit com o `testar.ps1` a falhar.

    O commit certo passou.
  - Brecha vista no meu próprio `c9f440b` (commit sem caminhos e com `MORG_A_TESTAR=1`): a guarda passa a recusar
    um commit sem caminhos (fora de um merge) e `MORG_A_TESTAR` num commit; teste vermelho (6 casos) → verde.
- [x] **ML4 Permissões** (2026-10-30):
  - `.claude/settings.json` em três colunas:
    - `deny`: ler `.env`, chaves, credenciais e a lista negra;
    - `ask`: push, instalar (npm, npx, pip, winget, Install-Module) e editar `settings.json`, hooks e `.githooks`;
    - `allow`: leituras do git e o `testar.ps1`;
  - `.gitignore` com `.env`, `.env.*`, `*.pem` e `*.key`;
  - `tests/test_permissoes.py` (5 testes);
  - o `settings.local.json` (desta máquina, fora do git) perdeu dois atalhos largos:
    - `py -I -` corria qualquer código;
    - `gh pr *` deixava criar e juntar PRs sem perguntar. Ficaram só `view`, `list`, `diff` e `checks`.
  - *Prova:* teste vermelho (7 falhas, contando os dois atalhos) → verde. Ao vivo, com um `.env` falso:
    - o `Write` e o `Read` foram recusados pelo deny;
    - o `cat` também foi recusado;
    - a leitura por Python foi recusada pelo modo automático.
  - **Achado:** no modo automático as regras `ask` do settings.json não perguntam. Confirmado pelo dono: o push a
    seco correu sem pergunta, e a escrita de um hook também.
    - Correção: o hook `.claude/hooks/perguntar_antes.py` devolve a decisão "ask" para push, instalações e
      Write/Edit das regras do agente (`.claude/settings*.json`, `.claude/hooks/`, `.githooks/`).
    - Teste vermelho → verde (7 testes).
    - Push a seco repetido: o dono **viu a pergunta**.
  - **Limite:** uma escrita pela shell não passa no Write/Edit (o mesmo limite do hook das 500 linhas). O
    `test_permissoes.py` e o `test_hooks.py` apanham uma regra tirada.
- [x] **ML5 Push seguro** (2026-10-30):
  - gitleaks 8.30.1 instalado pelo `winget` (com o OK do dono; hash verificado; release oficial do GitHub);
  - histórico todo varrido: **62 commits, "no leaks found"**. O 63.º, `c9f440b`, só muda o modo e não tem texto;
  - `scripts/portoes/antes_do_push.py` (15 testes): lista os ficheiros por commit; gitleaks nos commits a enviar
    (sem ele, recusa); `npm audit` contra a linha de base (só crítico/alto novo trava; relatório ilegível trava);
  - `.githooks/pre-push`, `.seguranca/audit-linha-de-base.txt` (vazia: 0 avisos) e README.
  - *Prova:* teste vermelho → verde. Num repositório de teste:
    - o push limpo para o `bare` passou, mostrando os ficheiros;
    - o commit com um token do GitHub falso (aleatório) foi recusado: "leaks found: 1", nada enviado.
- [x] **ML6 Regras no CLAUDE.md** (2026-10-30):
  - 7 skills com `npx skills@1.7.4 add … -s <7 nomes> --copy` (com o OK do dono), iguais ficheiro a ficheiro à cópia
    local lida na 1.ª verificação; `skills-lock.json` com a origem e o hash; CC BY 4.0 em `LICENCAS.txt`;
  - `CLAUDE.md` com 92 linhas: Regra n.º 1, núcleo, nunca, testes, código, docs, commits, arquitetura e índice das
    skills; 30 regras no formato `**TÍTULO:** regra · *motivo*`;
  - `docs/regras-e-barreiras.md`: as 30 regras e a barreira de cada uma:
    - 15 já têm máquina (hook, git, teste ou permissão);
    - 7 começam por texto, com o motivo; 2 delas ganham máquina na ML7 e na ML9;
    - 8 estão por fazer, com a fase.
  - `tests/test_regras.py` (6 testes): tamanho, títulos únicos, cada regra no mapa, caminhos citados existentes, e as
    skills do índice = as instaladas = as do lock;
  - `docs/proposta-CLAUDE.md` passou para `docs/arquivo/`.
  - *Prova:* vermelho (5 falhas com o CLAUDE.md antigo) → o próprio teste apanhou 3 caminhos inválidos no texto
    novo → verde.
  - *Por validar:* se as skills aparecem numa sessão nova (só tu o vês ao abrir uma).
- [x] **ML7 Docs com barreira** (2026-10-30):
  - `tests/test_docs_indices.py` (6 testes), que verifica:
    - cada `.md` e pasta de `docs/` no índice;
    - as ADR seguidas e na tabela;
    - cada pesquisa no índice, com data;
    - as armadilhas A1…An seguidas, cada uma com a regra;
    - os planos com "Fora do escopo" e a prova;
    - os `.context/HANDOFF-<assunto>.md` com as 5 secções e hashes que existem;
  - corrigido o que falhou:
    - a `auditoria-2026-10-24.md` entrou no índice;
    - este plano ganhou "Fora do escopo";
  - A-RETOMAR em `.context/HANDOFF-morg-laws.md` (a memória passa a apontar para lá);
  - mapa atualizado: 5 regras de docs passam de "por fazer" a "teste".
  - *Prova:* vermelho com 3 falhas, 2 reais e 1 intervalo de datas válido que o teste passou a aceitar → verde. As
    skills da ML6 já aparecem nesta sessão (validado).
- [x] **ML8 Fins de linha** (2026-10-30):
  - `.gitattributes`: `* text=auto eol=lf`, CRLF em `.ps1`, `.psm1`, `.cmd` e `.bat`, binários como `binary`;
  - ficheiros convertidos no disco, em bytes (26) e normalizados no índice (17), num commit só disso (`88ca6ef`).
    Entre eles estão o `INSTALAR.cmd` e o `DESINSTALAR.cmd`, que estavam em LF;
  - `tests/test_fins_de_linha.py` (4 testes): o índice em LF, o disco conforme a extensão e os atributos certos.
  - *Prova:*
    - teste vermelho (todos os ficheiros sem atributos);
    - `git diff --cached --ignore-cr-at-eol` só mostrou o `.gitattributes`;
    - `git ls-files --eol`: 165 `lf/lf`, 12 `lf/crlf`, 10 binários;
    - `testar.ps1` verde (360 testes) e estragos **70/70 apanhados**.
  - O portão da ML2 recusou-me um título com 77 caracteres: encurtado.
- [ ] **ML9 Catracas do lint:**
  - `RUF100`;
  - `noqa` com motivo;
  - 35 linhas por função (Python, PowerShell, JS) com linha de base;
  - definições e linha de base do PSScriptAnalyzer;
  - catraca dos `MUTANTES`;
  - ADR das regras do Biome.
  - *Prova:* uma função nova com 36 linhas faz o `testar.ps1` falhar.
- [ ] **ML10 Nomes:** renomear `comum.mjs` e `*.Comum.ps1`; teste dos nomes proibidos; ADR do `bar_helper`.
  - *Prova:* `testar.ps1`; o grep de cada nome novo dá < 5 resultados.
- [ ] **ML11a Cobertura das ferramentas:** `statusline.py`, hooks e portões dentro dos 100 %.
  - *Prova:* relatório da cobertura.
- [ ] **ML11b Cobertura das páginas:** lógica de `bar.html`, `splash.html` e `sistema.html` em `.mjs` testados (uma página por commit); a cola fica em `validacao-manual.md`.
  - *Prova:* cobertura JS 100 %; o teu teste real das páginas.
- [ ] **ML12 Telas:** `prefers-reduced-motion`, `tabular-nums`, teste de contraste dos tokens, ADR do `rem`.
  - *Prova:* teste; o teu teste com "Mostrar animações" desligado no Windows.
- [ ] **ML13 Changelog:** `changelog.d/`, regra no `commit-msg`, fragmentos atrasados e `juntar_changelog.py`.
  - *Prova:* testes; um `feat` em `2-configuracao/` sem fragmento é recusado no clone.
- [ ] **ML14 CI:** workflows e `MORG_PY` no `testar.ps1`.
  - *Prova local:* `testar.ps1` com `MORG_PY`.
  - *Prova real:* só depois do teu OK para o push (pode ir para um ramo de teste).
- [ ] **ML15 2.ª verificação Morg Laws:**
  - auditoria numa sessão nova, com um pedido neutro (sem as conclusões);
  - comparar as contagens com a 1.ª;
  - `docs/morg-laws/verificacao-02-*.md`;
  - estragos;
  - o teu teste real;
  - depois, o pedido do push (`main`, `exp/a`, tag).

## Ficheiros principais

- Novos:
  - `.githooks/`, `scripts/portoes/`, `.github/workflows/`, `.seguranca/`, `changelog.d/`, `.context/`;
  - `docs/regras-e-barreiras.md`, `docs/planos/`;
  - `tests/test_portoes_*.py`, `test_regras.py`, `test_dados_pessoais.py`, `test_docs_indices.py`.
- Mudam:
  - `CLAUDE.md`, `.claude/settings.json`, `.claude/hooks/*.py`;
  - `scripts/testar.ps1`, `ruff.toml`, `biome.jsonc`, `.gitattributes`, `docs/README.md`;
  - os testes e exemplos com o nome;
  - `comum/comum.mjs` e quem o importa (`guia/*.mjs`, `painel/*.mjs`, `tests/comum.test.mjs`, `tests/painel.test.mjs`).
- Reutilizar:
  - o padrão de `.claude/hooks/*.py` (lê o JSON do stdin em UTF-8, sai com 2 e o motivo);
  - `tests/test_hooks.py`;
  - `tests/test_ficheiros_texto.py` (limite de linhas e `GRANDES_POR_DIVIDIR`, modelo para as catracas);
  - `modelos/pre-push` do Morg Laws;
  - o leitor de AST de `testar.ps1` (`$FuncoesExcluidas`).

## Verificação final

- `powershell -File scripts/testar.ps1` verde a 100 %;
- `py -I scripts/estragos.py` sem nenhum estrago a escapar;
- os testes dos hooks no clone descartável (recusados e aceites);
- o varrimento do gitleaks ao histórico;
- a 2.ª verificação (ML15) com as contagens: a meta é 0 falhas e 0 parciais, tirando os itens da secção D;
- o teu teste real (páginas, animações, instalação).
