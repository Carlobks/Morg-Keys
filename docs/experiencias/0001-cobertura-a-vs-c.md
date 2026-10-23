# Experiência 0001 — Cobertura A contra C completa

- **Estado:** em curso. Plano aprovado em 2026-10-23; fase 0 e fase 1 iniciadas.
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

## Decisões do plano
1. **C construída por cima de A** (aprovado com a condição de não favorecer nenhum dos lados). Análise:
   - *Erros apanhados:* não muda. A C contém a A por definição, nas duas formas de a construir; o que se
     mede é quanto a C apanha **a mais**.
   - *Tempo e tokens:* a C conta como A + acréscimo, que é o custo real de adotar a C. Construir as duas de
     raiz mediria a mesma A duas vezes (com ruído entre as duas) e pagaria o dobro.
   - *Viés que existe nas duas formas e é controlado assim:* cada versão é escrita por um **subagente novo**,
     a partir do **mesmo commit base**, com o **mesmo modelo de pedido**; a **lista de bugs da fase 5 não é
     mostrada** a quem escreve os testes (senão escreveria testes à medida dos bugs).
2. **Enviar os commits e começar pela fase 0** (aprovado).

## Plano de execução
| Fase | O quê | Quem | Validação |
|---|---|---|---|
| 0 | Enviar os commits pendentes; instalar coverage.py e ruff; `package.json` **no repositório** + Biome (A29); comando único `scripts/testar.ps1`; os 3 hooks (bloquear arranque A2, testes antes do commit, limite de 500 linhas) | agente | cada ferramenta responde com a versão; cada hook bloqueia uma tentativa feita de propósito |
| 0 | **Ativar o Windows Sandbox** (ver abaixo) | utilizador | o programa "Windows Sandbox" abre |
| 1 | Testes de **caracterização** (fixam o comportamento atual): partes puras do `bar_helper.py` (`_panel_do`/`_panel_undo`, plano do `_restore`, herança do `layout_save`, `_apps_apply_core`) e funções JS do painel | agente | passam com o código atual e falham quando se estraga uma linha de propósito |
| 2 | **Refatoração comum**: `bar_helper.py` (1982 linhas), `painel/apps.html` (830) e `guia/guia.html` (622) divididos em ficheiros < 500 linhas, uma responsabilidade cada, cola Win32 isolada (Humble Object), comentários mantidos; `.js` novos no `includeFiles` (A23) | agente | testes da fase 1 verdes; reinstalar (com OK) e o utilizador confirma Alt+Esc C, guia e arranque |
| 3 | **Versão A** no ramo `exp/a` | subagente novo | cobertura 100 % da lógica; exclusões com motivo |
| 4 | **Versão C** no ramo `exp/c` (a partir de `exp/a`) | subagente novo | contratos + testes no Sandbox a correr |
| 5 | **Bateria de bugs reais** (lista abaixo), um de cada vez numa cópia isolada, contra a suíte A e a suíte C | agente | tabela de bugs apanhados |
| 6 | Resultados aqui; ADR 0008 com a regra de cobertura; aplicar o `CLAUDE.md` novo; juntar o ramo vencedor ao `main` | agente + OK do utilizador | — |

### Fase 2 — plano detalhado (2026-10-23)
Regra: comportamento igual; os testes da fase 1 não mudam nas asserções (só a ligação ao sistema falso);
comentários mantidos; um commit por passo, cada um com os testes verdes e a bateria de estragos.
- **2a. Dividir o `bar_helper.py` por responsabilidade** (código movido tal como está, mesmos nomes):
  `morg_win32.py` (ctypes, mutex, foco e visibilidade das janelas), `morg_processos.py` (caminhos dos
  programas, lançar processos), `morg_glaze.py` (CLI do GlazeWM, árvore, minimizadas), `morg_acordado.py`
  (não suspender), `morg_janelas_zebar.py` (guia Alt+K, barra, camada), `morg_arranjo.py` (layout.json, restauro),
  `morg_atalhos.py` (apps.txt → config.yaml), `morg_painel.py` (Alt+Esc, C), `morg_animacao.py`,
  `morg_cortina.py` (cortina preta nativa), `morg_arranque.py` (boot), `morg_acoes_windows.py`
  (Win+A, bloquear, energia, saída do GlazeWM). O `bar_helper.py` fica só com a lista de comandos e junta a sua
  pasta ao `sys.path` (com `-I` o Python não o faz). Teste novo: o ponto de entrada corre com `py -I`.
- **2b. Funções pequenas**: partir `_restore`, `boot`, `_apps_apply_core`, `_panel_do` e `main` em passos.
- **2c. JS e CSS fora do HTML**: `painel/apps.html` e `guia/guia.html` → `.html` + `.css` + `.mjs`, e as funções
  puras num `.mjs` próprio com testes `node --test` (caracterização do JS adiada da fase 1). Caminho do
  ajudante num atributo `data-` do HTML (o instalador só troca `{{HOME}}` em .html/.py/…, não em .mjs).
  `includeFiles` do `zpack.json` com os ficheiros novos (A23).
- **2d. Lint passa a bloquear** no `testar.ps1` (ruff e Biome no código; PSScriptAnalyzer só erros).
- **Validação real (utilizador)**: reinstalar com o `INSTALAR.cmd` e reiniciar a sessão (A7: o Zebar só lê o
  `zpack.json` ao arrancar); depois `docs/validacao-manual.md` §10. O agente não arranca o ambiente (A2).

### Windows Sandbox: o que é e como ativar
É um Windows descartável que abre numa janela dentro deste PC: começa sempre limpo, não vê os programas
nem as definições deste Windows e **apaga tudo ao fechar**. Serve para instalar e arrancar o Morg Keys de raiz
sem mexer no ambiente real. Vem com o Windows 11 Pro, mas vem desligado.

Ativar (uma vez, como administrador; o agente não muda definições do sistema):
1. Menu Iniciar → escrever **"Ativar ou desativar funcionalidades do Windows"** (no Windows em português do
   Brasil: "recursos do Windows").
2. Marcar **"Windows Sandbox"** (pode aparecer como "Área Restrita do Windows") → OK.
3. Reiniciar quando pedir.

Alternativa: PowerShell como administrador →
`Enable-WindowsOptionalFeature -Online -FeatureName Containers-DisposableClientVM -All`.

Estado verificado em 2026-10-23: Windows 11 Pro; hipervisor ativo (`HypervisorPresent = True`, logo a
virtualização está ligada); `WindowsSandbox.exe` ainda não existe (funcionalidade desligada).

### Onde é seguro arrancar o GlazeWM e o Zebar (correção)
Frase do plano anterior, **errada**: "o Sandbox é o único sítio onde posso arrancar o GlazeWM e o Zebar sem
risco". O certo, segundo a A2 (`docs/armadilhas.md`):
- **Seguro contra a A2 neste PC:** a tarefa agendada (`Start-ScheduledTask "GlazeWM (arranque)"`, ambiente
  limpo), abrir `.cmd` pelo `explorer.exe`, terminar a sessão ou reiniciar. Mas **mexe na sessão real do
  utilizador** (só pode haver um GlazeWM; fecha e reabre o ambiente), por isso pede OK.
- **Sandbox:** o único sítio onde se pode **instalar e arrancar de raiz, e repetir à vontade, sem tocar no
  ambiente real**. O ambiente do terminal do agente não passa para dentro (é outra máquina virtual).
  A pasta do repositório entra só em leitura.

## O que se mede (para cada versão)
| Medida | Como |
|---|---|
| Tempo para escrever os testes | duração de cada fase (início/fim registados; `duration_ms` dos subagentes) |
| Tempo para correr os testes | `Measure-Command` sobre o comando de testes, média de 3 corridas |
| Tokens gastos | tokens reportados por cada subagente + `get_usage` antes/depois; média por tarefa |
| Erros encontrados | **reintroduzir os bugs reais** (um de cada vez, numa cópia): `start` em falta no `_restore`, aprender a janela errada, `expect_ws`/desfazer, foco em `Chrome_RenderWidgetHostHWND` (A25), ícones em canvas (A26), Tutorial numa só linha (A27), crases perdidas (A28), fonte em uso (A24), tarefa criada como admin (A24), argsRegex/includeFiles errados (A8/A23), JSON com BOM (A16). Contar quais cada versão apanha. Esta lista não é mostrada aos subagentes das fases 3 e 4. |
| Falsos alarmes | testes que falham com o código certo (instabilidade), em 5 corridas |
| Mutação (opcional) | StrykerJS/cosmic-ray num módulo pequeno, se funcionarem no Windows |
| Cobertura atingida | coverage.py (linhas e ramos), `node --test --experimental-test-coverage`, Pester 6 |

Resultados: tabela neste ficheiro, com data, versão do código (commit) e o que não foi possível medir.

## Riscos e o que pode não dar para validar
- GlazeWM no Sandbox: precisa de `uiAccess` (binário assinado em pasta protegida); pode recusar arrancar.
- Zebar pode ignorar `WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS` (sem isso não há CDP para o Playwright).
- StrykerJS com `node --test` e cosmic-ray no Windows (opcionais).

Se algo não der, regista-se aqui com a evidência e a C é medida sem essa parte.

## Registo
| Data (Lisboa) | Fase | O que aconteceu |
|---|---|---|
| 2026-10-23 | — | Plano aprovado; decisão 1 (C por cima de A) com a análise de viés acima |
| 2026-10-23 | 0 | coverage 7.17.0, ruff 0.17.2, Biome 2.6.2 (no repositório); `scripts/testar.ps1` (0/1 provado); 3 hooks com 19 testes e 9 estragos apanhados; provados ao vivo. Incidentes A30 (650 processos) e A31 (hooks bloquearam tudo). Windows Sandbox instalado pelo utilizador. |
| 2026-10-23 | 1 | Testes de caracterização (base comum de A e C): `tests/sistema_falso.py` (ficheiros, GlazeWM, relógio e abridor falsos; Win32/subprocess são bombas) + 5 ficheiros, 71 testes novos (91 no total). Cobertura: `bar_helper.py` 0 % → 42 % (linhas e ramos), `claude_usage.py` 95 %. Prova por estragos: 22/22 apanhados, depois de reforçar 4 testes que deixavam escapar (aprender a janela errada, duas janelas a herdar a mesma entrada, espera mínima de 40 s, contagem das janelas antigas). **JS do painel adiado para o início da fase 2** (só 4 funções puras; o resto depende do DOM — testa-se ao passar para `.mjs`). Nota para a fase 5: estes testes são a base comum; regista-se também que bugs a base sozinha já apanha. |
| 2026-10-23 | 2a | `bar_helper.py` (1982 linhas) dividido em 14 módulos `morg_*.py` (69–319 linhas) por um script que move blocos de linhas tal como estão; o `bar_helper.py` ficou com 137 (lista de comandos + `main`). Mudanças necessárias: `sys.path.insert` da própria pasta (o `-I` não a junta) e `BAR_HELPER` no lugar de `Path(__file__)` nos relançamentos (senão o "não suspender" relançaria o módulo errado). Testes: só a ligação ao sistema falso mudou (`ModulosMorg` procura os nomes em todos os módulos; os falsos aplicam-se em todos os que os usam); 92 verdes; teste novo do ponto de entrada com `py -I` noutra pasta; estragos 23/23. **Bug antigo encontrado (não corrigido, comportamento igual):** `bar_helper.py` sem argumentos rebenta ao imprimir a ajuda num terminal cp1252 (carácter "✕") — anotado em `docs/pendentes.md`. |
| 2026-10-23 | 2b (parte) | Antes de partir o `boot` (sem testes), caracterizei-o com `ArranqueFalso` (8 testes: sequência das etapas, splash que não avisa, sem Zebar, porta que nunca responde, arranque.txt). Partidos: `boot` (6 passos), `_restore` (fases), `_apps_apply_core`, `_panel_do`, `main` (tabela `COMANDOS`, com teste que fixa cada comando). 108 testes; estragos 35/35. **Falta:** `animacao_tap` (45 linhas, sem testes: caracterizar primeiro). **Exceção com motivo:** `_BlackCover._run` (74 linhas) é cola Win32 pura que cria uma janela real por cima de tudo; divide-se na fase 4, com o teste real no Sandbox. **Incidentes:** A33 (falso alarme do hook da A2) e A34 (um teste meu chamou o `awake-hold` real; terminado, estado confirmado "off"; correção: testes de comandos dentro do `SistemaFalso`). Lição para a bateria de estragos: confirmar primeiro que os testes passam com o código certo (senão dá 100 % falso). |
