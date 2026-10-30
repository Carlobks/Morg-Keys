# 1.ª verificação Morg Laws (2026-10-30, ramo `exp/a`)

Pedido do dono do projeto: ver se o Morg Keys segue as regras gerais do repositório Morg Laws (o `AGENTS.md`, as
skills, os modelos de hooks, os aprendizados e os "não faça" do livro do Akita). Só leitura: nada foi alterado.

**Como se fez:** leitura de todo o Morg Laws; para cada regra, procura da prova no Morg Keys (ficheiros, histórico
do git com 55 commits, definições do Claude Code). Medições feitas: `scripts/testar.ps1` (resultado: "OK: todos os
testes passaram") e `npm audit` ("found 0 vulnerabilities").

**Resultado: 41 regras aplicáveis.** 17 cumpridas · 11 cumpridas em parte · 9 falhas · 4 por validar.

## 1. O que se aplica

| Aplica-se | Não se aplica |
|---|---|
| Núcleo do `AGENTS.md` (10 regras) e a secção "Nunca" | Skills `sql-postgres`, `supabase`, `nextjs-react` (sem banco nem Next/React) |
| Skills `escrevendo-regras-de-agente`, `git-e-commits`, `testes-e-provas`, `orquestrando-sessoes` | Categorias 1–8 da auditoria de segurança (RLS, Server Actions, buckets…) |
| Skill `pondo-o-plano-a-prova` | Nota de TypeScript |
| Skill `auditoria-de-seguranca`, categorias 9–12 (segredos, entrada não confiável, dados pessoais, dependências) | Regra "escrita em pt-BR" (vale só para o próprio Morg Laws) |
| Skill `desenhando-telas`, em parte (contraste, cor, movimento, tamanhos) | Escrita no "banco de produção" (não existe) |
| `modelos/pre-push`, as ideias dos hooks (noreply, lista negra), notas do Windows, "não faça" do Akita | |

## 2. Cumprido

| Regra | Prova |
|---|---|
| Plano antes de mexer, com o "sim" do dono | Aba Plano com as fases F0–F7 aprovadas e "A-RETOMAR" |
| Decisão a meio vai ao dono, com recomendação | Regra no CLAUDE.md global; decisões registadas em `auditoria-2026-10-24.md` |
| Push e PR só com o "sim" | 19 commits à espera do OK |
| Nunca saltar hooks | 0 menções a `--no-verify` nos 55 commits |
| Bug corrigido traz o teste | `dbb7f96`, `14241f4`, `68cfda9` |
| Provar medindo | `testar.ps1` exige 100 % (Python, JS, PowerShell) |
| Teste de mutação (Akita #25) | `scripts/estragos.py` |
| Texto vira barreira | Hooks `bloquear_arranque.py`, `limite_de_linhas.py`, `testes_antes_do_commit.py` |
| Hooks testados | `tests/test_hooks.py` |
| E-mail noreply | 55 de 55 commits |
| Mensagem com o porquê | 54 de 55 commits com corpo |
| Mensagem por ficheiro (`-F`) | Prática registada (o hook bloqueia certas palavras na linha de comando) |
| Registar o que se aprende | `docs/armadilhas.md` (A1–A43) |
| Pesquisa em ficheiro próprio, com data | `docs/pesquisa/` com índice datado (faz o papel do `FONTES.md`) |
| Decisões em ficheiro | ADR 0001–0007 em `docs/decisoes/` |
| Leitura independente sem dar a conclusão | Auditoria com 4 auditores separados; fase 4 da experiência esconde os docs do subagente |
| Dependências sem falhas conhecidas | `npm audit`: 0 |
| Achado de terceiros tratado como dado | PR #1 auditado sem correr o código externo |

## 3. Cumprido em parte

| Regra | O que falta |
|---|---|
| Ficheiro de regras curto e com as regras | `CLAUDE.md` com 14 linhas só tem a A2; o resto está em `docs/proposta-CLAUDE.md`, nunca adotada (Q2) |
| Sem silenciar alarme | 4 `noqa` e 1 `pragma: no cover` com motivo, mas há `noqa` de regras inativas (Q5); 2 regras do Biome desligadas no projeto |
| Cobertura 100 % real | Fora da medida: `statusline.py`, hooks, JS dentro dos `<script>` das páginas (Q1) |
| Hooks são a rede | Hook dos testes sem `onFailure: block` (Q10) |
| Nomes únicos e pesquisáveis | `comum/comum.mjs`, `tests/*.Comum.ps1`, `bar_helper.py`; a F3 planeia `scripts/comum.ps1` |
| Catraca: o que viola não piora | Existe para linhas por ficheiro; falta para as 35 linhas por função (Q3) e para os 49 avisos do PSScriptAnalyzer |
| Fins de linha consistentes | `.gitattributes` com `* -text`; 119 LF e 17 CRLF; 2 incidentes (Q9) |
| Handoff por assunto | Existe, mas fora do repositório (memória e plano em `~/.claude`) |
| Permissões em três colunas | Só "allow"; sem "deny" nem "ask" |
| Plano com "fora do escopo" e "prova de pronto" | Nem todas as fases o dizem |
| Movimento e tamanhos nas telas | Sem `prefers-reduced-motion`; 61 tamanhos de letra em `px`, 0 em `rem` |

## 4. Falhas

1. **Sem portão do git:** os 3 hooks são do Claude Code; um commit feito à mão salta tudo. Sem `.githooks/` nem
   `core.hooksPath`.
2. **Sem `pre-push` com gitleaks;** o gitleaks não está instalado. A verificação de segredos foi leitura de agente.
3. **Sem CI:** não existe `.github/workflows`.
4. **Dados reais em testes e exemplos:** o primeiro nome do utilizador aparece em testes (Python e Pester), no
   `splash.html`, no `arranque.txt`, no `morg_config_arranque.py`, no `instalar.ps1` e em `docs/instalacao.md`.
5. **Nomes de pessoas e caminhos da máquina nos docs públicos** (auditoria, pendentes, experiência 0001, pesquisa
   do arranque).
6. **Correção sem teste e sem `Sem-teste:`:** `17ce46f`; 0 linhas `Sem-teste:` no histórico.
7. **Formato das mensagens:** 37 de 55 títulos acima de 72 caracteres; nenhum em `tipo(área): …`.
8. **Sem negação de leitura de `.env` e segredos** nas permissões.
9. **Sem changelog** (`CHANGELOG.md` ou `changelog.d/`), num produto que outras pessoas instalam.

## 5. Por validar

| Regra | Porquê |
|---|---|
| Commits por caminho (nunca `git add -A`) | O histórico não guarda o comando; só os registos das sessões antigas |
| Teste visto a falhar antes da correção | O commit guarda o teste, não a corrida a vermelho |
| Contraste ≥ 4,5:1, alvos ≥ 24 px, cor nunca sozinha | Exige abrir as páginas no ambiente, o que a regra n.º 1 (A2) não deixa ao agente |
| Backup externo da pasta (Akita #74) | Não se vê pelo repositório |

## 6. Seguimento

O plano de implementação que põe isto a 100 % fica na aba Plano e em `docs/morg-laws/` quando for aprovado.
