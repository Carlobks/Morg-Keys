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
