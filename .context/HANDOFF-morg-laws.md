# Handoff: plano Morg Laws (cumprir as regras gerais a 100 %)

Para retomar numa sessão nova. Confirme o estado no repositório (`git log --oneline`) antes de confiar neste
ficheiro. Atualizado no commit que fecha cada fase. Modelo: skill `orquestrando-sessoes` §3.

## Objetivo

Pôr o Morg Keys a cumprir as regras do Morg Laws: cada regra do `CLAUDE.md` com uma barreira de máquina, ou com o
motivo escrito de ficar só em texto. Plano: `docs/morg-laws/plano-01.md` (fases ML0–ML15; o original vive na aba
Plano do Claude). Ponto de partida: `docs/morg-laws/verificacao-01-2026-10-30.md`. Mapa: `docs/regras-e-barreiras.md`.

## Estado verificado (2026-10-31, ramo `exp/a`, nada enviado para o GitHub)

| Fase | Commits | O que ficou |
|---|---|---|
| Verificação 01 | `84a9bb6` | 41 regras: 17 cumpridas, 11 em parte, 9 falhas, 4 por validar |
| ML0 | `df1db39` | `testar.ps1` em 21,5 s |
| ML1 | `9c92f52` | nomes fictícios; `tests/test_dados_pessoais.py`; lista negra fora do repositório |
| ML2 | `bac19a6` | `scripts/portoes/` (mensagem, identidade, lista negra) a 100 % |
| ML3 | `af01506`, `c9f440b`, `7986911` | `.githooks/` + `core.hooksPath`; `.claude/hooks/guarda_do_git.py` |
| ML4 | `42edd20`, `f9307b0` | deny/ask/allow; `.claude/hooks/perguntar_antes.py` |
| ML5 | `21996bb`, `54b1902` | gitleaks 8.30.1; histórico limpo (62 commits); `.githooks/pre-push` |
| ML6 | `994fac6` | `CLAUDE.md` com 30 regras; mapa das barreiras; 7 skills |
| ML7 | `5343c18` | testes dos índices, ADR, armadilhas, pesquisa, planos e handoffs |
| ML8 | `88ca6ef`, `2d083fd` | `.gitattributes` explícito; fins de linha normalizados; estragos 70/70 |
| ML9 | `627f2bb` | catracas: alarmes, 35 linhas por função, PSScriptAnalyzer, estragos; ADR 0008 |
| ML10 | `8c5a363` | `partilhado/paineis.mjs`, `tests/*.Preparacao.ps1`; `tests/test_nomes.py` |
| ML11a | `f039a5c` | hooks do Claude e `statusline.py` nos 100 %; `correr_como_script()` |
| ML11b | `13579f9`, `4c7b6a9`, `27c66fd`, `090c765`, `e98ea02` | lógica das 3 páginas em `*-logica.mjs`; catraca e Biome nos scripts em linha |

Última suíte: 388 testes Python a 100 % (2186 linhas, 736 ramos: pack, portões, hooks e statusLine), 79 JS a 100 %,
72 Pester a 100 % fora das funções excluídas; ~21 s por commit.

## Decisões e porquê

Do dono (2026-10-30), perguntadas com recomendação:
- **Morg Laws antes da F1:** as fases criam a rede (hooks do git, gitleaks, CI) que protege tudo o que vem depois,
  incluindo o push que está à espera.
- **Commits `tipo(área): …` com hook:** formato do Morg Laws; só um hook o obriga. O histórico antigo fica.
- **Changelog por fragmentos (`changelog.d/`, ML13):** o produto é instalado por outras pessoas.
- **Só 7 skills:** SQL, Supabase e Next.js não se aplicam a este projeto.
- **Sem AGENTS.md:** só se usa o Claude; as regras ficam no `CLAUDE.md`.
- **Não reescrever o histórico publicado:** o nome real nos testes antigos, o `17ce46f` sem teste e os títulos
  longos ficam como exceção registada (secção D do plano).
- **Push e instalações sempre com o OK, fase a fase:** o dono aprova cada fase ("faz a MLn") e cada instalação.

Técnicas (tomadas durante as fases, com o motivo medido):
- **Nome fictício "Ana" (e "Bruno" na conta simulada do Pester); lista negra fora do repositório**
  (`git config morg.listaNegra`): os nomes reais não podem estar escritos nem no teste que os procura.
- **Testes no `.githooks/pre-commit`, não no hook do Claude:** um hook do Claude só trava o agente; o do git vale
  também à mão. A guarda `MORG_A_TESTAR` (A30) evita o ciclo testes → commit → testes.
- **`guarda_do_git.py` recusa** `--no-verify`, `add -A/./:/`, `commit -a`, commit sem caminhos (fora de merge),
  `-m` com várias linhas e `MORG_A_TESTAR` num commit: cada um salta ou estraga os portões (as duas últimas brechas
  vieram do meu próprio `c9f440b`).
- **Hook `perguntar_antes.py` em vez de só regras `ask`:** no modo automático as regras `ask` do `settings.json`
  não perguntam (o dono confirmou: o push a seco correu sem pergunta); com o hook, a pergunta apareceu (A46).
- **`settings.local.json` sem `py -I -` nem `gh pr *`:** o primeiro corria qualquer código, o segundo deixava criar e
  juntar PRs sem perguntar.
- **gitleaks e npm audit a falhar fechado:** sem gitleaks ou com relatório ilegível o push não sai; a linha de base
  do npm audit só encolhe (nunca se acrescenta um aviso para passar).
- **`CLAUDE.md` ≤ 100 linhas com `**TÍTULO:**` + mapa das barreiras + `tests/test_regras.py`:** regra só escrita
  não se cumpre; um caminho citado que não existe ensina o agente a saltar a regra.
- **Handoff em `.context/` no repositório:** a memória do agente fica fora do git e de outras contas.
- **LF no git, CRLF só em `.ps1/.psm1/.cmd/.bat`:** o `cmd.exe` falha com LF nos `goto`; o resto é LF (A27).
- **`noqa` de `SIM115`/`BLE001` mantidos:** a auditoria Q5 errou; o ruff 0.17 liga ~400 regras por omissão
  (medido). O `tests/test_alarmes.py` pergunta ao ruff que regras estão ligadas.
- **PSScriptAnalyzer com linha de base, sem ficheiro de definições:** desligar uma regra seria silenciá-la.
- **Biome `noExcessiveLinesPerFunction` como erro:** 0 funções `.mjs` acima de 35 linhas, por isso trava logo.
- **ADR 0008 para as regras do Biome desligadas:** a experiência 0001 fica com o número livre seguinte.
- **`partilhado/paineis.mjs` e ADR do `bar_helper` dispensada:** a regra é sobre nomes *soltos*.
- **`Sem-changelog:` só na ML13:** sem `changelog.d/` o portão recusaria todos os feat/fix.
- **Hooks e statusLine corridos em processo (`runpy`) além do subprocesso:** o subprocesso prova o `py -I` real
  mas não conta na cobertura; correr os dois é o padrão já usado nos portões.
- **`main()` da statusline com 43 linhas fica:** encolhê-lo é mudança de estrutura, num commit à parte.
- **`{{HOME}}` fica no HTML das páginas:** o instalador só troca marcadores em .html/.css/.json/.py/.ps1/.txt/.yaml;
  num `.mjs` o caminho ficaria por trocar.
- **Biome dos scripts em linha dentro de um teste (pasta temporária):** o `biome.jsonc` do projeto não lê o JS
  dentro do HTML; o suporte de HTML do Biome é experimental.
- **O `esc` da barra fica próprio:** aceita `null` (texto vazio); o do `paineis.mjs` escreveria "null".

## Descartado

- Regras `ask` como única barreira (ver acima).
- `git commit -- <caminhos>` para a marca de executável: perde-a no Windows; usar `git add --chmod=+x` e
  `git commit -i` (A45).
- Uma lista de regras do ruff escrita à mão no teste: estava errada; pergunta-se ao ruff.

## Próximos passos

1. **ML12:** `prefers-reduced-motion` no splash e no painel do sistema, `tabular-nums` na hora e na bateria, teste
   de contraste dos tokens Catppuccin e ADR do `rem`.
2. ML13 (changelog). O teste real das 3 páginas (ML11b) fica com o dono, depois de reinstalar.
3. ML14: CI (só se prova depois de um push, com o OK do dono). ML15: 2.ª verificação numa sessão nova, neutra.
4. Depois: a F1 da auditoria (arranque robusto); a experiência 0001 (fases 4–6); jogos; A38.

**Cuidados:**
- Regra n.º 1 (A2): nunca arrancar o ambiente a partir daqui.
- Cada commit corre os testes (~21 s). Passar a mensagem por `py -I scripts/portoes/mensagem_commit.py <ficheiro>`
  antes do commit: títulos acima de 72 caracteres já foram recusados 2×.
- Commit por caminho; os ficheiros apagados vão só no `commit`, não no `add`.
- Editar em bytes com `assert` da contagem; ver `git ls-files --eol` antes e depois.
- O gitleaks está fora do PATH das consolas antigas: `%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gitleaks.Gitleaks_*`.
- A lista negra está em `%USERPROFILE%\.config\morg-keys\` (as permissões negam ao agente lê-la).
- A identidade global do git tem o nome real e um e-mail pessoal: um clone novo precisa de `--local` (A44).
