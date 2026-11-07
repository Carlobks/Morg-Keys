# Jogos em ecrã inteiro com o GlazeWM (2026-11-01)

**Pergunta:** porque é que um jogo em ecrã inteiro fica em janela e depois minimizado com o Morg Keys ligado
(relato do dono, 2026-10-25), e como se joga sem desinstalar?

**Estado:** pesquisa feita, **nada validado ainda**. Tudo o que vem de fóruns e issues fica como hipótese até ser
provado num jogo real neste PC (secção "Como validar").

## Fontes (lidas a 2026-11-01)

**GlazeWM** (versão instalada: 3.10.1):
- [Issue #699](https://github.com/glzr-io/glazewm/issues/699), aberta: num jogo em ecrã inteiro "nativo" (não o sem
  bordas), o jogo faz alt+tab sozinho e minimiza-se, mesmo sem outras apps abertas. Os utilizadores dizem que só
  resolve **pôr cada jogo na lista `ignore`** ou **pausar o GlazeWM** enquanto se joga.
- [Issue #858](https://github.com/glzr-io/glazewm/issues/858), fechada na v3.7.0: uma janela na lista `ignore`
  continua a receber os atalhos do GlazeWM (ex.: Alt+1 muda de workspace a meio do jogo). A resposta foi o comando
  novo `wm-toggle-pause`, que pausa a gestão das janelas **e** os atalhos (menos o da própria pausa).
- [Issue #833](https://github.com/glzr-io/glazewm/issues/833), aberta: o ecrã inteiro (F11, vídeos, jogos) não
  funciona em muitas apps; um utilizador diz que o problema desapareceu quando trocou os **cantos arredondados**
  do GlazeWM por cantos retos (`corner_style`).
- [Issue #729](https://github.com/glzr-io/glazewm/issues/729), aberta: pedido para o GlazeWM pausar sozinho quando
  deteta uma janela em ecrã inteiro. Ainda não existe.
- [Issue #92](https://github.com/glzr-io/glazewm/issues/92), aberta: jogos em "ecrã inteiro sem bordas" ficam por
  baixo da barra de tarefas; o autor do GlazeWM não sabe a causa.
- Notas de lançamento: a v3.8.0 fez o ecrã inteiro tapar a barra de tarefas e corrigiu a pausa (os comandos ainda
  corriam pausados); a v3.10.0 trouxe "Improved handling of fullscreen & maximized windows"
  ([PR #1298](https://github.com/glzr-io/glazewm/pull/1298)).
- **Código lido** (v3.10.1):
  - `packages/wm/src/traits/window_getters.rs` (PR #1298): o GlazeWM passa uma janela a "fullscreen" quando a
    moldura dela **ultrapassa** a área do workspace; mantém-na assim enquanto a cobrir;
  - `packages/wm/src/commands/window/ignore_window.rs`: `ignore` tira a janela da árvore do GlazeWM (deixa de a
    arrumar), mas não lhe tira os atalhos (confirma a #858).

**Omarchy / Hyprland** (repositório `basecamp/omarchy`, ramo `quattro`, ficheiros `default/hypr/apps/*.lua`):
- o Hyprland, que é o compositor, aceita o pedido de ecrã inteiro do próprio jogo. O Omarchy só acrescenta regras
  por app: o Steam a flutuar e com `idle_inhibit = "fullscreen"` (não suspende em ecrã inteiro), o RetroArch
  sempre em ecrã inteiro, e o Battle.net a flutuar;
- no Windows não há compositor que o Morg Keys controle: o GlazeWM é um programa por cima do Windows, por isso a
  solução do Hyprland não se copia.
- [Wiki do Hyprland, Window Rules](https://wiki.hypr.land/Configuring/Basics/Window-Rules/): as regras por janela
  (`fullscreen`, `content = "game"`, `immediate` para menos atraso).

**Outros:** uma pesquisa geral (Reddit, fóruns) não deu nenhuma solução específica para o GlazeWM. Há relatos de
jogos SDL que se minimizam ao perder o foco (variável `SDL_VIDEO_MINIMIZE_ON_FOCUS_LOSS`), noutros gestores de
janelas, só como analogia.

## O que se viu no Morg Keys (lido no repositório, sem jogo)

- `config.yaml`: `initial_state: 'tiling'` (uma janela nova entra no mosaico e é redimensionada);
  `window_effects` com borda e `corner_style: small_rounded` em **todas** as janelas; `hide_method: 'cloak'`;
  `state_defaults.fullscreen.shown_on_top: false`.
- Já existe `Alt+Shift+P` = `wm-toggle-pause` (linha 362).
- Os atalhos do Morg Keys são quase todos com **Alt** (Alt = Super): num jogo, Alt+1…9, Alt+W/Q (fecha a janela!),
  Alt+F, etc. chegam ao GlazeWM antes do jogo.
- A barra do Zebar é `zOrder: normal` e nunca pede o foco; os painéis (`top_most`) estão escondidos fora de uso.
- Os ajudantes Python só mexem nas janelas do Zebar e no arranque (restauro do `layout.json`), não em janelas novas.

## Hipóteses (por validar)

1. **H1 (a mais provável, pela #699):** um jogo em ecrã inteiro **exclusivo** (DirectX/Vulkan) entra no mosaico, o
   GlazeWM redimensiona-o ou mexe-lhe no foco, e o Windows tira-o do modo exclusivo e minimiza-o.
2. **H2 (pela #833):** os cantos arredondados e a borda que o GlazeWM põe na janela do jogo (atributos do DWM)
   estragam o ecrã inteiro.
3. **H3:** os atalhos com Alt colidem com as teclas do jogo (não explica a minimização, mas estraga o jogo).

## Como validar (com o dono, num jogo real)

Para cada jogo (um em ecrã inteiro exclusivo e um sem bordas), anotar o que acontece em cada passo:
1. com o Morg Keys como está: abrir o jogo em ecrã inteiro e, com o jogo aberto, ler daqui
   `glazewm query windows` (só leitura) para saber o processo, a classe e o estado da janela;
2. com o GlazeWM pausado antes de abrir o jogo (`Alt+Shift+P`): o ecrã inteiro funciona? (testa H1/H2/H3 juntas);
3. sem pausa, com uma regra `ignore` só para o processo do jogo: funciona? (testa H1);
4. sem pausa e sem `ignore`, com `corner_style` desligado: funciona? (testa H2).

## Requisito do dono (2026-11-01)

"Eu gosto de poder usar os atalhos quando o jogo está aberto; o meu único problema é ele ficar minimizado." Por
isso **a pausa (`wm-toggle-pause`) fica de fora**: desliga os atalhos. O caminho a validar é o `ignore`, que tira o
jogo da arrumação do GlazeWM e deixa os atalhos a funcionar (o comportamento descrito na #858). O passo 2 do
"Como validar" deixa de ser preciso.

## O que se mediu com um jogo aberto (2026-11-01, Baldur's Gate 3)

`glazewm query windows` (só leitura), com o jogo aberto em ecrã inteiro e "travado em modo janela":
- processo `bg3_dx11`, classe `SDL_app`, estado `minimized`, título `Baldur's Gate 3 (1894x979) - (DX11)`;
- o executável fica em `…\Steam\steamapps\common\Baldurs Gate 3\bin\`, lançado pelo `LariLauncher` (mesma pasta);
- **1894×979 é o tamanho da área do mosaico** (1896×1018), não o do ecrã (1920×1080, 1536×864 a 125 %): o GlazeWM
  arrumou a janela ao abrir e o jogo adotou esse tamanho. Confirma a H1 quanto ao tamanho; a minimização fica
  por explicar;
- o **cliente da Steam** (`steamwebhelper`) também tem a classe `SDL_app`: uma regra por essa classe apanhá-lo-ia;
- o GlazeWM 3.10.1 só reconhece uma janela nas regras por **processo, classe ou título** (`WindowMatchConfig` em
  `packages/wm-common/src/parsed_config.rs`); as regras correm em `manage`, `focus` e `title_change`; não há
  forma de usar a pasta do executável;
- `glazewm sub --events window_managed` avisa de cada janela nova que o GlazeWM passa a arrumar;
- bibliotecas neste PC: só a da Steam (`steamapps\libraryfolders.vdf`); em `steamapps\common` há também
  ferramentas (Godot Engine, wallpaper_engine, PalServer, Steamworks Shared).
- **Não validado:** a afirmação de que os jogos SDL se minimizam ao perder o foco. O cabeçalho atual do SDL2 diz
  que `SDL_HINT_VIDEO_MINIMIZE_ON_FOCUS_LOSS` é falso por omissão, e não se sabe que versão do SDL o BG3 usa.

## Correções possíveis (por validar)

1. Uma regra `ignore` por processo (`bg3_dx11`): certa, mas jogo a jogo.
2. Uma regra por classe dos motores comuns (`SDL_app`, `UnityWndClass`, `UnrealWindow`): parcial, e a `SDL_app`
   apanha a Steam.
3. Uma lista automática dos `.exe` das bibliotecas de jogos (Steam primeiro), gerada ao instalar e no
   `Alt+Shift+R`: a regra existe antes de o jogo abrir. Pede exceções para as ferramentas.
4. Um ajudante que reage ao `window_managed` e ignora as janelas de `.exe` nas pastas de jogos: atua depois de o
   GlazeWM já ter arrumado a janela (o que estragou o tamanho do BG3).
5. Um atalho para ignorar a janela em foco e guardá-la na lista de jogos.
6. As apps normais em ecrã inteiro (F11, vídeos): o GlazeWM 3.10 deteta-as; a #833 aponta os cantos arredondados.
   Pede um teste próprio.

**Decisão do dono (2026-11-01):** provar primeiro com a correção 1, só para o BG3. Se resultar, fazer a 3 com a 5.
O atalho da 5 (`Alt+Shift+I`) **abre um painel** que mostra o que já foi adicionado e **pergunta o que se vai
adicionar** antes de o fazer, para não adicionar sem querer.

## 1.º teste real com o `ignore` (dono, 2026-11-01)

- **Funcionou:** o BG3 abriu em ecrã inteiro, e os atalhos funcionaram com o jogo aberto.
- **Falhou:** ao trocar de workspace, o jogo minimizou-se; ao voltar, não estava em ecrã inteiro nem na barra do
  Zebar (a barra só mostra as janelas que o GlazeWM arruma). Pela barra do Windows, voltou logo em ecrã inteiro.
- **Explicação, validada na documentação da Microsoft**
  ([DXGI overview](https://learn.microsoft.com/en-us/windows/win32/direct3ddxgi/d3d10-graphics-programming-guide-dxgi),
  "Debugging in full-screen mode", lida a 2026-11-01): um jogo em ecrã inteiro **exclusivo** larga esse modo
  sempre que a janela dele fica tapada por outra. Com um só ecrã, mostrar outro workspace tapa-o, por isso o jogo
  minimiza-se. Não é o GlazeWM; é o próprio DirectX. Com o `ignore`, o GlazeWM também não o volta a mostrar ao
  regressar ao workspace, porque não o arruma.
- **O que falta validar:** com o jogo em **"janela sem bordas"** e o GlazeWM a arrumá-lo em estado de ecrã inteiro
  (regra `set-fullscreen` em vez de `ignore`), o GlazeWM esconde-o (cloak) ao sair do workspace e mostra-o ao
  voltar, sem o DirectX largar nada. É o comportamento que o dono quer, por confirmar.
- **Conflito:** o `Alt+Shift+I` já abre o Microsoft Edge no `apps.txt` do dono; o atalho do painel dos jogos tem de
  ser outro.

## 2.º teste: janela sem bordas com `set-fullscreen` (2026-11-07)

- **O que mudou:** o `bg3_dx11` saiu do bloco `ignore` do `config.yaml` e tem uma regra própria
  `commands: ['set-fullscreen']`, pelo processo e nunca pela classe (`SDL_app` é também do `steamwebhelper`). Sem
  opções, valem os `state_defaults.fullscreen` (`maximized: false`, `shown_on_top: false`). O comando existe no
  GlazeWM 3.10.1 (`packages/wm-common/src/app_command.rs`). O teste `test_regras_de_janela.py` passou a exigir isto.
- **Pré-requisito:** o jogo em "janela sem bordas" (Definições → Vídeo → modo de ecrã); em ecrã inteiro exclusivo o
  DirectX continua a largar o ecrã quando o jogo fica tapado.
- **À espera do teste real do dono:** passos em `docs/validacao-manual.md` §11. Ainda não foi verificado em
  máquina que o jogo volta em ecrã inteiro ao regressar ao workspace.

## Conclusão (provisória)

Nada decidido antes da validação. Se o `ignore` resolver, a solução tem de ser automática: uma lista de jogos (como
o `apps.txt`) que gera as regras, ou uma regra por classe de janela dos motores mais comuns (por validar quais),
para não ter de configurar cada jogo à mão.
