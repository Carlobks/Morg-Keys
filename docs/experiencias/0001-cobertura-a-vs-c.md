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

### Fase 2 — resto do plano (revisto em 2026-10-23, depois de 2a e 2b)
| Passo | O quê | Validação |
|---|---|---|
| 2b-fim | Caracterizar `animacao_tap` (tocar, segurar, repetição já tratada) com falsos de `GetTickCount64`, ficheiro `.anim-tap`, mutex e camada; depois partir em "toque" e "segurar". Passar a bateria de estragos para `scripts/estragos.py` (hoje só existe numa pasta temporária). | testes + estragos |
| 2c-1 | Capturas **antes**: painel e guia em pré-visualização no navegador interno (servidor local estático, não o Zebar — A2 não se aplica). | capturas guardadas |
| 2c-2 | `painel/apps.html` (830) → `apps.html` + `apps.css` + `apps.mjs` + funções puras num `.mjs` à parte com testes `node --test` (`appLabel`, `iconFor`, `keyHtml`, `b64`). Caminho do ajudante num atributo `data-` (o instalador só troca `{{HOME}}` em .html). | node --test; captura **depois** igual à de antes; sem erros na consola |
| 2c-3 | `guia/guia.html` (622) da mesma forma. `sistema.html` (204) fica. | idem |
| 2c-4 | `zpack.json`: `includeFiles` com `painel/*.mjs`, `painel/*.css`, `guia/*.mjs`, `guia/*.css` (A23). Verificação única (não é teste do projeto, para não antecipar a versão C): cada ficheiro que as páginas pedem está coberto pelo `includeFiles`. | script de verificação |
| 2d | Lint a bloquear no `testar.ps1`: corrigir só o que não muda comportamento (ex.: `check=False` explícito, `type="button"`); o que pode mudar o aspeto (ordem de regras CSS, `!important`) fica desligado no `biome.jsonc` **com o motivo escrito**. PSScriptAnalyzer: só erros bloqueiam; `Write-Host` do instalador é de propósito. | `testar.ps1` verde; um aviso posto de propósito faz falhar |
| Real | O utilizador reinstala (`INSTALAR.cmd`) e termina/volta a entrar na sessão (A7). Lista curta: barra (chávena, quota), Alt+K, Alt+Esc (camada e E), Alt+Esc C (escolher e enviar, Desfazer), Alt+Esc G, Alt+Shift+R, ecrã de arranque. | confirmação do utilizador |

Mudança para quem desenvolve: a pré-visualização do painel e do guia deixa de abrir como ficheiro (`file:` não
carrega módulos `.mjs`); passa a ser o servidor local `pack-preview` de `.claude/launch.json` (`py -I -m
http.server 8765` na pasta do pack) e `http://localhost:8765/painel/apps.html?preview` ou
`…/guia/guia.html?preview`. Cuidado: o navegador guarda a página em cache; depois de mudar ficheiros,
acrescentar `&v=2` (ou outro número) ao endereço.

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
| 2026-10-24 | 2b-fim | `animacao_tap` caracterizada (6 testes: tocar, segurar com repetição real de 33 ms, repetições depois do segurar, mutex ocupado, ficheiro estragado, `animacao_set`) e partida; `_apps_validar` partida (`_erro_da_tecla`, `_MenuIniciar`). Bateria passou para `scripts/estragos.py` (corre de qualquer pasta; verifica primeiro que os testes passam). 114 testes; estragos 40/40. Todas as funções ≤ 35 linhas, exceto `_BlackCover._run` (exceção com motivo, fase 4). **2b terminado.** |
| 2026-10-24 | 2c | Painel (830 linhas) e guia (622) divididos em `.html` + `.css` + `.mjs` + `*-logica.mjs` (sem DOM); o que era igual nos dois (`esc`, `SPECIAL`, `appLabel`, `drawIcons`) passou para `comum/comum.mjs`; dados de exemplo do painel em `apps-exemplo.mjs`. Caminho do ajudante em `data-helper` no `<html>`. **Prova de "igual":** em vez de comparar capturas a olho, uma impressão digital da página (atributos e texto, **todos** os estilos calculados e a caixa de cada elemento, em SHA-256) no navegador interno, a 1400×900: painel em 4 estados (inicial, app escolhida, enviada para G, filtro + seta) e guia em 2; os 6 iguais antes e depois (antes provado estável em duas corridas). Caminho do Zebar (sem `?preview`) carrega todos os módulos e falha só onde falhava (sem Zebar). `includeFiles` verificado por script único: todos os ficheiros pedidos cobertos. Testes JS: 13 (`tests/painel.test.mjs`, `tests/guia.test.mjs`); cobertura dos módulos de lógica 100 % (o resto de `comum.mjs` é o `drawIcons`, DOM). Estragos: 9 novos em `.mjs`; a 1.ª corrida deu 47/49 (dois testes meus fracos: texto sem `=` no base64; comentário sem `=` no `parseApps`), reforçados → **49/49**. Python: 110 testes (o mesmo número; o "114" do registo do 2b contava mal). Biome passou a ver o JS: 4 erros, 9 avisos (código antigo, só mudou de ficheiro) → 2d. **Cuidado aprendido:** o navegador guardou a página antiga em cache e a 1.ª medição "depois" foi da versão antiga — confirmar sempre os recursos carregados (`performance.getEntriesByType('resource')`). |
| 2026-10-24 | 2d | Lint a bloquear no `testar.ps1`. **ruff:** o repositório não tinha configuração, as regras eram as por omissão do ruff 0.17 (que mudam com a versão) → `ruff.toml` com a versão presa (`>=0.17.2,<0.18`) e E402. Corrigido sem mudar comportamento: `check=False` explícito em 10 `subprocess.run`, `ClassVar` em 4 atributos de testes, `noqa` inúteis do `bar_helper.py` (o ruff já aceita imports depois de `sys.path.insert`); exceções com motivo na própria linha: `open` sem `with` no `bat_tray.py` (o log é o stdout do `.bat`) e 2 `except Exception` (medição do arranque; resposta sempre ao painel). **Biome** (avisos contam como erros): 3 `type="button"`, 2 `forEach` com chaveta, 3 template strings; desligadas com motivo em `biome.jsonc` (o `biome.json` não aceita comentários): `noDescendingSpecificity` e `noImportantStyles` (mudam a cascata = o aspeto). **PSScriptAnalyzer:** só `Error`/`ParseError` bloqueiam (0 hoje); passa a ver também o `uncloak.ps1` do pack. Prova: um import não usado, um `let` que devia ser `const` e um `.ps1` partido → `FALHOU: Lint Python, Lint JS/CSS, Lint PowerShell` (saída 1). Impressão digital depois das mudanças: estilos e caixas iguais nos 6 estados (só a estrutura muda, pelo `type="button"`). 110 + 13 testes; os 49 estragos continuam a encontrar o texto. **Cuidado:** o `sed -i` do Git Bash trocou CRLF por LF num ficheiro inteiro (`estragos.py`); reposto — ver o `file` antes e depois. **Fase 2 terminada; falta o teste real do utilizador.** |
| 2026-10-24 | 2 (real) | O utilizador reinstalou com o `INSTALAR.cmd` (duplo clique, versão `fc256df`) e confirmou: "tudo está a funcionar bem" (barra, guia, painel e restantes atalhos com os ficheiros `.mjs`/`.css` novos servidos pelo Zebar). **Fase 2 validada.** Próximo: fase 3 (versão A no ramo `exp/a`, subagente novo). |
