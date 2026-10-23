# Opções para a regra "100 % de cobertura" neste projeto

Pesquisa e análise de código de 2026-10-23 (contagem com `ast`, função a função). Ver também
`testes-tdd-cobertura.md` e `ferramentas-de-teste.md`.

## Inventário do código
`bar_helper.py` (1982 linhas; 1621 sem vazias/comentários):
| Categoria | Linhas | % | Exemplos |
|---|---|---|---|
| Lógica pura (ou só ficheiros numa pasta temporária) | ~209 | 13 % | `_parse_key`, `_resolve_app`, `_fixed_bindings`, `_apps_entries`, `_arranque_cfg`, `_url_port`, pilha de desfazer |
| Lógica que precisa de falsos (subprocess, CLI do GlazeWM, ficheiros) | ~625 | 39 % | `_restore`, `_apps_apply_core`, `_panel_do`, `_panel_undo`, `layout_save`, `main` |
| Decisões misturadas com chamadas Win32 | ~360 | 22 % | `boot`, `animacao_tap`, `guide`, `panel_show`, `_panel_release` |
| Cola pura com o sistema | ~430 | 26 % | declarações ctypes, `_BlackCover`, `_focus_webview`, `_bring_to_front`, `_shell_open` |
Depois de separar as decisões da cola (Humble Object), a parte pura sobe para ~45–55 % e a cola fica ~20 %.
JS das páginas (~1440 linhas de script): ~22 % lógica extraível para `.mjs`, ~15 % dados, ~63 % DOM/Zebar.
PowerShell (~680 linhas): ~15–20 % testável (substituição de marcadores, `ValidarBat`, `InstaladorValido`).

## O que se pode testar no sistema real
- **GlazeWM**: uma instância por máquina (mutex global); IPC em `127.0.0.1:6123`. `glazewm query` é seguro
  (só lê); `glazewm command` mexe nas janelas reais. Sem GlazeWM de teste ao lado do do utilizador → VM/Sandbox.
- **Zebar**: uma instância; sem modo de teste; DevTools ligadas. As páginas já correm num navegador com um
  `zebar` falso (o painel tem `?preview`); `bar.html` importa o Zebar de forma estática (precisa de um falso).
- **WebView2 + Playwright** por CDP (variável `WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS` ou registo
  `HKCU\Software\Policies\Microsoft\Edge\WebView2\AdditionalBrowserArguments`): abre uma porta de controlo para
  páginas com `shellExec` → só dentro de Sandbox/VM. Não verificado se o Zebar o respeita.
- **Foco**: `GetGUIThreadInfo`, UI Automation; para "aparece mas não recebe teclas" (A25) o teste certo é CDP
  (`document.hasFocus()`) ou tecla real.
- **Windows Sandbox**: CLI `wsb` (Windows 11 24H2), sem saída do processo (resultados por pasta partilhada).
  **Não está ativo neste PC** (ativar pede administrador e reinício).

## Comparação
| | A — 100 % da lógica, cola excluída com motivo | B — 100 % literal, tudo simulado | C — A + testes reais onde der |
|---|---|---|---|
| Esforço | refatorar `bar_helper.py` (lógica/orquestração/cola), ~1500–2500 linhas de teste Python + ~400–600 JS, 2–4 sessões | ~2× A; jsdom/happy-dom | A + Sandbox + Playwright/CDP, +1–3 sessões |
| Falsa confiança | média (mutação mitiga) | **alta**: os falsos copiam a crença de quem escreveu o código | baixa a média |
| Manutenção | baixa/média | **alta**: refatorar a cola parte testes | média: o aparelho envelhece com cada versão |
Referências: Fowler desconfia de 100 %; Google 60/75/90 %; Akita > 80 % (95 % na lógica); SQLite tem 100 % de
ramos com código de teste ~590× maior (https://www.sqlite.org/testing.html).

## Que bugs reais cada opção teria apanhado
| Bug | A | B | C |
|---|---|---|---|
| `_restore` aprende a janela errada | sim (com o cenário) | = A | = A |
| `start = time.monotonic()` em falta | sim (e pyflakes) | sim | sim |
| Desfazer / `expect_ws` | sim | sim | sim |
| Foco na janela errada (A25) | não | **não** (o falso confirma o erro) | **sim** |
| Ícones em canvas (A26) | não | não | talvez (instável) |
| Tutorial numa só linha (A27) | teste de invariante (já existe) | idem | idem |
| Fonte em uso / tarefa como admin (A24) | só se alguém pensar no caso | idem | sim/talvez |
| A3, A8, A13, A16, A18, A20, A21, A23 | **sim, com testes de contrato estáticos** (zpack, config, BOM, títulos) | idem | idem |
Conclusão: B não apanharia nenhum bug a mais do que A; os caros só com o sistema real; muitas armadilhas
apanham-se com testes de contrato que nenhuma regra de cobertura pede.

## Recomendação do estudo
C mínimo: A obrigatório + testes de contrato + falsos que **rebentam** se o código tentar tocar no sistema real
(Regra n.º 1) + mutação periódica + testes reais no Sandbox só para arranque, instalação e foco, quando ativado.
Para o mutmut (WSL) o módulo de lógica não pode importar `ctypes.WinDLL`.

## Não verificado
Zebar com a variável/registo do WebView2; mocks do Tauri com o bundle do Zebar; GlazeWM com uiAccess no
Sandbox; `# pragma: no cover — motivo` com texto; cosmic-ray no Windows; post original da Google; números do
JS/PowerShell (estimativas).
