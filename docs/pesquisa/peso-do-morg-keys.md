# Peso do Morg Keys no PC (2026-11-10)

**Pergunta:** quanto gasta o Morg Keys (CPU e memória), se o ajudante `arrastar` (plano 0007) está otimizado e o
que vale a pena otimizar na arquitetura. Pedido do dono, 2026-11-10.

**Estado:** só medição e recomendações; nada mudou. Qualquer mudança precisa de um plano próprio.

## O que se mediu (PC parado, 1 monitor, 24 núcleos, Zebar 3.3.1, GlazeWM 3.10.1)

Amostra de 30 s com `TotalProcessorTime` e memória privada de cada processo; os scripts (só leitura) ficam fora do
repositório.

| Parte | Processos | Memória privada | CPU parado |
|---|---|---|---|
| GlazeWM + watcher | 2 | 10 MB | 0 % |
| Ajudante `arrastar` | 2 (`pyw.exe` à espera + `pythonw.exe`) | 13 MB | 0 % (bloqueia no `recv` sem prazo) |
| Zebar (o próprio programa) | 1 | 55 MB | ~0 % |
| WebView2 da interface do próprio Zebar (`%LocalAppData%\com.glzr.zebar`) | 6 | ~110 MB | 0 % |
| WebView2 do pack (`%AppData%\zebar\webview-cache\omarchy-catppuccin`) | 13: browser, GPU, 2 utility, **8 renderers** | ~440 MB | ~0 % |
| **Total** | 24 | **~614 MB** | **~0,02 %** do PC |

- **Ajudante `arrastar`: está bem.** Parado não acorda nunca: fica à espera da próxima mensagem do GlazeWM. Só
  acorda de 50 em 50 ms enquanto há uma janela solta, ou seja, durante o arrastar. Os 1,5 MB do `pyw.exe` são o
  lançador oficial, que fica vivo à espera do Python. Chamar o `pythonw.exe` diretamente poupava esses 1,5 MB, mas
  o caminho muda quando o Python é atualizado. Não vale a pena.
- **Janelas do pack:** `bar`, `guia`, `sistema`, `apps` ×2 e `limites` ×2 (todas criadas no mesmo segundo do
  arranque). O `apps` e o `limites` estão **abertos duas vezes**, e cada cópia é um renderer de ~30 MB. O 8.º
  renderer não tem janela visível associada (provavelmente o que ficou do `splash`, ou um renderer de reserva do
  Chromium; não se confirmou).
  - **Causa provável:** correm dois `zebar startup` quase ao mesmo tempo, o do `bar_helper.py boot`
    (`morg_arranque.py`) e o 1.º `startup_commands` do GlazeWM. O comentário do `config.yaml` diz que "widgets já
    abertos não se duplicam", mas com os dois em corrida os últimos da lista (`apps`, `limites`) duplicam. **Não se
    verificou:** é preciso reiniciar o PC e contar as janelas.
- **Custo escondido: a chávena (`awake status`) a cada 5 s.** A barra corre
  `zebar.shellExec(py.exe -I bar_helper.py awake status)` a cada 5 s (`bar.html`, `AWAKE_EVERY_MS`), só para ver
  se existe um mutex. Medição de 10 chamadas: `py.exe` ~20 ms de CPU, mais `python.exe` ~67 ms (só ~16 ms são o
  Python vazio; o resto é importar o `bar_helper` inteiro, com `morg_acoes_windows`, `pathlib`, `re` e `ctypes` à
  cabeça no `-X importtime`).
  - Isto dá **~85 ms de CPU a cada 5 s**, ~1 s por minuto (~1,7 % de um núcleo, ~0,07 % do PC), e **1 440
    processos criados por hora** (lançador + Python), cada um visto pelo antivírus. Como os processos são curtos, a
    amostra de 30 s não os apanha.
  - O ✻ do Claude faz o mesmo de 30 em 30 s (`claude_usage.py`, que importa pouco), 2 por minuto: aceitável.
- **Temporizadores das páginas:**
  - A `sistema` tem um `setInterval` de 200 ms sempre ligado, que só testa uma classe. Na amostra, o renderer dela
    gastou 0,007 % do PC. É barato, mas acorda o processo 5 vezes por segundo.
  - A `guia`, a `apps` e a `limites` só verificam o foco (120–150 ms) enquanto estão abertas.
  - Os providers da barra (cpu e memória de 5 s, rede de 10 s, data de 1 s, bateria de 30 s) são os normais.

## Fontes (lidas a 2026-11-10)

- **[Microsoft, Performance best practices for WebView2 apps](https://learn.microsoft.com/en-us/microsoft-edge/webview2/concepts/performance)**
  (atualizada a 2026-11-02):
  - cada controlo WebView2 tem processos próprios e o custo cresce com o número de instâncias;
  - partilhar um só `CoreWebView2Environment` poupa memória;
  - "Avoid redundant WebView2 instances";
  - pôr `MemoryUsageTargetLevel = Low` nas WebViews inativas, ou `TrySuspendAsync` se puderem parar os scripts;
  - não usar WebView2 para ecrãs de arranque simples.
- **[Microsoft, ICoreWebView2_19 / MemoryUsageTargetLevel](https://learn.microsoft.com/en-us/microsoft-edge/webview2/reference/win32/icorewebview2_19)**
  e **[TrySuspendAsync](https://learn.microsoft.com/en-us/dotnet/api/microsoft.web.webview2.core.corewebview2.trysuspendasync)**:
  - "Low" mantém os scripts a correr;
  - o `TrySuspend` só serve para WebViews invisíveis e pausa os scripts;
  - não se misturam os dois.

  São APIs do programa anfitrião (o Zebar, em Rust/Tauri). Uma página do pack não as pode chamar.
- **[Chrome, Timer throttling in Chrome 88](https://developer.chrome.com/blog/timer-throttling-in-chrome-88)**: os
  temporizadores das páginas visíveis não são travados. Numa página escondida há menos de 5 minutos, correm no
  máximo uma vez por segundo; ao fim de 5 minutos, uma vez por minuto (com cadeia ≥ 5). Não se confirmou se uma
  janela do Tauri escondida com `hide()` conta como "escondida" para o Chromium.
- **[Zebar, releases](https://github.com/glzr-io/zebar/releases)**: a 3.3.1 é a última. A 3.3.0 corrigiu uma fuga de
  recursos nos providers `battery` e `media`; nenhuma nota fala de widgets duplicados.
- **[Zebar, issue #264](https://github.com/glzr-io/zebar/issues/264)** (lida através de um espelho): os widgets
  perdem objetos GDI a cada mudança de workspace (com `visible_on_all_workspaces`). Fica por medir aqui (contar os
  objetos GDI do `zebar.exe` antes e depois de 50 mudanças).

## O que não se verificou

- A causa dos widgets duplicados: precisa de um reinício e de contar as janelas.
- De quem é o 8.º renderer.
- Se as janelas escondidas do Zebar ficam com os temporizadores travados.
- A fuga de GDI da issue #264 nesta máquina.

## Conclusão: o que vale e o que não vale a pena

| Mudança | Ganho estimado | Vale? |
|---|---|---|
| Acabar com os widgets duplicados (um só `zebar startup` no arranque do PC, ou o do GlazeWM esperar pelo mutex do boot como o `layout-restore` já faz) | ~60 MB e menos 2 páginas a correr os mesmos atalhos | **Sim**, é um defeito |
| Chávena: atualizar ao clicar e quando o modo `sistema` fecha (o provider `glazewm` já avisa a barra), com uma verificação lenta de 60 s como rede; e um script pequeno só com `ctypes` em vez do `bar_helper` inteiro | De 1 440 para ~120 processos por hora; ~1 s de CPU por minuto | **Sim**, barato |
| `setInterval` de 200 ms da `sistema` → ligar só enquanto aberta | Quase nada (0,007 %) | Só se se mexer na página |
| Juntar os widgets numa só página, ou tirar os pré-carregados | ~30 MB por widget, mas abrir fica lento (o pré-carregamento existe por isso) | Não |
| Ambiente WebView2 da própria interface do Zebar (~110 MB), `MemoryUsageTargetLevel` | Só mudando o Zebar (Rust, fora deste repositório) | Não |
| Chamar o `pythonw.exe` diretamente no ajudante `arrastar` | 1,5 MB | Não |
