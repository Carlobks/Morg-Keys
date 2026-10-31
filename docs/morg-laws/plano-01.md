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
- [x] **ML9 Catracas do lint** (2026-10-31):
  - `RUF100` no `ruff.toml`; `tests/test_alarmes.py`:
    - cada `noqa`, `pragma` ou `node:coverage` com motivo;
    - contagem máxima: 4, 1 e 2;
    - `noqa` só de regras que o ruff tem ligadas (perguntado ao próprio ruff).
  - **Achado:** a auditoria Q5 estava errada. A `SIM115` e a `BLE001` estão ligadas por omissão no ruff 0.17 (cerca
    de 400 regras). Tirei os 3 `noqa`, o ruff acusou, e reponho-os.
  - 35 linhas por função:
    - Python: `tests/test_tamanho_das_funcoes.py`, com 4 antigas que só encolhem;
    - JS: `noExcessiveLinesPerFunction` do Biome como erro (0 funções `.mjs` acima);
    - PowerShell: no `testar.ps1` (0 acima).
  - PSScriptAnalyzer: `tests/linha-de-base-pssa.txt` (50 avisos em 6 regras), comparada no `testar.ps1`. Sem ficheiro
    de definições: desligar uma regra seria silenciar.
  - `tests/test_estragos_minimo.py` (≥ 70 estragos); ADR 0008 (regras do Biome desligadas; a experiência fica com a
    seguinte).
  - *Prova:* cada catraca vista a falhar com uma mudança temporária, depois reposta:
    - um `noqa` falso: 3 falhas;
    - uma função de 36 linhas: falha;
    - a linha de base do PSScriptAnalyzer: "10 avisos, linha de base 9";
    - `testar.ps1` verde (366 testes).
  - O HTML inline ainda não passa pelo Biome (ML11b).
- [x] **ML10 Nomes** (2026-10-31):
  - renomeados com `git mv`:
    - `comum/` → `partilhado/` (bateria e Claude da barra, funções dos painéis);
    - `comum/comum.mjs` → `partilhado/paineis.mjs`;
    - `tests/comum.test.mjs` → `tests/paineis.test.mjs`;
    - `tests/*.Comum.ps1` → `tests/*.Preparacao.ps1`;
  - referências atualizadas em bytes, com a contagem por ficheiro: 18 ficheiros, incluindo os `includeFiles` do
    `zpack.json`, o `testar.ps1`, o `estragos.py` e os docs vivos. Os docs históricos (experiência, verificação 01)
    ficam como estavam;
  - `tests/test_nomes.py`: nenhum ficheiro ou pasta com um nome genérico solto (o nome inteiro ou uma parte entre pontos).
  - **ADR do `bar_helper` dispensada:** a regra é sobre nomes *soltos*, e `bar_helper` diz o quê. O teste deixa-o
    passar, de propósito.
  - O instalador renomeia a `~\.glzr` antiga e escreve tudo de novo, por isso não fica uma pasta `comum/` velha.
  - *Prova:* teste vermelho (5 nomes) → verde; `testar.ps1` verde (370 testes; Pester 100 %).
  - Um erro meu: estimei 5 trocas no `testar.ps1` e eram 6. O `assert` parou antes de gravar.
- [x] **ML11a Cobertura das ferramentas** (2026-10-31, `f039a5c`):
  - o `--source` do `testar.ps1` passou a ter `.claude\hooks` e `2-configuracao\claude` (os portões já lá estavam);
  - `correr_como_script()` em `tests/carregar_por_caminho.py`: corre o script como `__main__` neste processo,
    para contar na cobertura (os testes em subprocesso provam o `py -I` real, mas não contam);
  - `tests/test_hooks_como_script.py` (10 testes: os 4 hooks pelo `main()`) e `tests/test_statusline.py`
    (8 testes, com o `rate_limits.json` numa pasta temporária, nunca no `~/.claude` real);
  - **Achado:** o teste das mensagens com várias linhas da guarda passava pela regra "sem caminhos", cujo texto
    também tem "-F", e nunca chegava à recusa certa. Agora leva caminhos e procura "várias linhas".
  - *Prova:* vermelho com "FALHOU: Cobertura Python", 95 % (statusline 0 %, hooks 54–92 %) → verde com 388
    testes Python a 100 % (2186 linhas, 736 ramos); JS 45; Pester 72 a 100 % fora das excluídas.
  - O `main()` da statusline continua com 43 linhas (catraca das antigas): encolhê-lo é estrutura, fica à parte.
- [x] **ML11b Cobertura das páginas** (2026-10-31):
  - a lógica saiu dos `<script>` em linha, sem mudar o comportamento, uma página por commit:
    - `bar.html` → `bar-logica.mjs` (`13579f9`): 306 → 209 linhas;
    - `arranque/splash.html` → `arranque/splash-logica.mjs` (`4c7b6a9`): 218 → 190;
    - `guia/sistema.html` → `guia/sistema-logica.mjs` (`27c66fd`): 118 → 81;
  - no HTML fica só a cola (canvas e SVG dos ícones, providers, `shellExec`, eventos, temporizadores). Os
    caminhos com `{{HOME}}` ficam lá, porque o instalador não troca marcadores nos `.mjs`. O `zpack.json` inclui
    os módulos novos;
  - testes: `bar-logica` 15, `splash-logica` 9 e `sistema-logica` 4. Um deles confirma que cada tecla do painel
    tem ação na camada `sistema` do `config.yaml`;
  - barreira (`090c765`), em `tests/paginas-em-linha.test.mjs`:
    - cada nome importado pelos scripts em linha existe no módulo;
    - catraca do tamanho de cada script em linha (207, 188 e 79 linhas);
    - o Biome passa a ler o JS em linha, com nomes por declarar e por usar e funções até 35 linhas. Até aqui não o
      lia;
  - estragos (`e98ea02`): o `estragos.py` passa a ver os `.mjs` da raiz e de `arranque/`, com mais 10 estragos
    e o mínimo a 80. Resultado: **80/80 apanhados**;
  - `docs/validacao-manual.md`: o passo à mão de cada página.
  - *Prova:*
    - cobertura JS 100 % (79 testes);
    - o teste dos imports, a catraca e o Biome vistos a falhar com estragos temporários;
    - `testar.ps1` verde.
  - *Teste real (2026-10-31):* depois de reinstalar, o dono confirmou o arranque, a barra e o painel `Alt+Esc` no
    Zebar: "Está tudo a funcionar perfeitamente".
- [x] **ML12 Telas** (2026-10-31):
  - `83dc898`: `@media (prefers-reduced-motion: reduce)` no fim das 5 folhas (barra, guia, painel de apps, splash e
    sistema). O plano só nomeava o splash e o sistema, mas as outras também tinham transições.
    - Animações e transições a 0,01 ms, sem atraso e com uma só volta: fica o estado final e o sinal (o arco
      parado). Não se usa `none`, porque o splash espera pelo `transitionend`.
    - O brilho da chávena, movido por JavaScript, sai.
    - `tabular-nums` no `body` de cada página.
  - `d790cb6` (**achado**): o texto apagado usava o `overlay0`, com 3,4:1. Passou para o `overlay2` (5,8 a 6,6:1),
    por decisão do dono. Sobre o fundo `surface0` (campos de filtro e hover das apps) fica o `subtext0`.
    - Teste de contraste calculado a partir dos tokens das folhas, cobrindo os fundos da página, o fundo da própria
      regra e os chips a 16 %.
    - As exceções têm motivo: o ícone da chávena só no hover, as teclas fixas inativas e a borda do estado.
  - ADR 0009: os `px` ficam nas páginas do Zebar, porque ali `1rem` é sempre `16px` e a escala do Windows já chega.
  - *Prova:*
    - `tests/test_telas.py` (8 testes): vermelho com 14 falhas e 1 erro (movimento e algarismos), e com 17
      seletores no `overlay0` (contraste); verde depois das correções;
    - `testar.ps1` verde.
  - *Por validar (o teu teste real):*
    - com "Efeitos de animação" desligado no Windows (Acessibilidade > Efeitos visuais): o arranque sem movimento e
      os painéis sem deslizar;
    - o texto apagado mais legível;
    - a escala a 125 % (ADR 0009).
- [x] **ML13 Changelog** (2026-10-31):
  - `07afb3a`:
    - `changelog.d/AAAA-MM-DD-assunto.md` com `Categoria: …` na primeira linha e os itens com "- ". As categorias
      e a ordem são as do Keep a Changelog 1.1.0, e o ficheiro por mudança vem do towncrier
      (`docs/pesquisa/changelog.md`);
    - `scripts/changelog/juntar_changelog.py` (`<versão> [--rascunho]`) junta os fragmentos no `CHANGELOG.md` e
      apaga-os. Fica numa pasta própria para entrar no `--source` da cobertura sem levar o `estragos.py`;
    - o `commit-msg` recusa um feat ou fix em `2-configuracao/`, no instalador ou no desinstalador sem fragmento
      nem `Sem-changelog: <motivo>`;
    - `tests/test_changelog.py` confere cada fragmento;
    - regra CHANGELOG POR FRAGMENTO no `CLAUDE.md` e no mapa das barreiras; README.
  - `86ec68b`: 10 fragmentos atrasados, com o que mudou desde o último push do `exp/a` (`044f96e`).
  - **Achado:** o `--rascunho` rebentava numa consola cp1252 com o "✻" (A16). Teste vermelho → escreve em UTF-8.
  - *Prova:*
    - vermelho: 11 falhas e 1 erro no portão, e o módulo em falta;
    - verde: `testar.ps1` com 416 testes Python a 100 % (2269 linhas, 770 ramos) e 72 Pester;
    - no clone descartável, o hook `commit-msg` com um `feat` em `styles.css`:
      - recusado sem fragmento;
      - aceite com o fragmento;
      - aceite com `Sem-changelog:`.
    - O `pre-commit` não correu no clone, porque lá não há `node_modules` para o Biome.
  - *Não feito:* estragos novos para o portão e o juntar (o mínimo de 80 mantém-se).
- [x] **ML14 CI** (2026-10-31):
  - `.github/workflows/ci.yml` com três tarefas:
    - `testar`: o `testar.ps1` no `windows-latest`, em cada push e PR;
    - `segredos`: o gitleaks 8.30.1 em todo o histórico, com o sha256 conferido;
    - `estragos`: à segunda-feira, ou à mão.
  - Segurança e versões:
    - as actions estão fixadas por SHA, com a versão em comentário (checkout v7.0.1, setup-python v7.0.0,
      setup-node v7.1.0);
    - `contents: read` e `persist-credentials: false`;
    - versões fixas, as desta máquina.
  - O `testar.ps1` e o `estragos.py` aceitam `MORG_PY`. O mapa das barreiras e o README citam o CI.
  - **Achado (A47):** com um `MORG_PY` errado, o `testar.ps1` dizia "OK", porque o `& $Py` falha sem mexer no
    `$LASTEXITCODE`. Agora falha fechado. Teste vermelho (saía 0), depois verde.
  - *Prova local:*
    - `tests/test_ci.py` (8 testes) vermelho, depois verde;
    - `testar.ps1` verde com `MORG_PY` no `python.exe` real (423 testes Python a 100 %, 72 Pester);
    - `testar.ps1` verde normal (424).
  - *Prova real* (com o OK do dono, push só para o ramo `ci/teste-ml14`):
    - 1.ª corrida (`41229680427`): `segredos` verde; `testar` com 2 falhas, porque o checkout não liga o
      `core.hooksPath` que os testes da guarda do git exigem. O JS, o Pester, o lint e as catracas já passaram.
    - `82d2109`: o CI liga os portões como diz o README, sem afrouxar os testes. Teste vermelho, depois verde.
    - 2.ª corrida (`41230243035`): **`testar` verde (3 min) e `segredos` verde**.
  - *Não provado:* os `estragos` no GitHub. O `workflow_dispatch` e o agendamento só correm quando o workflow
    estiver no ramo por omissão (`main`).
  - O ramo `ci/teste-ml14` continua no GitHub. Apagá-lo pede o OK do dono.
- [~] **ML15 2.ª verificação Morg Laws** (2026-10-31, sessão nova e neutra, `3e85bd9` e `17aa84f`):
  - **44 regras aplicáveis: 29 cumpridas, 11 em parte, 1 falha e 3 por validar.** Na 1.ª eram 17, 11, 9 e 4.
    Nada do que a 1.ª mediu piorou.
  - Provas: `testar.ps1` verde (424 testes Python a 100 %), estragos **80/80** e gitleaks com 92 commits, sem
    achados.
  - A meta (0 falhas e 0 parciais fora da secção D) **não foi atingida**.
    - A falha é o K3: falta `disableBypassPermissionsMode`.
    - Achados médios:
      - M1: o caminho pessoal em 4 commits já publicados (secção D7: não se reescreve);
      - M2: `cat .env` pelo terminal;
      - M3: `curl | sh` sem pergunta;
      - M4: os estragos no disco partilhado.
    - Achados baixos: B2–B10.
  - Falta: a decisão do dono sobre os achados; depois, o pedido do push.
  - Lista original da fase:
  - auditoria numa sessão nova, com um pedido neutro (sem as conclusões);
  - comparar as contagens com a 1.ª;
  - `docs/morg-laws/verificacao-02-*.md`;
  - estragos;
  - o teu teste real;
  - depois, o pedido do push (`main`, `exp/a`, tag).

- [x] **ML16 Achados da 2.ª verificação** (2026-10-31; pedido pelo dono: "corrige antes" do push).
  - **Feito:** 9 commits, de `bcf3a82` a `9a6cd8c`, e a ADR 0010. A tabela achado → commit → barreira está no fim
    da verificação 02.
  - Achados durante o trabalho:
    - a 1.ª corrida dos estragos na cópia parou porque o worktree não tem `node_modules` (o Biome do teste das
      páginas). Corrigido em `97e20a5`: o `node_modules` é copiado, e não ligado, e a tarefa `estragos` do CI
      ganhou o `npm ci`;
    - a barreira dos nomes apanhou mais 3 `HELPER`, além dos 2 da verificação;
    - o `Teste-mudado:` recusou o próprio commit que o criou, e o da linha de base do PSScriptAnalyzer, até
      levarem o motivo;
    - o hook dos segredos recusa também um texto que só cita o padrão (ex.: num heredoc), o limite da A32.
  - *Prova:*
    - cada teste vermelho antes da correção, depois verde;
    - `testar.ps1` verde (445 testes Python a 100 %, 72 Pester);
    - **estragos 80/80 na cópia**, com o `git status` limpo durante a corrida;
    - ao vivo: `cat` do ficheiro de ambiente e download para a shell **recusados** pelo hook. O `gh pr create --help`
      correu: se apareceu a pergunta, foi o hook (não o consigo ver daqui).
  - Fica em texto o K5 (hook de fim de sessão). Por validar contigo: N2, D7 (alvos de toque) e K6 (backup).
  - **Push** (2026-10-31, com o OK do dono):
    - `main` `e7db97a..5f1ee68`, `exp/a` `044f96e..861c371` e a tag nova `exp-a-medida`;
    - o gitleaks varreu 69 + 1 commits, sem achados;
    - CI do `exp/a` (`41234044122`): **`testar` e `segredos` verdes**.
    - Ficam por fazer: apagar o ramo `ci/teste-ml14` (com o OK) e levar o workflow ao `main`, para os estragos
      semanais correrem.
  - Plano original da fase:
  - **Objetivo:** fechar a falha K3 e os achados M2–M4 e B2–B10 de `docs/morg-laws/verificacao-02-2026-10-31.md`,
    cada um com um teste visto a falhar antes da correção.
  - **Fora do escopo:**
    - reescrever o histórico publicado (o M1 fica como exceção numa ADR);
    - os alvos de toque e o backup (D7 e K6), que se validam contigo;
    - o push.
  - **Passos**, um commit por grupo:
    1. **Permissões e hooks do agente** (K3, M2, M3, B2, B3):
       - `disableBypassPermissionsMode: "disable"` no `.claude/settings.json`;
       - novo hook `.claude/hooks/bloquear_segredos.py` (Bash e PowerShell): recusa comandos que nomeiam `.env`,
         `.env.*`, `*.pem`, `*.key`, `~/.ssh` ou as credenciais do Claude, e recusa um download que vai direto
         para uma shell (`curl|wget|iwr|irm … | sh|bash|iex|powershell`);
       - o `perguntar_antes.py` passa a perguntar antes de `gh pr create|merge` e `gh release create`;
       - o `guarda_do_git.py` recusa o `git stash`, salvo `list` e `show`, porque leva o trabalho de outras sessões;
       - testes em `test_permissoes.py`, `test_hooks*.py` e `test_guarda_do_git.py`;
       - a mudança no `settings.json` e nos hooks pede o teu "sim" na hora, porque o hook `perguntar_antes` o exige.
    2. **Estragos numa cópia** (M4): o `estragos.py` corre num `git worktree add --detach` temporário, em vez do
       disco partilhado, e remove-o no fim, também se rebentar. Mede o último commit. O teste confere que a pasta
       dos estragos não é a raiz do repositório.
    3. **Teste mudado pede o porquê** (B10): o `commit-msg` exige a linha `Teste-mudado: <motivo>` quando o
       commit apaga ou muda linhas de ficheiros que já existiam em `tests/`. Acrescentar casos não pede nada.
       O K5 (hook de fim de sessão) fica em texto, com o motivo: o handoff é atualizado no commit que fecha cada
       fase, e um hook de fim de sessão dispararia em cada turno.
    4. **Regras com motivo** (B6, B4): cada regra do `CLAUDE.md` ganha o motivo. Onde não couber nas 100 linhas,
       o motivo vai para uma coluna "Porquê" no `docs/regras-e-barreiras.md`. O `test_regras.py` exige o motivo
       num dos dois sítios. O mapa corrige os FINS DE LINHA (a barreira já existe desde a ML8).
    5. **Pequenos** (B5, B7, B8, B9):
       - BOM no `uncloak.ps1`, com a linha de base do PSScriptAnalyzer a descer de 1 para 0, e um teste que exige
         o BOM em todos os `.ps1`;
       - `aria-label="Fechar"` nos botões ✕, mantendo o ✕ (o rótulo visível decides tu no teste real);
       - `helper` e `data` renomeados pela função, com o `test_nomes.py` a apanhar identificadores genéricos em
         `.mjs` e `.html`;
       - "Joao Silva" → "Ana" no `Tutorial.html`.
    6. **M1 em ADR 0010:** o histórico já publicado fica como está (o motivo é o da secção D7), e a árvore está
       limpa com o teste.
  - *Prova:*
    - cada teste vermelho antes da correção, depois verde;
    - `testar.ps1` verde;
    - estragos 80/80, já corridos na cópia, com o `git status` limpo durante a corrida;
    - sondas ao vivo dos hooks novos: `cat .env` e `curl … | sh` recusados, e `gh pr create` a perguntar.
  - Depois: a verificação 02 ganha uma nota com o que fechou, e segue-se o pedido do push.

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
