# Experiência 0001 — Cobertura A contra C completa

- **Estado:** planeada (2026-10-23), à espera do OK para começar.
- **Pedido do utilizador:** testar as duas opções em testes reais e escolher a melhor com base nos resultados.
- **Contexto:** `docs/pesquisa/opcoes-cobertura.md` (inventário e prós/contras) e
  `docs/pesquisa/ferramentas-de-teste.md`.

## As duas versões
- **A** — 100 % de linhas e ramos da lógica testável; a cola com o sistema (ctypes/Win32, ShellExecute,
  DOM/WebView2, processo do GlazeWM, arranque) isolada em funções finas, excluída da cobertura com o motivo
  escrito e listada em `docs/validacao-manual.md`; falsos que rebentam se o código tocar no sistema real.
- **C completa** — A + testes de contrato (argsRegex vs páginas, includeFiles, títulos, BOM, BMP/SVG) + testes
  no Windows real dentro do **Windows Sandbox** (instalar, arrancar, atalhos, foco do teclado com Playwright/CDP
  ou UI Automation, capturas DPI-aware).

## O que se mede (para cada versão)
| Medida | Como |
|---|---|
| Tempo para escrever os testes | duração de cada fase (início/fim registados; `duration_ms` dos subagentes) |
| Tempo para correr os testes | `Measure-Command` sobre o comando de testes, média de 3 corridas |
| Tokens gastos | `subagent_tokens` de cada subagente + `get_usage` antes/depois; média por tarefa |
| Erros encontrados | **reintroduzir os bugs reais** (um de cada vez, num ramo): `start` em falta no `_restore`, aprender a janela errada, `expect_ws`/desfazer, foco em `Chrome_RenderWidgetHostHWND` (A25), ícones em canvas (A26), Tutorial numa só linha (A27), crases perdidas (A28), fonte em uso (A24), tarefa criada como admin (A24), argsRegex/includeFiles errados (A8/A23), JSON com BOM (A16). Contar quais cada versão apanha. |
| Falsos alarmes | testes que falham com o código certo (instabilidade), em 5 corridas |
| Mutação (opcional) | StrykerJS/cosmic-ray num módulo pequeno, se funcionarem no Windows |
| Cobertura atingida | coverage.py (linhas e ramos), `node --test --experimental-test-coverage`, Pester 6 |

Resultados: tabela neste ficheiro, com data, versão do código (commit) e o que não foi possível medir.

## Pré-requisitos
1. Refatoração comum a A e C (feita uma só vez, antes de medir): dividir `bar_helper.py` (1982 linhas),
   `painel/apps.html` (830) e `guia/guia.html` (622) em ficheiros < 500 linhas, separar lógica de cola
   (Humble Object), injetar os acessos ao sistema. Comportamento igual; testes de caracterização primeiro.
2. Ferramentas: Pester 6.2.0 e PSScriptAnalyzer 1.25.0 **instalados** (utilizador). **Por instalar:**
   coverage.py e ruff (o pip falhou: "from versions: none" no PowerShell e resposta cortada do PyPI na Bash —
   repetir; o PyPI responde) e Biome 2.6.2 (foi parar ao `package.json` pessoal e foi desfeito, A29 —
   criar `package.json` no repositório primeiro).
3. Para C: ativar o **Windows Sandbox** (administrador + reinício; feito pelo utilizador) e confirmar se o
   GlazeWM (uiAccess) e o Zebar/WebView2 funcionam lá dentro.
4. Comando único `scripts/testar.ps1` (ou `verificar.ps1`) e os 3 hooks aprovados.

## Riscos e o que pode não dar para validar
GlazeWM com uiAccess no Sandbox; Zebar a aceitar `WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS`; StrykerJS com
`node --test`; cosmic-ray no Windows. Se algo não der, regista-se aqui com a evidência.
