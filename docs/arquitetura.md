# Arquitetura e funcionamento

> Numeração das secções (§N) mantida do antigo `COMO-FOI-FEITO.md`; mapa em `docs/README.md`.

## 2. Arquitetura

```
Início de sessão
  └─ Tarefa agendada "GlazeWM (arranque)"  (pyw.exe -I bar_helper.py boot)
       └─ bar_helper.py boot  ── o "orquestrador"
            ├─ lê arranque.txt (animação + programas .bat)
            ├─ janela nativa preta com o 1.º quadro da animação (arranque/cafe.bmp) — cobre tudo no 1.º instante
            ├─ zebar.exe start-widget-preset omarchy-catppuccin/splash  (animação + lista de progresso)
            ├─ zebar.exe startup     → barra (bar), guia (guia) e painel (sistema), todos do pack omarchy-catppuccin
            ├─ ShellExecute glazewm.exe  (gestor de janelas; lê ~/.glzr/glazewm/config.yaml)
            ├─ por cada "bat = …": pythonw bat_tray.py <bat> [endereço] [nome]  (escondido, ícone na bandeja)
            ├─ repõe apps de ~/.glzr/layout.json nos seus workspaces
            └─ espera 3 s sem mudanças (máx. 60 s) → o splash sai → a cortina preta sai

Em uso
  GlazeWM (atalhos)  ──shell-exec──▶ pyw.exe -I bar_helper.py <comando>
  Zebar (páginas HTML) ──shellExec──▶ py.exe/pyw.exe -I bar_helper.py <comando> | claude_usage.py
  Claude Code ──statusLine──▶ ~/.claude/statusline.py ──escreve──▶ ~/.claude/rate_limits.json ──lido por──▶ claude_usage.py
```

Peças:
- **GlazeWM 3.10.1**: gestor de janelas em mosaico (Rust). Instalado em `C:\Program Files\glzr.io\GlazeWM\`, com a CLI em `cli\glazewm.exe`.
- **Zebar 3.3.1**: widgets em HTML/JS dentro de WebView2 (Tauri). Vem no mesmo instalador e fica em `C:\Program Files\glzr.io\Zebar\zebar.exe`.
- **Python 3**: só biblioteca padrão. Corre **sempre** pelo lançador `C:\Windows\py.exe` (com consola, quando a página precisa da saída) ou `C:\Windows\pyw.exe` (sem janela), e sempre com `-I` (modo isolado).
- **`bar_helper.py`**: o único "programa" nosso (ponto de entrada). Só tem a lista de subcomandos (docstring do topo) e o `main`; o trabalho está nos módulos `morg_*.py` da mesma pasta, um por responsabilidade (tabela abaixo). Como é chamado com `py -I`, junta a sua pasta ao `sys.path` (o `-I` não o faz).

## 3. Mapa de ficheiros

Tudo vive em `%USERPROFILE%\.glzr\`. O pacote guarda os modelos em `2-configuracao\glzr\`, com a mesma estrutura.

| Ficheiro | Função |
|---|---|
| `glazewm\config.yaml` | Config do GlazeWM: aparência, workspaces 1–10 e `S` (scratchpad), regras de janelas, modos (`resize`, `sistema`) e atalhos. O bloco entre `# >>> apps:` e `# <<< apps <<<` é **gerado** por `apps-apply`; não editar à mão. |
| `zebar\settings.json` | `startupConfigs`: que widgets o `zebar startup` abre (barra, guia, painel). O splash **não** está aqui de propósito: só o `boot` o abre. |
| `zebar\omarchy-catppuccin\` | O **único pack** do Zebar: barra na raiz, guia e painel em `guia\`, ecrã de arranque em `arranque\`, cliente do Zebar em `vendor\`. O Zebar só serve ficheiros de dentro da pasta do pack (ver §7), por isso todas as páginas partilham o mesmo `vendor\`. |
| ↳ `zpack.json` | Cinco widgets (os títulos das janelas são `Zebar - omarchy-catppuccin / <widget>`, que o `bar_helper.py` procura):<br>• `bar`: 100%×30px, topo, `zOrder: normal`. Permissões: `py.exe` só com `claude_usage.py` ou `bar_helper.py awake status/toggle` ou `quick`.<br>• `guia` (`guia/guia.html`): 68%×85% do ecrã (≈1300×900 num 1920×1080; cabe num portátil 1366×768, com menos colunas e deslizar), centro, `top_most`. Permissão: `pyw.exe … guide-hide`.<br>• `sistema` (`guia/sistema.html`): 560×455, centro −120px. Permissão: `pyw.exe … layer-hide`.<br>• `apps` (`painel/apps.html`): 72%×74%, centro, `top_most`, `focused: false`. Permissões: `py.exe … panel (state|apps|undo|do <base64url>)` e `pyw.exe … panel-hide`.<br>• `splash` (`arranque/splash.html`): 100%×100%, `top_most`, `transparent: true`. Permissão: `pyw.exe … splash-ready`.<br>`guia`, `sistema` e `apps` têm `focused: false`, porque arrancam escondidos. O Zebar junta o `includeFiles` de todos os widgets do pack. |
| ↳ `bar.html`, `styles.css`, `icons.css` | Barra. Os ícones são glifos Nerd Font da fonte `JetBrainsMono NF`. A constante `PACK` (pasta do pacote) e `PY` (`C:\Windows\py.exe`) estão no topo do script. |
| ↳ `bar_helper.py` | Ponto de entrada (ver §5): lista de subcomandos e `main`. |
| ↳ `morg_win32.py` | ctypes (user32, kernel32, dwmapi, shell32), `_NamedMutex`, foco e visibilidade das janelas (`_bring_to_front`, `_focus_webview`, `_hide_when_unfocused`). |
| ↳ `morg_processos.py` | Caminhos (`HERE`, `BAR_HELPER`, `ZEBAR`, `GLAZE_CLI`, `PYTHONW`) e lançar processos (`_shell_open`, `_popen_detached`, `_start_widget`, `_wait_for`). |
| ↳ `morg_glaze.py` | CLI do GlazeWM (`_glaze`, `_workspaces`), árvore de janelas, restaurar minimizadas. |
| ↳ `morg_acordado.py` · `morg_acoes_windows.py` | Não suspender · Win+A, bloquear, energia, saída do GlazeWM. |
| ↳ `morg_janelas_zebar.py` | Guia (Alt+K), barra (mostrar/esconder) e camada Alt+Esc. |
| ↳ `morg_arranjo.py` | `layout.json` (`LAYOUT_FILE`, `LAUNCH`, `APP_LABELS`), `layout-save`, `_restore`, `layout-restore`. |
| ↳ `morg_atalhos.py` · `morg_painel.py` | `apps.txt` → `config.yaml` (`APPS_FILE`, `GLAZE_CONFIG`) · painel Alt+Esc, C. |
| ↳ `morg_config_arranque.py` · `morg_ecra_arranque.py` · `morg_cortina.py` · `morg_animacao.py` · `morg_arranque.py` | `arranque.txt` e `ANIMACOES` · splash e `progress.json` · cortina preta nativa · Alt+Esc, E · o `boot` (`BOOT_QUIET_S = 3`, `BOOT_CAP_S = 60`). |
| ↳ `claude_usage.py` | Lê `~/.claude/rate_limits.json` e devolve JSON `{now, captured_at, five_hour, seven_day}` à barra. |
| ↳ `uncloak.ps1` | Volta a mostrar janelas que o GlazeWM deixou "cloaked" ao sair (C# via Add-Type, `IApplicationView::SetCloak`). |
| ↳ `vendor\zebar-3.3.1.mjs` | Cliente JS do Zebar, num só ficheiro (ver §7). **Uma só cópia**: a barra importa `./vendor/…`, as páginas em `guia\` e `arranque\` importam `../vendor/…`. |
| ↳ `guia\` | **Guia** (`Alt+K`) e **painel** (`Alt+Esc`), e os ficheiros que o utilizador edita. Em `Documentos\Guia de Atalhos` há uma *junction* para esta pasta. |
| ↳ `guia.html` + `guia.css` + `guia.mjs` + `guia-logica.mjs` | Guia em 4 colunas. A tabela dos atalhos (`SECTIONS`) e o HTML que a desenha estão em `guia-logica.mjs` (sem DOM; testado em `tests/guia.test.mjs`); `guia.mjs` liga o filtro e o Zebar. A secção de apps lê `apps.txt` com `fetch`. Animação a crescer a partir do café da barra. Fecha com `Esc`, ✕, clique fora (polling de `isFocused`) ou `Alt+K`. O caminho do `bar_helper.py` vem do atributo `data-helper` do `<html>` (o instalador só troca `{{HOME}}` em `.html`, não em `.mjs`). |
| ↳ `sistema.html` | Painel com as letras da camada `Alt+Esc`. **Só mostra**: quem executa as letras é o GlazeWM (modo `sistema`). |
| ↳ `apps.txt` | Lista `TECLAS = APP` editada pelo utilizador (formato no cabeçalho do próprio ficheiro). |
| ↳ `painel\apps.html` | Painel **Apps e arranque** (`Alt+Esc, C`, widget `apps`): lista das apps (especiais, sites, menu Iniciar) à esquerda; teclado desenhado (`Alt+Shift+letra`, `Alt+Enter`, `Alt+Shift+Enter`) e 10 caixas de workspace à direita. Escolher e enviar (sem arrastar: o Tauri do Zebar 3.3.1 não desliga o seu tratamento de arrastar ficheiros, que no Windows bloqueia o arrastar HTML5): clica-se numa app (ou ↑ ↓ e Enter) e depois no destino (ou letra = `Alt+Shift+letra`, 1–0 = workspace, Enter / Shift+Enter = `Alt+Enter` / `Alt+Shift+Enter`, Del = tirar, Esc = cancelar). Cada envio é um pedido `panel do …` ao `bar_helper.py`, que grava e aplica logo; enquanto corre, o painel não aceita cliques (`body.busy`). Abrir com `?preview` mostra-o com dados de exemplo (`apps-exemplo.mjs`), sem gravar nada. Ficheiros: `apps.html` (estrutura; `data-helper` como no guia), `apps.css`, `apps.mjs` (desenho e eventos), `apps-logica.mjs` (ícones, teclado, base64; sem DOM, testado em `tests/painel.test.mjs`). |
| ↳ `comum\comum.mjs` | Partilhado pelo guia e pelo painel: `esc`, `SPECIAL` (as palavras especiais do `apps.txt`), `appLabel` e `drawIcons` (ícones Nerd Font centrados, em SVG — A26). |
| ↳ `arranque\` | **Ecrã de arranque** (widget `splash`). |
| ↳ `splash.html` | As animações (SVG, em ciclo) e, por baixo, a lista de etapas lida de `progress.json` a cada 250 ms. Fecha-se sozinho com `fim`. A lista segue o estilo do guia e do painel: cartão escuro, ícone por etapa em caixinha (`iconFor(id)`: `barra`, `glazewm`, `app:<processo>`, `bat:<n>`, `fim`), e à direita o estado numa "tecla" escura (a rodar / ✓ / !). A cor (`--c` no `<body>`) é a da animação: pêssego (peach) no Café. |
| (estilo comum) | Barra, guia, painel e splash partilham o mesmo kit visual: cores Catppuccin Mocha; ícones Nerd Font em caixinhas com fundo `color-mix(cor 16%)`; teclas e estados numa caixa `#11111b` com contorno `color-mix(cor 55-60%)` e sombra de 2 px. **Os ícones são desenhados num `<canvas>`, centrados pelo desenho real** (`measureText` → `actualBoundingBox*`), em `drawIcons`/`paintIcon` (nas páginas dos painéis desenhados em SVG, ver A26). Na fonte "JetBrainsMono NF" cada ícone é mais largo do que a célula e fica desviado, e o CSS sozinho não os centra. |
| ↳ `cafe.bmp` | 1.º quadro de cada animação (Café: 280×280), desenhado pela cortina nativa (GDI) antes de o WebView2 estar pronto. Tem de ser **igual** ao 1.º quadro do SVG, no mesmo sítio (ver A21). |
| ↳ `progress.json` | Gerado em cada arranque: `{boot_id, started, animacao, preview, steps:[{id,label,state}], fim}`. **Não** vai no pacote. |
| `zebar\omarchy-catppuccin\guia\arranque.txt` | **Escolhas do arranque, editáveis pelo utilizador** (visível em `Documentos\Guia de Atalhos`). `animacao = cafe` e uma linha `bat = CAMINHO \| ENDEREÇO \| NOME` por programa; endereço e nome opcionais. Lido por `_arranque_cfg()` em cada arranque. No pacote vai o modelo `scripts\arranque-modelo.txt` (com `{{ANIMACAO}}` e sem `.bat`). |
| `zebar\omarchy-catppuccin\bat_tray.py` | Corre um `.bat` escondido (`cmd /c`, na pasta do `.bat`, sem consola, saída em `~\.glzr\arranque\<nome>.log`), com ícone na bandeja. Um processo por `.bat` (mutex `Local\MorgBatTray_<sha1 do caminho>`). |
| `arranque\` (em `~\.glzr`) | Registos (`<nome>.log`) dos programas `.bat`. Também é um bom sítio para guardar os próprios `.bat` (ex.: `iniciar.bat` com `cd /d "<pasta do projeto>"` + `npm run dev`), apontados no `arranque.txt`. |
| `layout.json` | Que app abre em que workspace no arranque. Cada entrada: `workspace`, `process`, `title_hash` (gravados com `Alt+Esc, G`) e, nas que vêm do painel, `label`, `value` (a app escolhida) e `launch` (`{file, args}` para ShellExecute). Uma app do menu Iniciar cujo processo não se sabe à partida fica sem `process` até ao primeiro arranque, que o aprende. **Não** vai no pacote. |
| `instalacao.json`, `instalacao.log` | Escritos pelo instalador; o desinstalador usa o `.json` para repor o que estava. |
| `~\.claude\statusline.py` | statusLine do Claude Code. Escreve `rate_limits.json` de forma atómica. |

## 4. O arranque (`bar_helper.py boot`) em detalhe

1. **Prioridade normal.** A tarefa agendada corre com `Priority 4`; além disso, `SetPriorityClass(NORMAL)`. Com a prioridade por omissão das tarefas (7), o arranque era lento. O instalador só aceita uma tarefa antiga que não consiga substituir se tiver `Priority 4` e nenhum atraso no gatilho.
2. **Cortina preta nativa** (`_BlackCover`). É uma janela Win32 `top_most`, com o título `Morg Keys arranque`, que pinta a imagem da animação escolhida em `arranque.txt` (tabela `ANIMACOES` em `morg_config_arranque.py`) ao centro (x 50%, y `ANIM_CY` = 38%) e esconde o cursor. Aparece em menos de 1 s, antes de haver WebView2. O GlazeWM ignora-a por uma regra de título. **Abre-se antes de importar os outros módulos:** com `boot`, o `bar_helper.py` só importa `morg_config_arranque` e `morg_cortina` e chama `abrir_cedo` (prioridade normal + cortina); depois importa o resto, e o `boot()` usa essa cortina (`morg_cortina.CORTINA_CEDO`). Com o disco a frio, cada ficheiro lido antes da cortina é tempo de ambiente de trabalho à vista.
3. **Mutex `Local\MorgBootRunning`.** O `layout-restore` dos `startup_commands` do GlazeWM vê o mutex e cede a vez ao `boot`.
4. **Splash.** O `boot` corre `zebar start-widget-preset --pack omarchy-catppuccin --widget-name splash --preset default`. A página desenha-se transparente por cima da cortina, igual ao BMP e no mesmo sítio. Depois chama `splash-ready`, que faz `SetEvent Local\MorgSplashReady`, e só então a cortina fecha: preto sobre preto, sem corte. Se o evento não chegar em 20 s, segue na mesma.
5. **`zebar startup`.** Abre os `startupConfigs` no mesmo Zebar: barra, guia escondido e painel escondido.
6. **GlazeWM** com `os.startfile` (ShellExecute; ver armadilha A1). Espera pela IPC (`glazewm query workspaces`) e pela janela da barra, e depois volta a pôr o splash por cima (`_splash_to_top`).
7. **Bandeja do Windows pronta** (`Shell_TrayWnd`). Para cada linha `bat =` de `arranque.txt`, lança `bat_tray.py` fora do job (ver A4) e põe uma linha no splash. Se o `.bat` não existe, a linha fica "falhou".
8. **Repõe o `layout.json`.** Abre o que não está aberto e move cada janela para o seu workspace; o casamento é por processo, mais hash do título. Cada app aparece na lista do splash e fica "feita" quando está no sítio.
9. **Espera que assente.** Sai quando a assinatura `(id, título)` de todas as janelas não muda durante `BOOT_QUIET_S` (3 s) e cada `.bat` com endereço local responde na sua porta (`_url_port`). Os `.bat` sem endereço contam como prontos logo que arrancam. Limite: `BOOT_CAP_S` (60 s).
10. **Foco certo** por baixo do ecrã. Depois escreve `fim` em `progress.json`. O splash anima a saída e fecha-se; se não o fizer em 8 s, recebe `WM_CLOSE`. A cortina fecha e o foco é reposto outra vez.

O registo do último arranque fica em `zebar\omarchy-catppuccin\.layout-restore.log`.

## 5. Como funciona cada funcionalidade

- **Atalhos de janelas e workspaces.** São comandos nativos do GlazeWM no `config.yaml` (secções comentadas `--- Janelas ---`, `--- Workspaces ---`, etc.). Os workspaces 1–5 têm `bind_to_monitor: 0` e `keep_alive: true`, por isso aparecem sempre na barra. `toggle_workspace_on_refocus: true` faz do `Alt+º` um mostra/esconde do scratchpad `S`.
- **Camada `Alt+Esc`.** É o `binding_mode` `sistema`. `Alt+Esc` liga o modo e corre `layer-show` (mostra `sistema.html`). Cada letra faz: ação → `wm-disable-binding-mode --name sistema` → `layer-hide`. `Esc`, `Enter` e `Alt+Esc` só saem.
- **Guia `Alt+K`.** O widget `guia` arranca escondido com o Zebar (`guide-ensure-hidden` garante isso). O comando `guide` alterna a visibilidade e dá foco real: `AttachThreadInput` + `SetFocus` em `Chrome_RenderWidgetHostHWND`, sem simular teclas. Há um filtro de autorrepetição: segurar `Alt+K` abre uma só vez, com tempo por `GetTickCount64` e um mutex. **Só o helper mexe na visibilidade.** O estado de visibilidade do Tauri não acompanha o Win32, e ter dois donos causava fechos sozinhos.
- **Café (não suspender).** `awake toggle` lança `awake-hold`, um processo `pythonw` que chama `SetThreadExecutionState(ES_CONTINUOUS|ES_SYSTEM_REQUIRED|ES_DISPLAY_REQUIRED)` e espera pelo evento `Local\OmarchyAwakeStop`. Está "ligado" se o mutex `Local\OmarchyAwakeAlive` existir. Ao sair do GlazeWM, `after-exit` desliga-o.
- **Som e Wi-Fi na barra.** Clicar no som envia `Win+A` por `SendInput` (`quick`). O Wi-Fi abre `ms-availablenetworks:`.
- **Minimizadas.** A barra lista as janelas minimizadas (dados do provider `glazewm` do Zebar); um clique faz `toggle-minimized` + foco. `Alt+Shift+M` corre `restore-min`.
- **Disposição.** `layout-save` (`Alt+Esc, G`) grava `layout.json`. `layout-restore` (nos `startup_commands`, quando não há `boot`) e o `boot` repõem. Os dicionários `LAUNCH` e `APP_LABELS` em `morg_arranjo.py` dizem como abrir e como chamar cada processo conhecido.
- **Painel Apps e arranque** (`Alt+Esc, C`). O `bar_helper.py panel` mostra o widget `apps` com foco (como o guia); a página pede tudo ao helper com `py.exe` e recebe JSON em ASCII:
  - `panel state`: atalhos (`apps.txt`), teclas bloqueadas (`_fixed_bindings` do `config.yaml`) e entradas do `layout.json`;
  - `panel apps`: lista do menu Iniciar (`Get-StartApps`, ~1,2 s), guardada em `.start-apps.json` (6 h) para o `apps-apply` do painel não a pedir de novo;
  - `panel do <base64url de um JSON>`: `key` (com `from` = mover), `unkey`, `ws-add`, `ws-move`, `ws-del`. Antes de cada uma guarda um passo em `.panel-undo.json` (até 20). As mudanças de tecla reescrevem só a linha dessa tecla no `apps.txt` e correm `_apps_apply_core`; com erro repõem o ficheiro e devolvem a mensagem (nada muda);
  - `panel undo`: repõe `apps.txt`/`layout.json` do último passo e volta a aplicar.

  No arranque, `_restore` abre as entradas com `launch` por ShellExecute (`_shell_open`): uma por janela em falta. As que não têm `process` ficam com a primeira janela nova que aparecer (até 20 s), e o processo aprendido é gravado. `layout-save` (`Alt+Esc, G`) substitui o arranjo, mas mantém `launch`/`label`/`value` das apps que já conhecia (uma entrada antiga por janela).
- **Apps (`apps.txt` → atalhos).** `apps-apply` (`Alt+Shift+R`) segue estes passos:
  1. Lê `apps.txt`.
  2. Valida cada linha: tem de começar por `Alt`, sem `Ctrl`, sem teclas repetidas, sem colidir com atalhos fixos do `config.yaml`.
  3. Resolve a app, por esta ordem: palavras especiais (`terminal`, `claude-code`, `explorador`), `web:` (dá `chrome --app=URL`), caminho `.exe`, e por fim o nome do menu Iniciar via `Get-StartApps` (dá `explorer "shell:AppsFolder\<AppID>"`).
  4. Reescreve o bloco entre os marcadores e corre `wm-reload-config`.

  Com qualquer erro **não muda nada** e mostra uma MessageBox. Com `--skip-missing` (o instalador usa-o), as apps que não existem ficam comentadas em `apps.txt`, com a nota `# (não encontrada neste PC)`.
- **Uso do Claude.** O plano só expõe a percentagem real pelo campo `rate_limits` da **statusLine** do Claude Code. Estimar a partir de tokens dava números errados e foi abandonado. O `statusline.py` grava `rate_limits.json`; a barra pergunta ao `claude_usage.py` a cada 30 s (`USAGE_EVERY_MS`). Mostra `5h X% · sem Y% · ↺ tempo`, esbatido se o dado tiver mais de 15 min. Clicar abre `claude.ai/settings/usage`.
- **Sair do GlazeWM** (`Alt+Esc, Q`). Os `shutdown_commands` matam o Zebar e correm `on-exit`. Este lança `after-exit` fora do job (ver A4), que espera o GlazeWM terminar, desliga o café e corre `uncloak.ps1`.
- **Animações do arranque.** Por agora há uma: `cafe` (chávena com vapor). O mecanismo está pronto para mais (receita 5b). A escolha está em `arranque.txt`; o `boot` passa-a ao splash dentro de `progress.json` (`animacao`).
  - **Em `splash.html`:** cada animação é um `<svg class="anim" data-anim="nome">` mais uma entrada no objeto JS `ANIMS`, com `first()` (pôr o 1.º quadro, igual ao BMP) e `start()` (o ciclo; devolve o `setInterval`).
  - **No arranque:** o `<body>` recebe a classe `a-<nome>`, que mostra só esse SVG e ajusta as cores da lista.
  - **`Alt+Esc, E`:** corre `bar_helper.py animacao tap` e **não** sai da camada. Tocar passa à seguinte (ordem da tabela `ANIMACOES`) e grava-a com `_set_animacao()`; o painel (`sistema.html`) lê `arranque.txt` a cada 200 ms enquanto está aberto e mostra "Animação: X". Segurar mostra a escolhida: o Windows repete a tecla (1.ª repetição ~0,25-1 s depois, as seguintes a cada ~33 ms), e cada repetição volta a correr o comando. Duas chamadas a menos de `ANIM_REPEAT_MS` (150 ms) = segurar. Como a pressão e a 1.ª repetição já trocaram, repõe-se a animação de antes da pressão (4.º campo de `.anim-tap`). Depois espera que as repetições parem (tecla largada), sai da camada (`wm-disable-binding-mode`, `layer-hide`) e corre `animacao_preview()`. Sair da camada só depois de largar evita que as repetições cheguem à app em foco.
  - **`animacao next` / `animacao <nome>`** (linha de comandos) trocam e mostram logo. Esta escreve um `progress.json` com `preview: true` e etapas de exemplo, abre o widget e marca `fim` ao fim de ~5 s. Não faz nada durante um arranque real (mutex `Local\MorgBootRunning`).
- **Programas `.bat` ao iniciar** (`bat_tray.py`). Cada `bat =` de `arranque.txt` corre escondido, com ícone na bandeja (`Shell_NotifyIconW`) e o menu [Abrir no navegador] / Ver registo ao vivo / Reiniciar / Parar-Iniciar / Fechar. O ícone é o do Node.js se o `.bat` falar em npm/node; senão, o do `cmd`.
  - **Com endereço local:** "a correr" = a porta responde. Isto também reconhece um servidor arrancado fora daqui. Parar mata a árvore que lançou **e** quem escuta na porta (`Get-NetTCPConnection` → `taskkill /T /F`).
  - **Sem endereço:** "a correr" = o processo que lançou está vivo.
  - Volta a pôr o ícone se o Explorador reiniciar (`TaskbarCreated`).
  - Exemplo de uma linha: `bat = C:\Projetos\site\iniciar.bat | http://localhost:3000 | Servidor do site`.
