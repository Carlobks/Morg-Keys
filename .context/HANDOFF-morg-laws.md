# Handoff: plano Morg Laws (cumprir as regras gerais a 100 %)

Para retomar numa sessão nova. Confirme o estado no repositório (`git log --oneline`) antes de confiar neste
ficheiro. Atualizado no commit que fecha cada fase. Modelo: skill `orquestrando-sessoes` §3.

## Objetivo

Pôr o Morg Keys a cumprir as regras do Morg Laws: cada regra do `CLAUDE.md` com uma barreira de máquina, ou com o
motivo escrito de ficar só em texto. Plano: `docs/morg-laws/plano-01.md` (fases ML0–ML15). Ponto de partida:
`docs/morg-laws/verificacao-01-2026-10-30.md`. Mapa atual: `docs/regras-e-barreiras.md`.

## Estado verificado (2026-10-30, ramo `exp/a`, nada enviado para o GitHub)

| Fase | Commits | O que ficou |
|---|---|---|
| Verificação 01 | `84a9bb6` | 41 regras: 17 cumpridas, 11 em parte, 9 falhas, 4 por validar |
| ML0 | `df1db39` | `testar.ps1` em 21,5 s |
| ML1 | `9c92f52` | nomes fictícios; `tests/test_dados_pessoais.py`; lista negra fora do repositório |
| ML2 | `bac19a6` | `scripts/portoes/` (mensagem, identidade, lista negra) a 100 % |
| ML3 | `af01506`, `c9f440b`, `7986911` | `.githooks/` + `core.hooksPath`; `.claude/hooks/guarda_do_git.py` |
| ML4 | `42edd20`, `f9307b0` | deny/ask/allow; `.claude/hooks/perguntar_antes.py` |
| ML5 | `21996bb`, `54b1902` | gitleaks 8.30.1; histórico limpo; `.githooks/pre-push` |
| ML6 | `994fac6` | `CLAUDE.md` com 30 regras; mapa das barreiras; 7 skills |
| ML7 | `5343c18` | testes dos índices, ADR, armadilhas, pesquisa, planos e handoffs |
| ML8 | `88ca6ef` + este commit | `.gitattributes` explícito; fins de linha normalizados; estragos 70/70 |

## Decisões (do dono, 2026-10-30)

- As fases Morg Laws vêm antes da F1 da auditoria.
- Commits `tipo(área): …` obrigados por hook; changelog por fragmentos em `changelog.d/` (ML13).
- Só as 7 skills que servem; **sem AGENTS.md** (só se usa o Claude).
- Não se reescreve o histórico publicado.

## Descartado

- Regras `ask` no `settings.json` como única barreira: no modo automático não perguntam. Ficou o hook
  `perguntar_antes.py`, que o dono confirmou que pergunta.
- Testes no hook do Claude: passaram para o `.githooks/pre-commit`, para valerem também à mão.
- `git commit -- <caminhos>` para mudar a marca de executável: perde-a no Windows (A45).

## Próximos passos

1. ML9: catracas do lint (RUF100, 35 linhas por função, PSScriptAnalyzer, MUTANTES) e ADR das regras do Biome.
2. ML10 a ML13: catracas do lint, nomes, cobertura das páginas, telas, changelog.
3. ML14: CI (só se prova depois de um push, com o OK do dono). ML15: 2.ª verificação numa sessão nova.
4. Depois: a F1 da auditoria (arranque robusto).

Cuidados: Regra n.º 1 (A2); cada commit corre os testes (~21 s); o gitleaks está fora do PATH das consolas
antigas (`%LOCALAPPDATA%\Microsoft\WinGet\Packages\Gitleaks.Gitleaks_*`).
