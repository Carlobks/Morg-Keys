# Ferramentas de teste e verificação para este projeto (outubro de 2026)

Pesquisa de 2026-10-23 (versões do PyPI/npm/PowerShell Gallery nesse dia). Estado desta máquina: `py` = Python
3.11.9 (não há `python` no PATH), sem coverage.py/pytest; Node v24.14.1 (a LTS mais recente é a 24.22.1);
PowerShell 5.1 com Pester 3.4.0 (antigo). **Nada disto é distribuído com o Morg Keys: só desenvolvimento.**

## Python
| Ferramenta | Versão | Prós | Contras |
|---|---|---|---|
| unittest + unittest.mock | biblioteca padrão | já instalado; mocks de ctypes/subprocess | asserções mais verbosas |
| pytest | 9.1.1 (2026-06-19), Python ≥3.10 | fixtures, parametrize, mensagens melhores; corre testes unittest | dependência extra |
| `trace` | biblioteca padrão | sem instalar | só linhas, sem ramos, sem limiar mínimo |
| coverage.py | 7.17.0 (2026-10-22), Python ≥3.11 | linhas **e ramos**, `fail_under` (sai com código 2), `exclude_also` | dependência de desenvolvimento |
Padrão recomendado: **injeção de dependências** (`user32=`, `run=` com o valor real por omissão; o teste passa
um falso). coverage.py: no 3.11 usa o motor em C (`sys.monitoring` só a partir do 3.12).
Fontes: https://pypi.org/project/pytest/ · https://pypi.org/project/coverage/ ·
https://coverage.readthedocs.io/en/latest/config.html · https://docs.python.org/3.11/library/trace.html

## JavaScript (páginas do Zebar)
- `node:test` estável desde o Node 20; a **cobertura continua experimental no Node 24**
  (`--experimental-test-coverage`, limiares `--test-coverage-lines/branches/functions`, sai com 1 abaixo).
  `mock.module` é "early development". https://nodejs.org/docs/latest-v24.x/api/test.html
- Vitest 5.0.5 (2026-10-15): cobertura v8/istanbul e limiares, mas puxa muitas dependências npm.
- Jest 30.5.2: ESM nativo menos direto; não compensa aqui.
- DOM: separar a **lógica pura em módulos ES** e testá-la sem DOM; jsdom 30.1.3 / happy-dom 21.0.4 só se for
  mesmo preciso (não reproduzem as APIs do Zebar/Tauri).
- **Playwright 1.64.1 + WebView2** (oficial): `WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS=--remote-debugging-port=9222`
  + `chromium.connectOverCDP(...)`. https://playwright.dev/docs/webview2 ·
  https://learn.microsoft.com/en-us/microsoft-edge/webview2/how-to/webdriver . Exige arrancar o Zebar com a
  variável (só o utilizador pode — Regra n.º 1) e abre uma porta local: só em sessões de teste.

## PowerShell 5.1
- **Pester 6.2.0** (2026-09-09): corre em Windows PowerShell 5.1 e PS 7.4+; cobertura com
  `New-PesterConfiguration` (`CodeCoverage.Enabled`, `CoveragePercentTarget`, 75 % por omissão).
  Instala ao lado do 3.4.0: `Install-Module Pester -MinimumVersion 6.2.0 -Scope CurrentUser -Force -SkipPublisherCheck`.
  https://pester.dev/docs/introduction/installation · https://pester.dev/docs/usage/code-coverage
- PSScriptAnalyzer 1.25.0 (lint): `Install-Module PSScriptAnalyzer -Scope CurrentUser`.

## Testes de mutação (mais fortes do que cobertura)
| Ferramenta | Versão | Windows | Veredicto |
|---|---|---|---|
| mutmut | 3.8.0 | precisa de WSL ("fork") | não prático |
| cosmic-ray | 8.7.0 | "OS Independent", não confirmado | talvez |
| StrykerJS | 10.1.1 | tap-runner deve servir para node:test (sem exemplo oficial) | ocasional |
Só para módulos pequenos e críticos, de vez em quando.

## Ponta a ponta no Windows
- WinAppDriver e Appium Windows Driver: **abandonados** — evitar.
- pywinauto 0.6.9 (2025) com manutenção irregular; FlaUI obriga a projeto C#.
- Mais barato: Python + ctypes (`SendInput`, `GetForegroundWindow`) + `glazewm query` + capturas
  (System.Drawing, processo **DPI-aware**). Só na sessão real do utilizador, com o ambiente arrancado por ele.

## Lint e verificações estáticas
ruff 0.17.2 (Python) · Biome 2.6.2 / ESLint 10.13.0 (JS) · PSScriptAnalyzer 1.25.0 · yamllint 1.38.0 ·
check-jsonschema 0.38.2 (esquemas do Zebar v3.3.1 em draft-07). Alternativa sem dependências: script Python que
valida JSON e chaves obrigatórias.

## Um só comando e hooks
- `scripts/verificar.ps1` (PowerShell 5.1): não instala nada; sai ≠ 0 se algo falhar.
- Git: `.githooks/pre-commit` + `git config core.hooksPath .githooks`.
- Claude Code (`.claude/settings.json`): `PreToolUse` para bloquear comandos, `Stop` com exit 2 para obrigar a
  testes verdes. https://code.claude.com/docs/en/hooks

## Não verificado
Versão do Node em que entraram os limiares de cobertura; se o Pester 6 falha abaixo do alvo de cobertura
(verificar `$result.CodeCoverage` no script); cosmic-ray em Windows; StrykerJS com node:test; detalhes da
pywinauto 1.0.0b1; página do check-jsonschema.
