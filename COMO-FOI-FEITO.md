# Morg Keys: como foi feito

Documento técnico para **o TI ou um agente de IA** que tenha de instalar, manter, alterar ou refazer este ambiente sem ter acompanhado a sua construção. O guia do utilizador final é o `Tutorial.html`.

Lê-se por esta ordem:
- **§1–3**: o que é e onde está cada coisa.
- **§4**: o arranque.
- **§5**: cada funcionalidade.
- **§6**: instalar à mão.
- **§7**: como o pacote foi montado.
- **§8**: armadilhas. **Ler antes de mudar qualquer coisa.**
- **§9**: receitas de alteração.
- **§10**: verificação.

> [!WARNING]
> **Regra n.º 1 (sobretudo para agentes de IA): nunca arrancar o GlazeWM, o Zebar nem o `bar_helper.py boot` / `layout-restore` a partir de um terminal do Claude Code ou de outro agente.**
> Tudo o que eles lançarem herda o ambiente desse terminal (`CLAUDECODE`, `CLAUDE_CODE_*`, `ANTHROPIC_BASE_URL`…). As sessões do Claude Code abertas depois pelos atalhos passam a cobrar **pela API** em vez do plano, e o Windows Terminal pode ficar preso. Para confirmar se um terminal está "contaminado": `Get-ChildItem env: | ? Name -match 'CLAUDE|ANTHROPIC'` (tem de vir vazio). Formas seguras de arrancar: tarefa agendada (`Start-ScheduledTask "GlazeWM (arranque)"`), terminar a sessão do Windows, ou reiniciar. Detalhes em A2 e A22 (§8).

---

## 1. Objetivo e decisões fixas

Reproduzir no Windows 11 a experiência do **Omarchy 4** (Arch + Hyprland, por DHH). O resultado:
- janelas em mosaico conduzidas pelo teclado;
- barra no topo em **Catppuccin Mocha**;
- guia de atalhos em `Alt+K`;
- camada de sistema;
- ecrã de arranque que tapa o ambiente de trabalho até tudo estar pronto.

Projeto não oficial, inspirado no Omarchy; sem ligação ao Omarchy, à 37signals nem ao DHH.

Decisões de design, que **não se mudam sem perguntar ao mantenedor**:

| Decisão | Porquê |
|---|---|
| `Alt` faz o papel de Super. `Win` sozinho fica para o Raycast. | O Raycast já usava a tecla Win. |
| **Nunca** usar `Ctrl+Alt` em atalhos. | Em teclados PT/ES, `AltGr` = `Ctrl+Alt` e escreve `@ # € [ ]`. Os atalhos do Omarchy com Super+Ctrl foram para a camada `Alt+Esc`. |
| Foco em `Alt+setas` / `H J L`. `Alt+K` é o guia; para cima é `Alt+↑`. | Igual ao Super+K do Omarchy. `Win+setas` foi testado e rejeitado. |
| Design: bordas mauve, cantos `small_rounded`, gaps de 10px. | Escolha de design. |
| Sem transparência em `Alt+Backspace`. Sem ícone de Bluetooth na barra. Sem regras app→workspace. | As regras foram rejeitadas porque moviam popups, como o login do Gmail. |
| Reiniciar e desligar na camada, sempre com confirmação. | Evitar desligar por engano. |
| Arranque: ecrã preto com uma animação que **só sai quando tudo está pronto**, sem nada a piscar. | Não se vê o ambiente a montar-se. |
| O instalador só faz **uma pergunta**, com valor por omissão: os `.bat` a correr ao iniciar. Tudo o que é pessoal fica em `arranque.txt`. | O pacote tem de servir em qualquer PC. Um servidor local de quem usa é só mais um `.bat`. |
| Animações do arranque escolhíveis e trocáveis com uma tecla (`Alt+Esc, E`, com pré-visualização), como os temas do Omarchy. Por agora há uma: Café. | Pronto para acrescentar mais (receita 5b, §9). |
| **Um só pack do Zebar** (`omarchy-catppuccin`) com subpastas `guia\` e `arranque\`. | Uma só cópia do cliente `vendor\zebar-3.3.1.mjs` (ver §7). |

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
- **`bar_helper.py`**: o único "programa" nosso. É um ficheiro com subcomandos; a lista completa está no docstring do topo.

## 3. Mapa de ficheiros

Tudo vive em `%USERPROFILE%\.glzr\`. O pacote guarda os modelos em `2-configuracao\glzr\`, com a mesma estrutura.

| Ficheiro | Função |
|---|---|
| `glazewm\config.yaml` | Config do GlazeWM: aparência, workspaces 1–10 e `S` (scratchpad), regras de janelas, modos (`resize`, `sistema`) e atalhos. O bloco entre `# >>> apps:` e `# <<< apps <<<` é **gerado** por `apps-apply`; não editar à mão. |
| `zebar\settings.json` | `startupConfigs`: que widgets o `zebar startup` abre (barra, guia, painel). O splash **não** está aqui de propósito: só o `boot` o abre. |
| `zebar\omarchy-catppuccin\` | O **único pack** do Zebar: barra na raiz, guia e painel em `guia\`, ecrã de arranque em `arranque\`, cliente do Zebar em `vendor\`. O Zebar só serve ficheiros de dentro da pasta do pack (ver §7), por isso todas as páginas partilham o mesmo `vendor\`. |
| ↳ `zpack.json` | Cinco widgets (os títulos das janelas são `Zebar - omarchy-catppuccin / <widget>`, que o `bar_helper.py` procura):<br>• `bar`: 100%×30px, topo, `zOrder: normal`. Permissões: `py.exe` só com `claude_usage.py` ou `bar_helper.py awake status/toggle` ou `quick`.<br>• `guia` (`guia/guia.html`): 68%×85% do ecrã (≈1300×900 num 1920×1080; cabe num portátil 1366×768, com menos colunas e deslizar), centro, `top_most`. Permissão: `pyw.exe … guide-hide`.<br>• `sistema` (`guia/sistema.html`): 560×455, centro −120px. Permissão: `pyw.exe … layer-hide`.<br>• `apps` (`painel/apps.html`): 72%×74%, centro, `top_most`, `focused: false`. Permissões: `py.exe … panel (state|apps|undo|do <base64url>)` e `pyw.exe … panel-hide`.<br>• `splash` (`arranque/splash.html`): 100%×100%, `top_most`, `transparent: true`. Permissão: `pyw.exe … splash-ready`.<br>`guia`, `sistema` e `apps` têm `focused: false`, porque arrancam escondidos. O Zebar junta o `includeFiles` de todos os widgets do pack. |
| ↳ `bar.html`, `styles.css`, `icons.css` | Barra. Os ícones são glifos Nerd Font da fonte `JetBrainsMono NF`. A constante `PACK` (pasta do pacote) e `PY` (`C:\Windows\py.exe`) estão no topo do script. |
| ↳ `bar_helper.py` | Ajudante (ver §5). Constantes no topo: `GLAZE_CLI`, `ZEBAR`, `LAYOUT_FILE`, `APPS_FILE`, `BOOT_QUIET_S = 3`, `BOOT_CAP_S = 60`. |
| ↳ `claude_usage.py` | Lê `~/.claude/rate_limits.json` e devolve JSON `{now, captured_at, five_hour, seven_day}` à barra. |
| ↳ `uncloak.ps1` | Volta a mostrar janelas que o GlazeWM deixou "cloaked" ao sair (C# via Add-Type, `IApplicationView::SetCloak`). |
| ↳ `vendor\zebar-3.3.1.mjs` | Cliente JS do Zebar, num só ficheiro (ver §7). **Uma só cópia**: a barra importa `./vendor/…`, as páginas em `guia\` e `arranque\` importam `../vendor/…`. |
| ↳ `guia\` | **Guia** (`Alt+K`) e **painel** (`Alt+Esc`), e os ficheiros que o utilizador edita. Em `Documentos\Guia de Atalhos` há uma *junction* para esta pasta. |
| ↳ `guia.html` | Guia em 4 colunas. A secção de apps lê `apps.txt` com `fetch`. Animação a crescer a partir do café da barra. Fecha com `Esc`, ✕, clique fora (polling de `isFocused`) ou `Alt+K`. |
| ↳ `sistema.html` | Painel com as letras da camada `Alt+Esc`. **Só mostra**: quem executa as letras é o GlazeWM (modo `sistema`). |
| ↳ `apps.txt` | Lista `TECLAS = APP` editada pelo utilizador (formato no cabeçalho do próprio ficheiro). |
| ↳ `painel\apps.html` | Painel **Apps e arranque** (`Alt+Esc, C`, widget `apps`): lista das apps (especiais, sites, menu Iniciar) à esquerda; teclado desenhado (`Alt+Shift+letra`, `Alt+Enter`, `Alt+Shift+Enter`) e 10 caixas de workspace à direita. Arrastar e largar; cada largada é um pedido `panel do …` ao `bar_helper.py`, que grava e aplica logo. Abrir com `?preview` (ou como ficheiro) mostra-o com dados de exemplo, sem gravar nada. |
| ↳ `arranque\` | **Ecrã de arranque** (widget `splash`). |
| ↳ `splash.html` | As animações (SVG, em ciclo) e, por baixo, a lista de etapas lida de `progress.json` a cada 250 ms. Fecha-se sozinho com `fim`. A lista segue o estilo do guia e do painel: cartão escuro, ícone por etapa em caixinha (`iconFor(id)`: `barra`, `glazewm`, `app:<processo>`, `bat:<n>`, `fim`), e à direita o estado numa "tecla" escura (a rodar / ✓ / !). A cor (`--c` no `<body>`) é a da animação: pêssego (peach) no Café. |
| (estilo comum) | Barra, guia, painel e splash partilham o mesmo kit visual: cores Catppuccin Mocha; ícones Nerd Font em caixinhas com fundo `color-mix(cor 16%)`; teclas e estados numa caixa `#11111b` com contorno `color-mix(cor 55-60%)` e sombra de 2 px. **Os ícones são desenhados num `<canvas>`, centrados pelo desenho real** (`measureText` → `actualBoundingBox*`), em `drawIcons`/`paintIcon`. Na fonte "JetBrainsMono NF" cada ícone é mais largo do que a célula e fica desviado, e o CSS sozinho não os centra. |
| ↳ `cafe.bmp` | 1.º quadro de cada animação (Café: 280×280), desenhado pela cortina nativa (GDI) antes de o WebView2 estar pronto. Tem de ser **igual** ao 1.º quadro do SVG, no mesmo sítio (ver A21). |
| ↳ `progress.json` | Gerado em cada arranque: `{boot_id, started, animacao, preview, steps:[{id,label,state}], fim}`. **Não** vai no pacote. |
| `zebar\omarchy-catppuccin\guia\arranque.txt` | **Escolhas do arranque, editáveis pelo utilizador** (visível em `Documentos\Guia de Atalhos`). `animacao = cafe` e uma linha `bat = CAMINHO \| ENDEREÇO \| NOME` por programa; endereço e nome opcionais. Lido por `_arranque_cfg()` em cada arranque. No pacote vai o modelo `scripts\arranque-modelo.txt` (com `{{ANIMACAO}}` e sem `.bat`). |
| `zebar\omarchy-catppuccin\bat_tray.py` | Corre um `.bat` escondido (`cmd /c`, na pasta do `.bat`, sem consola, saída em `~\.glzr\arranque\<nome>.log`), com ícone na bandeja. Um processo por `.bat` (mutex `Local\MorgBatTray_<sha1 do caminho>`). |
| `arranque\` (em `~\.glzr`) | Registos (`<nome>.log`) dos programas `.bat`. Também é um bom sítio para guardar os próprios `.bat` (ex.: `iniciar.bat` com `cd /d "<pasta do projeto>"` + `npm run dev`), apontados no `arranque.txt`. |
| `layout.json` | Que app abre em que workspace no arranque. Cada entrada: `workspace`, `process`, `title_hash` (gravados com `Alt+Esc, G`) e, nas que vêm do painel, `label`, `value` (o que se arrastou) e `launch` (`{file, args}` para ShellExecute). Uma app do menu Iniciar cujo processo não se sabe à partida fica sem `process` até ao primeiro arranque, que o aprende. **Não** vai no pacote. |
| `instalacao.json`, `instalacao.log` | Escritos pelo instalador; o desinstalador usa o `.json` para repor o que estava. |
| `~\.claude\statusline.py` | statusLine do Claude Code. Escreve `rate_limits.json` de forma atómica. |

## 4. O arranque (`bar_helper.py boot`) em detalhe

1. **Prioridade normal.** A tarefa agendada corre com `Priority 4`; além disso, `SetPriorityClass(NORMAL)`. Com a prioridade por omissão das tarefas (7), o arranque era lento.
2. **Cortina preta nativa** (`_BlackCover`). É uma janela Win32 `top_most`, com o título `Morg Keys arranque`, que pinta a imagem da animação escolhida em `arranque.txt` (tabela `ANIMACOES` em `bar_helper.py`) ao centro (x 50%, y `ANIM_CY` = 38%) e esconde o cursor. Aparece em menos de 1 s, antes de haver WebView2. O GlazeWM ignora-a por uma regra de título.
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
- **Disposição.** `layout-save` (`Alt+Esc, G`) grava `layout.json`. `layout-restore` (nos `startup_commands`, quando não há `boot`) e o `boot` repõem. Os dicionários `LAUNCH` e `APP_LABELS` em `bar_helper.py` diz como abrir e como chamar cada processo conhecido.
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

## 6. Instalação

### 6.1 Automática

Duplo clique em `INSTALAR.cmd`, com a sessão iniciada **na conta do utilizador final**. Ele corre `scripts\instalar.ps1`, que faz:

1. **Verifica:**
   - Windows 11 (build ≥ 22000);
   - `%USERPROFILE%` sem espaços (ver A6);
   - pacote numa pasta local (um admin elevado não vê unidades de rede mapeadas);
   - se está elevado, avisa e pede confirmação.

   No fim desta etapa faz `Unblock-File` a tudo.
1b. **Pergunta** (feita depois dos passos 2 e 3, logo antes da configuração; só se não houver já um `arranque.txt` de uma instalação anterior, e sem `-SemPerguntas`/`-Animacao`/`-Bat`): em ciclo, o caminho de cada `.bat`, o endereço e o nome (Enter vazio = terminar). A animação fica `cafe` (a única, por agora).

   Cada `.bat` é validado: tem de existir e ser `.bat` ou `.cmd`, e o endereço tem de começar por `http(s)://`. Se o `.bat` usa npm/node e o Node.js não está instalado, só avisa. Sem perguntas: `-Animacao cafe` e `-Bat "caminho|endereço|nome"` (vários separados por `;`).
2. **Programas em falta.** Os instaladores **não vêm no repositório**. Para cada programa em falta, usa o ficheiro de `1-instaladores\` se lá estiver e passar na verificação; senão **descarrega-o do site oficial** para lá e verifica-o. Um ficheiro que não passe **nunca** é executado (o `.part` é apagado e a instalação para).

   | Programa | Endereço oficial | Verificação |
   |---|---|---|
   | GlazeWM + Zebar | `github.com/glzr-io/glazewm/releases/download/v3.10.1/glazewm-v3.10.1.exe` | SHA-256 fixo (§7; igual ao `digest` publicado no release do GitHub) |
   | Python 3.11.9 | `www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe` | SHA-256 fixo (§7; o MD5 bate com o publicado em python.org) |
   | VC++ 2015-2022 x64 | `aka.ms/vs/17/release/vc_redist.x64.exe` | Assinatura Authenticode válida de `O=Microsoft Corporation` (a Microsoft atualiza o ficheiro no mesmo endereço, por isso não há hash fixo) |

   Sem internet: pôr os ficheiros com os nomes de §7 em `1-instaladores\` antes de correr. Depois corre `scripts\instalar-programas.ps1` com `-Verb RunAs` (**um** UAC). Esse script instala só o que falta:

   | Programa | Argumentos |
   |---|---|
   | VC++ | `/install /quiet /norestart` |
   | GlazeWM + Zebar | `/quiet /norestart` |
   | Python 3.11.9 | `/quiet InstallAllUsers=1 Include_launcher=1 InstallLauncherAllUsers=1 PrependPath=0 Include_test=0 Include_doc=0 Shortcuts=0` |

   Depois tira entradas Run ou Startup que mencionem glaze ou zebar. O Python é para todos os utilizadores porque, com UAC de outra conta, uma instalação "por utilizador" iria para o perfil do admin.
3. **Fonte.** Copia os 4 TTF para `%LOCALAPPDATA%\Microsoft\Windows\Fonts` e regista-os em `HKCU\…\Fonts` como `JetBrainsMono NF <estilo> (TrueType)`. Depois faz `AddFontResourceW` e `WM_FONTCHANGE`. Não precisa de admin.
4. **Configuração:**
   1. Se a GlazeWM estiver a correr, faz `wm-exit`; mata o Zebar.
   2. Uma `~\.glzr` existente passa a `~\.glzr.copia-<data>`.
   2b. Fecha os ajudantes Python ainda a correr (`pythonw` com `.glzr` na linha de comandos: café, ícones dos `.bat`) com os seus filhos (`taskkill /T`). Senão a tarefa lançaria uma segunda cópia de cada `.bat`, e a pasta podia não se deixar renomear.
   3. Copia `2-configuracao\glzr` para `~\.glzr`, trocando os marcadores (ver a tabela abaixo). Escreve UTF-8 sem BOM.
   4. O `arranque.txt` recebe a animação e as linhas `bat =` respondidas (ver o passo 1b).
   5. Numa reinstalação, recupera da cópia `apps.txt`, `layout.json`, `arranque.txt` (se não houve perguntas) e a pasta `arranque\`. Aceita também a estrutura antiga (pack `guia-atalhos` separado): os ficheiros vão para `omarchy-catppuccin\guia\`. Se o `arranque.txt` recuperado tiver uma animação que já não existe, passa a `cafe`.
   6. Falha se ficar algum `{{` por substituir.
   7. Cria a junction `Documentos\Guia de Atalhos` → `~\.glzr\zebar\omarchy-catppuccin\guia`.

   | Marcador | Valor | Exemplo |
   |---|---|---|
   | `{{HOME}}` | `%USERPROFILE%` com `/` | `C:/Users/joao` |
   | `{{HOME_RE}}` | o mesmo, escapado para regex dentro de JSON | — |
   | `{{ANIMACAO}}` | nome da animação (só em `arranque.txt`) | `cafe` |
5. **Apps.** Corre `py -I bar_helper.py apps-apply --skip-missing`.
6. **Claude Code**, se existir `~\.claude` ou `~\.local\bin\claude.exe`. Copia `statusline.py`; se havia um diferente, guarda-o como `.bak`. Junta `statusLine` ao `settings.json` com um script Python, **sem mexer** numa statusLine alheia.
7. **Windows.** `HideIcons=1` (exceto com `-ManterIcones`) e barra de tarefas a esconder-se (`StuckRects3`, byte 8 = 3; exceto com `-ManterBarraWindows`). Reinicia o Explorador. Guarda os valores anteriores em `instalacao.json`.
8. **Tarefa agendada** `GlazeWM (arranque)`:
   - ação: `C:\Windows\pyw.exe -I "<HOME>\.glzr\zebar\omarchy-catppuccin\bar_helper.py" boot`;
   - gatilho: AtLogOn do utilizador;
   - principal: o próprio utilizador, Interactive, RunLevel Limited;
   - definições: sem limite de tempo, `IgnoreNew`, `Priority 4`, a correr também com bateria.
9. Arranca a tarefa, exceto com `-NaoIniciar`.

### 6.2 À mão (se o script não puder correr)

Seguir exatamente os passos de §6.1, por ordem. Os pontos críticos:
- **Os marcadores têm de ficar todos trocados.** Os `argsRegex` do `zpack.json` (um por widget) têm de bater **exatamente** com os argumentos que as páginas e o GlazeWM passam; senão o Zebar recusa o comando, em silêncio. O caminho do `bar_helper.py` está na constante `PACK` de `bar.html`, na `HELPER` de `guia.html` e `sistema.html`, e escrito diretamente na chamada `splash-ready` de `splash.html`.
- **O bloco das apps fica vazio até correr `apps-apply`.** Sem ele, `Alt+Enter` não faz nada.
- **A tarefa tem de chamar `pyw.exe … boot`.** Não pode chamar `glazewm.exe` diretamente (ver A1).

### 6.3 Desinstalação

`DESINSTALAR.cmd` → `scripts\desinstalar.ps1`, que faz:

1. Remove a tarefa.
2. Fecha o GlazeWM, o Zebar e os `pythonw` cuja linha de comandos contém `.glzr`.
3. Corre `uncloak.ps1`.
4. Repõe `HideIcons` e a barra de tarefas a partir de `instalacao.json`.
5. Tira a `statusLine` do Claude Code, só se for a nossa.
6. Remove a junction com `cmd /c rmdir` (ver A10).
7. **Move** `~\.glzr` para `~\.glzr.removido-<data>`. Nunca apaga.

Os programas ficam instalados.

## 7. Como o pacote foi montado

Os três `.exe` **não estão no repositório** (estão no `.gitignore`): o instalador descarrega-os (§6.1, passo 2). Os nomes abaixo são os que ele procura em `1-instaladores\`.

| Peça | Origem | SHA-256 |
|---|---|---|
| `GlazeWM-3.10.1-com-Zebar.exe` | `github.com/glzr-io/glazewm/releases/download/v3.10.1/glazewm-v3.10.1.exe` (o instalador oficial já traz o Zebar 3.3.1) | `469F8675F5AD1353BDA9CEDE7CBB0E320E1B9A1D5657DA709B60A51D86E95020` |
| `Python-3.11.9-amd64.exe` | `www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe` (MD5 publicado: `e8dcd502e34932eebcaf1be056d5cbcd`) | `5EE42C4EEE1E6B4464BB23722F90B45303F79442DF63083F05322F1785F5FDDE` |
| `VisualC++-Redistribuivel-x64.exe` | Microsoft (VC++ 2015-2022 x64, `aka.ms/vs/17/release/vc_redist.x64.exe`). Muda de versão no mesmo endereço. | verificado pela assinatura da Microsoft |
| `JetBrainsMonoNerdFont-{Regular,Medium,SemiBold,Bold}.ttf` (no repositório, com `OFL.txt`) | Nerd Fonts, release `JetBrainsMono.zip` | Regular `C8AF9DFD…6925F`, Medium `F7523DBC…1C76A`, SemiBold `387FD979…A40E1`, Bold `546D7F5E…0B8DA` |
| `vendor\zebar-3.3.1.mjs` | `npm i zebar@3.3.1` + `esbuild --bundle --format=esm`, num só ficheiro, para não depender de CDN. A versão tem de bater com o `zebar.exe` (3.0 não tinha `tauriWindow`). **Uma só cópia**: o Zebar só serve a cada página ficheiros de dentro da pasta do seu pack que batam com o `includeFiles` (código do Zebar 3.3.1: `asset_server.rs`, `widget_factory.rs`); por isso todas as páginas estão no mesmo pack. | `E160BB83…1929FA` |
| `cafe.bmp` | `scripts\gerar-cafe-bmp.ps1`: desenha com System.Drawing (GDI+) a mesma geometria do `<svg id="cafe">`, sem vapor, a 280×280, em BMP 24-bit, em fundo preto. Não precisa de navegador. | — |
| `2-configuracao\` | `scripts\gerar-modelos.ps1` no PC onde se mantém a configuração (ver abaixo). | — |

**Atualizar o pacote depois de mudar a configuração ativa (`~\.glzr`):** correr `scripts\gerar-modelos.ps1`. Ele:
1. confirma que todos os ficheiros da lista existem em `~\.glzr` (senão para **sem apagar nada**) e copia-os. Ficam de fora logs, ficheiros com ponto (estado), `progress.json`, `layout.json` e `__pycache__`;
2. troca a pasta do utilizador por `{{HOME}}` ou `{{HOME_RE}}` (nos `zpack.json`); o `arranque.txt` pessoal **não** vai, e em seu lugar vai `scripts\arranque-modelo.txt`;
3. esvazia o bloco das apps;
4. copia `~\.claude\statusline.py`.

**Ficheiro novo no `.glzr`?** Acrescentá-lo à lista `$files` do `gerar-modelos.ps1`.

**Validação usada:** aplicar a substituição do instalador a uma pasta temporária com o próprio utilizador. Os ficheiros saem iguais byte a byte aos ativos; só difere o bloco das apps. Depois correr `apps-apply --skip-missing` nessa cópia (com `USERPROFILE` a apontar para ela e `python.exe` direto, porque o lançador `py.exe` falha com o `USERPROFILE` trocado). O `config.yaml` resultante fica igual ao ativo, exceto as apps em falta, que ficam comentadas.

## 8. Armadilhas (cada uma custou horas)

| # | Armadilha | Consequência | Regra |
|---|---|---|---|
| A1 | O `glazewm.exe` tem `uiAccess=true` | CreateProcess, Agendador e chave Run falham com `0x800702E4` (a Run falha **em silêncio**) | Lançar só por ShellExecute (`os.startfile`, `explorer`, `Start-Process`). A tarefa chama o `boot`, que faz ShellExecute. |
| A2 | Herança de ambiente | Se o GlazeWM (ou o Zebar, ou o `boot`/`layout-restore`) for arrancado de uma sessão do Claude Code, tudo o que ele lançar herda `CLAUDECODE`, `CLAUDE_CODE_*` e `ANTHROPIC_BASE_URL`: o Claude Code aberto pelos atalhos passa a cobrar **pela API**, e o Windows Terminal pode ficar preso. Fica assim até o GlazeWM ser fechado. | Nunca arrancar estes programas a partir de um terminal do Claude Code ou de um agente. Seguro: tarefa agendada (`Start-ScheduledTask`, que corre com ambiente limpo), terminar a sessão ou reiniciar. `wm-reload-config` e `glazewm command …` são seguros (não lançam processos novos). Verificar um terminal: `Get-ChildItem env: \| ? Name -match 'CLAUDE\|ANTHROPIC'`. |
| A3 | `shell-exec` do GlazeWM | Divide nos espaços. Aspas à volta do **programa** falham (bug #1417). Nomes curtos de apps da Store (`wt`) podem falhar. | Programa sem aspas e sem espaços (`%ProgramFiles%/…` funciona; `%LOCALAPPDATA%/Microsoft/WindowsApps/wt.exe` por caminho completo). Aspas só nos **argumentos** (`pyw.exe -I "C:/…/bar_helper.py" cmd`). |
| A4 | Job object do GlazeWM | Processos lançados pelo GlazeWM morrem com ele. Os `shutdown_commands` morrem antes de terminar. | O que tem de sobreviver (`after-exit`, `awake-hold`, `bat_tray.py`) sai com `CREATE_BREAKAWAY_FROM_JOB` (`_popen_detached`). |
| A5 | `hide_method: cloak` | Ao sair ou rebentar o GlazeWM, janelas de outros workspaces podem ficar invisíveis mas "abertas" | `after-exit` corre `uncloak.ps1`. À mão: `powershell -File uncloak.ps1`. |
| A6 | Pasta do utilizador com espaços | Os atalhos `wt`/`claude-code` (programa sem aspas, A3) partem | O instalador recusa. Para suportar, seria preciso mudar esses comandos. |
| A7 | Zebar só lê pacotes (`zpack.json`) ao arrancar | Um pacote novo dá "No widget pack found" num Zebar já aberto | Depois de mudar `zpack.json`, fechar **todos** os `zebar.exe` e voltar a abrir. |
| A8 | Permissões do Zebar | `shellExec` só corre o `program` exato com argumentos que batam com `argsRegex` (âncoras `^…$`); senão falha em silêncio | Ao mudar caminhos ou acrescentar um comando, atualizar o `argsRegex` no `zpack.json` e reiniciar o Zebar (A7). |
| A9 | Visibilidade das janelas do Zebar | O estado do Tauri não acompanha o Win32: mostrar pelo JS e esconder pelo Win32 dessincroniza | Um só dono: o `bar_helper.py`. As páginas pedem (`guide-hide`, `layer-hide`, `splash-ready`); não mudam a visibilidade. |
| A10 | Junction em PowerShell 5.1 | `Remove-Item -Recurse` numa junction **apaga o conteúdo do destino** | Remover junctions só com `cmd /c rmdir "<junction>"`. |
| A11 | WebView2 a frio | Até 8 s para pintar, com um clarão branco no início | `transparent: true` nos widgets e a cortina nativa com o BMP até a página avisar (`splash-ready`). |
| A12 | `start-widget-preset` | Arranca o Zebar **só** com esse widget e ignora os `startupConfigs` | O `boot` corre a seguir `zebar startup`, que funciona com o Zebar já aberto. |
| A13 | `keep_alive` dos workspaces | Ignorado sem `bind_to_monitor` | Ambos juntos (`bind_to_monitor: 0`). |
| A14 | `toggle_workspace_on_refocus` | Também afeta o `move` (issue #1397) | Por isso o "mover para workspace N" é `move` + `focus` explícitos. |
| A15 | Regras app→workspace | Moviam popups (o login do Google ia parar a outro workspace) | Não usar. O arranque usa `layout.json`. |
| A16 | `Set-Content`/`Out-File` em PowerShell 5.1 | Escrevem com BOM ou ANSI. O Zebar e o Python rejeitam JSON com BOM. | Escrever com `[IO.File]::WriteAllText(p, t, (New-Object Text.UTF8Encoding $false))`. Os `.ps1` com acentos levam BOM (o 5.1 lê sem BOM como ANSI). |
| A17 | `$ErrorActionPreference='Stop'` + programa nativo com stderr | Em PowerShell 5.1, uma linha em stderr vira exceção | `try { & prog … 2>$null } catch {}`. |
| A18 | Atalhos com Ctrl+Alt | Roubam o AltGr (`@ # € [ ]`). O GlazeWM também rejeita atalhos com modificadores a mais carregados. | Só `Alt` e `Alt+Shift`. O `apps-apply` recusa `Ctrl`. |
| A19 | Foco depois de o Zebar abrir | A janela "Tauri App" roubava o foco | O `boot` e o `layout-restore` repõem o foco no contentor que o GlazeWM diz estar focado. |
| A20 | Python | `python.exe` do PATH pode não existir ou ser outro | Sempre `C:\Windows\py.exe`/`pyw.exe -I`: o lançador escolhe a versão instalada, e `-I` ignora o diretório atual e as variáveis `PYTHON*`. |
| A21 | Passagem cortina nativa → animação | Se o BMP da cortina não for exatamente o 1.º quadro do SVG (tamanho, posição, cores), vê-se um salto no arranque | BMP e SVG com a mesma geometria. Tamanho em `ANIMACOES`, centro a `ANIM_CY` = 38% em ambos. O 1.º quadro (`first()`) não pode ter partes animadas (o vapor do café só começa depois). |
| A22 | Testar o arranque | Chamar o `boot` a partir de um terminal de agente herda o ambiente (A2) | Para ver só a animação: `bar_helper.py animacao preview` (não arranca o GlazeWM nem apps; mas, se o Zebar estiver **fechado**, arranca-o com o ambiente herdado — só correr com o Zebar já aberto). O arranque completo só se testa terminando a sessão ou reiniciando. |
| A23 | Zebar só serve ficheiros do próprio pack | Uma página não consegue importar `../outro-pack/…`; uma junction/symlink também não serve (o caminho é resolvido antes da verificação). Ficheiro fora do `includeFiles` → 404 em silêncio. | Tudo num só pack (`omarchy-catppuccin`). Ficheiro novo que uma página precise de ler: acrescentar o padrão ao `includeFiles` de um dos widgets (o Zebar junta os de todos) e reiniciar o Zebar (A7). Os títulos das janelas dependem do nome do pack (`Zebar - omarchy-catppuccin / <widget>`): mudar o nome do pack obriga a mudar `GUIDE_TITLE`, `BAR_TITLE`, `LAYER_TITLE` e `SPLASH_TITLE` no `bar_helper.py`. |

## 9. Receitas de alteração

1. **Novo atalho fixo.** Acrescentar ao `keybindings:` do `config.yaml`, **fora** do bloco das apps. Testar com `glazewm command wm-reload-config` (ou `Alt+Shift+R`) e ver `glazewm\errors.log`. Acrescentar a linha ao `guia.html`.
2. **Nova letra na camada `Alt+Esc`.** No modo `sistema`, copiar uma entrada e mudar a ação, sem esquecer `wm-disable-binding-mode --name sistema` e `layer-hide`. Acrescentar a letra a `sistema.html` e ao `guia.html`.
3. **Novo comando chamado por uma página do Zebar.** Implementar no `bar_helper.py` (função + ramo no `main`). Alargar o `argsRegex` do `zpack.json` do widget e reiniciar o Zebar (A7, A8).
4. **Mudar a barra.** `bar.html`, `styles.css` e `icons.css`; as cores Catppuccin Mocha estão em variáveis CSS. Recarregar: fechar o Zebar e correr `zebar.exe startup`.
5. **Mudar o desenho de uma animação.** Trocar o SVG em `splash.html` e gerar de novo o BMP com o mesmo tamanho e posição (`cafe.bmp`: `scripts\gerar-cafe-bmp.ps1`). Os tamanhos estão em `ANIMACOES` e `ANIM_CY` no `bar_helper.py`. Sem isso, a passagem cortina→animação dá um salto (A21).
5b. **Nova animação** (ex.: `montanha`):
   1. **`splash.html`:** um `<svg id="montanha" class="anim" data-anim="montanha">` com posição CSS `left: calc(50% - L/2)`, `top: calc(38% - A/2)` e tamanho L×A. Acrescentar `body.a-montanha #montanha` à regra que mostra o SVG escolhido, e uma entrada `montanha: { first(){…}, start(){…; return setInterval(…)} }` em `ANIMS`. A lista fica por baixo: ajustar `body.a-montanha #list { top: … }`.
   2. **BMP:** desenhar `montanha.bmp` L×A, igual ao que `first()` mostra (copiar a ideia de `gerar-cafe-bmp.ps1`), em `omarchy-catppuccin\arranque\`.
   3. **`bar_helper.py`:** `ANIMACOES["montanha"] = ("Montanha", "montanha.bmp", L, A)`. A ordem da tabela é a ordem do `Alt+Esc, E`.
   4. **Documentação:** acrescentar o nome ao comentário de `scripts\arranque-modelo.txt`, ao `ValidateSet` de `-Animacao` do `instalar.ps1` (com duas ou mais, pode voltar a perguntar qual), ao objeto `NOMES` de `sistema.html` e ao Tutorial.
   5. **Pacote:** acrescentar o BMP à lista `$files` do `gerar-modelos.ps1` e correr esse script.
   6. **Testar:** `pyw -I bar_helper.py animacao montanha` (pré-visualização). Depois reiniciar a sessão para ver a passagem da cortina.
6. **Atualizar GlazeWM ou Zebar.** No `instalar.ps1`, tabela `$Instaladores`: novo `Url` e novo `Sha256` (o GitHub publica-o no campo `digest` de cada ficheiro do release: `gh api repos/glzr-io/glazewm/releases/tags/<versão>`). Mudar o nome do ficheiro também em `instalar-programas.ps1`. Gerar de novo `vendor\zebar-<versão>.mjs` com a versão igual (**um** ficheiro). Atualizar os `import` nas 4 páginas, o `$schema` do `zpack.json` e do `settings.json`. Ler as notas da versão para mudanças no `config.yaml`.
7. **Depois de qualquer alteração aprovada:** correr `scripts\gerar-modelos.ps1` para o pacote a levar.

## 10. Verificação (depois de instalar ou alterar)

1. Termine a sessão e volte a entrar: só ecrã preto com a animação e a lista, e depois o ambiente pronto, sem clarões.
2. A barra no topo tem ícones (não quadrados) e mostra o relógio e os workspaces.
3. `Alt+K` abre o guia e fecha com `Esc`, `Alt+K` e com um clique fora. Segurar `Alt+K` abre uma só vez.
4. `Alt+Esc` mostra o painel; `Esc` fecha. `Alt+Esc`, `I` faz aparecer o café. `Alt+Esc`, tocar `E`: o painel mostra "Animação: X" (muda quando há mais de uma). Segurar `E`: ao largar, a animação aparece uns segundos.
4b. Cada `.bat` de `arranque.txt` tem o seu ícone junto ao relógio. Com endereço, "Abrir no navegador" funciona.
5. `Alt+Enter` abre o terminal. As apps de `apps.txt` abrem com os seus atalhos.
5b. `Alt+Esc, C` abre o painel. Arrastar uma app para uma tecla livre: o atalho funciona logo. Arrastar para o workspace 3: aparece na caixa; depois de reiniciar, a app abre no 3. Desfazer volta atrás. Teclas cinzentas não aceitam apps.
6. `Alt+Esc, G`, reiniciar: as apps voltam aos seus workspaces.
7. `Alt+Esc, Q` (sair do GlazeWM): todas as janelas ficam visíveis. Para voltar, correr a tarefa `Start-ScheduledTask "GlazeWM (arranque)"`.
8. Com Claude Code: depois de uma resposta, a barra mostra `5h …% · sem …%`.

Registos: `~\.glzr\instalacao.log`, `glazewm\errors.log`, `zebar\errors.log`, `zebar\omarchy-catppuccin\.layout-restore.log`, `.uncloak.log` e `arranque\<nome>.log` (um por `.bat`).
