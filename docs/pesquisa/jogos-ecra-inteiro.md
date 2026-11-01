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

## Conclusão (provisória)

Nada decidido antes da validação. Se a pausa resolver, a solução mínima é um **"modo jogo"**: um atalho que pausa o
GlazeWM e esconde a barra, e que volta atrás com o mesmo atalho. Se o `ignore` resolver, pode juntar-se uma lista
automática por classe de janela dos motores mais comuns (por validar quais), para não ter de configurar cada jogo.
