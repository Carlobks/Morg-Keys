# Handoff: plano Morg Laws (cumprir as regras gerais a 100 %)

Para retomar numa sessão nova. Confirme o estado no repositório (`git log --oneline`) antes de confiar neste
ficheiro. Atualizado no commit que fecha cada fase. Modelo: skill `orquestrando-sessoes` §3.

## Objetivo

Pôr o Morg Keys a cumprir as regras do Morg Laws: cada regra do `CLAUDE.md` com uma barreira de máquina, ou com o
motivo escrito de ficar só em texto. Plano: `docs/morg-laws/plano-01.md` (fases ML0–ML15; o original vive na aba
Plano do Claude). Ponto de partida: `docs/morg-laws/verificacao-01-2026-10-30.md`. Mapa: `docs/regras-e-barreiras.md`.

## Estado verificado (2026-10-31, ramo `exp/a`; enviado para o GitHub com o OK do dono, CI verde)

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
| ML12 | `83dc898`, `d790cb6` | sem animações quando o Windows as desliga; tabular-nums; contraste 4,5:1; ADR 0009 |
| ML13 | `07afb3a`, `86ec68b` | `changelog.d/`, `juntar_changelog.py`, `Sem-changelog:` no `commit-msg`; 10 fragmentos atrasados |
| ML14 | `1dcb1dc`, `82d2109` | `.github/workflows/ci.yml` (testar, gitleaks, estragos semanais), `MORG_PY`, A47; verde no GitHub (ramo `ci/teste-ml14`) |
| ML15 | `3e85bd9`, `17aa84f` | 2.ª verificação (sessão neutra): 29 cumpridas, 11 em parte, 1 falha, 3 por validar |
| ML16 | `bcf3a82` … `9a6cd8c` | achados da 2.ª: hook dos segredos, stash, PR, estragos numa cópia, `Teste-mudado:`, motivos, nomes, BOM, aria-label, ADR 0010 |

Última suíte: 445 testes Python a 100 % (2306 linhas, 782 ramos: pack, portões, hooks, statusLine e changelog), 79 JS a 100 %,
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
- **Texto apagado em `overlay2` (decisão do dono, ML12):** o `overlay0` dava 3,4:1; o `overlay2` mantém um degrau
  abaixo do `subtext0`. Sobre `surface0` (4,45:1) usa-se o `subtext0`.
- **Reduced-motion a 0,01 ms e não `none`:** o splash espera pelo `transitionend` da opacidade para soltar a cortina.
- **`px` nas páginas (ADR 0009):** no Zebar `1rem` é sempre `16px` e a escala do Windows já chega às páginas.
- **Fragmento `AAAA-MM-DD-assunto.md` com `Categoria:` dentro (ML13):** sem hash (não existe antes do commit) e
  sem a categoria no nome (um nome errado mudava-a sem ninguém notar). Categorias do Keep a Changelog.
- **`scripts/changelog/` numa pasta própria:** o `--source` da cobertura aceita pastas; `scripts/` levaria o
  `estragos.py`. Os scripts que escrevem na consola escrevem bytes UTF-8 (A16): o "✻" rebentava o print.
- **CI só com SHAs e versões fixas (ML14):** uma action com menos de 2 semanas fica de fora (setup-python
  v7.0.0 e não v7.1.0). O gitleaks no CI é o binário oficial com o sha256 no workflow, sem action de terceiros.
- **O `testar.ps1` falha fechado sem o Python (A47):** `Get-Command $Py` antes de contar com o `$LASTEXITCODE`.

## Descartado

- Regras `ask` como única barreira (ver acima).
- `git commit -- <caminhos>` para a marca de executável: perde-a no Windows; usar `git add --chmod=+x` e
  `git commit -i` (A45).
- Uma lista de regras do ruff escrita à mão no teste: estava errada; pergunta-se ao ruff.

## Próximos passos

1. Feito a 2026-10-31: push do `main` (`5f1ee68`), do `exp/a` (`861c371`) e da tag `exp-a-medida`; CI do `exp/a`
   verde (corrida 41234044122 do GitHub Actions). Falta, com o OK: apagar o ramo `ci/teste-ml14` e levar o workflow ao `main` (os
   `estragos` semanais só correm lá). Opcional: uma 3.ª verificação neutra para medir a ML16.
2. Teste real da ML12 com o dono (animações desligadas no Windows, texto apagado, escala a 125 %).
3. O CI corre em cada push: um vermelho no GitHub lê-se com `gh run view <id> --log-failed`.
4. Depois do plano: a ordem está em `docs/pendentes.md` (bug do painel Apps e arranque, relatório de erros,
   frases, modal do Claude, guia do Alt+R, F1–F7, experiência 0001, jogos e A38).

**Cuidados:**
- Regra n.º 1 (A2): nunca arrancar o ambiente a partir daqui.
- Cada commit corre os testes (~21 s). Passar a mensagem por `py -I scripts/portoes/mensagem_commit.py <ficheiro>`
  antes do commit: títulos acima de 72 caracteres já foram recusados 2×.
- Commit por caminho; os ficheiros apagados vão só no `commit`, não no `add`.
- Editar em bytes com `assert` da contagem; ver `git ls-files --eol` antes e depois.
- O gitleaks está fora do PATH das consolas antigas: `%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gitleaks.Gitleaks_*`.
- A lista negra está em `%USERPROFILE%\.config\morg-keys\` (as permissões negam ao agente lê-la).
- A identidade global do git tem o nome real e um e-mail pessoal: um clone novo precisa de `--local` (A44).
- O hook `bloquear_segredos` recusa qualquer comando que só cite um segredo ou o padrão do download (ex.: num
  heredoc); escrever o script num ficheiro e corrê-lo. Mudar ou tirar linhas em `tests/` pede `Teste-mudado:`.
