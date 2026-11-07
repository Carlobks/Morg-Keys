# Arrastar janelas e abas com o GlazeWM (2026-11-03)

**Pergunta:** porque é que, ao arrastar uma janela (sobretudo uma aba do Chrome), o GlazeWM "fica louco": a janela
salta de um lado para o outro, às vezes vai para o lado certo e às vezes fica uma linha fina que não se abre? E
como se tem uma animação suave na arrumação, como no Omarchy? Relato do dono, 2026-11-03.

**Estado:** causa confirmada com o dono a 2026-11-07 (secção "Teste com o dono"); correção decidida (A, mosaico ao largar) e implementada (plano 0007, passos 7.1–7.3); falta o teste real do dono (7.4).

## Fontes (lidas a 2026-11-03)

- **[Issue #1080](https://github.com/glzr-io/glazewm/issues/1080)**, aberta pelo **autor do GlazeWM**, com a
  etiqueta "help wanted": ao arrastar uma aba do Chrome para fora, o Chrome cria uma janela nova **com o botão do
  rato ainda carregado**, e o GlazeWM tenta arrumá-la logo no mosaico; "isto causa algum tremer para a frente e para
  trás" e "seria melhor esperar pelo fim do arrastar". A tentativa dele com `GetGUIThreadInfo` (`GUI_INMOVESIZE`)
  não chegou: o Windows não marca a janela como "a ser arrastada" logo que ela aparece. **Não está resolvida na
  3.10.1** (a versão instalada).
  - Um comentário aponta um fork com binários próprios (`mcleinn/glazewm-with-multimonitor-workspaces`), que corrige
    outra coisa (arrastar ser lido como redimensionar). Fica só como referência: binários de terceiros não se
    instalam (regra SEM SEGREDOS / downloads).
- **[Issue #43](https://github.com/glzr-io/glazewm/issues/43)** (fechada, 2022): abas do Chromium voltavam à janela
  de origem quando se arrastavam para fora de uma zona; dada como corrigida na 3.4. Mostra que o problema das abas
  é antigo.
- **[Issue #636](https://github.com/glzr-io/glazewm/issues/636)** (aberta): mover e redimensionar com Alt+rato, como
  o AltSnap; sem implementação.
- **[Issue #647](https://github.com/glzr-io/glazewm/issues/647)** (fechada na 3.6): o GlazeWM passou a esconder as
  janelas por "cloaking", **sem animação**. O GlazeWM não tem animações próprias de arrumação: só liga ou desliga as
  do Windows (abrir, fechar, minimizar).
- **Código do GlazeWM 3.10.1** (lido):
  - `packages/wm/src/events/handle_window_moved_or_resized.rs`: um arrastar começa quando a janela muda de sítio
    com o botão esquerdo carregado e o cursor perto dela, e só se nenhuma outra janela estiver a ser arrastada;
  - `packages/wm/src/events/handle_window_moved_or_resized_end.rs`: uma janela do mosaico arrastada passa a
    "flutuante temporária" e, ao largar, volta ao mosaico no sítio do cursor; se não passou o limiar, volta ao
    lugar de antes;
  - `packages/wm-common/src/active_drag.rs`: o estado do arrastar.
- **Omarchy / Hyprland:** o Hyprland é o próprio compositor. As animações (`animations { … }` na configuração) e o
  arrastar (`bindm = SUPER, mouse:272, movewindow`) são dele, desenhados frame a frame. O GlazeWM corre por cima
  do Windows e só pode pedir ao Windows que mude o tamanho e o sítio das janelas, de uma vez.
- **komorebi** (outro gestor de janelas para Windows): tem animações de movimento (`animation`, `animation-fps`,
  `animation-style` na documentação da CLI). Fica como referência; trocar de gestor de janelas não está em cima da
  mesa.

## Hipóteses (por validar)

1. **Abas do Chrome (a #1080):** a janela nova da aba é arrumada no mosaico enquanto o Chrome ainda a arrasta; os
   dois lutam pela posição, e a janela salta ou fica com um tamanho estranho (a "linha fina").
2. **Janelas inteiras:** o arrastar normal do GlazeWM (flutuante temporária, largar no sítio do cursor) funciona,
   mas sem animação, por isso as outras janelas "saltam" para o lugar novo ao largar.

## Correções possíveis (por validar)

1. **Esperar pelo fim do arrastar, fora do GlazeWM:** um ajudante ouve as janelas novas
   (`glazewm sub --events window_managed`); se o botão esquerdo estiver carregado nesse momento, põe a janela a
   flutuar (`set-floating`) e, quando o botão for largado, volta a pô-la no mosaico. Precisa de um processo sempre
   a correr e de testes com o Chrome; a janela volta ao mosaico ao lado da janela em foco, não no sítio do cursor.
2. **Contribuir a correção ao GlazeWM** (a #1080 pede ajuda): é Rust, fora do repositório do Morg Keys.
3. **Animações suaves:** o GlazeWM não as tem, e o Windows não deixa um programa de fora animar a arrumação sem
   mover a janela muitas vezes por segundo. Fica como limitação conhecida.

## Como validar (com o dono)

1. Arrastar uma aba do Chrome para fora com o Morg Keys como está, e anotar o que acontece (salta? linha fina?).
2. O mesmo com o GlazeWM pausado (`Alt+Shift+P`): se o problema desaparecer, é o GlazeWM (a #1080).
3. Se a correção 1 avançar: provar com o Chrome e com outra app que arrasta abas (ex.: o Terminal do Windows).

## Teste com o dono (2026-11-07)

Gravação das janelas do GlazeWM 5 vezes por segundo (consulta `query windows`, só leitura) enquanto o dono
arrastava abas do Chrome, sem pausa:
- cada aba arrastada para fora é uma janela nova do `chrome`; aparece `floating` e, **0,24 s depois**, o GlazeWM
  já a meteu no mosaico (`tiling`), com o botão do rato ainda carregado;
- durante o arrasto o Chrome cria e destrói janelas várias vezes (mais de 15 em 37 s); cada vez o GlazeWM
  rearruma tudo (metades horizontais, verticais, três colunas e de volta);
- a "linha fina": uma janela com **244 px** de altura (`1896x244`), espremida entre duas.

Com o GlazeWM pausado (`Alt+Shift+P`), nas palavras do dono: "ficou muito melhor", e o encaixe do Windows nos
cantos funciona. **Confirma a hipótese 1 (a #1080).** A gravação com pausa não vê nada, porque o GlazeWM pausado
não arruma janelas novas.

Nota: `glazewm sub` com a saída redirecionada para um ficheiro não escreveu nada em 10 minutos (o processo estava
vivo). Para um ajudante, usar a ligação do GlazeWM em vez da linha de comandos.

**Decisão do dono (2026-11-07, "siga a recomendação"): A. mosaico ao largar.** Enquanto se arrasta, a janela nova
fica solta e nada se mexe; ao largar, entra no mosaico de uma vez.

## Como fazer a correção 1 (lido a 2026-11-07)

- **Ligação ao GlazeWM:** o `packages/wm/src/ipc_server.rs` (v3.10.1) abre um WebSocket só em
  `127.0.0.1:6123` e lê cada mensagem como os argumentos da linha de comandos (`message.split_whitespace()`).
  Responde em JSON (`ClientResponse` com `data`, `error`, `success`; `EventSubscription` com `subscription_id`).
  Um ajudante liga-se uma vez, pede `sub -e window_managed` e fica parado à espera (sem gastar CPU). O Python
  só com a biblioteca padrão não tem cliente WebSocket: são umas dezenas de linhas (aperto de mão HTTP e
  tramas com máscara, RFC 6455), testáveis sem rede.
- **Apontar a uma janela:** `command --id <uuid> <comando>` (`subject_container_id` em
  `packages/wm-common/src/app_command.rs`). `set-floating` aceita `--centered=false` (sem isso usa o
  `centered: true` do `config.yaml`) e `set-tiling` não tem opções.
- **O botão do rato:** `GetAsyncKeyState(VK_LBUTTON)` (documentação da Microsoft, lida a 2026-11-07) dá o estado
  **físico** do botão, seja qual for a janela em foco; com os botões trocados (`GetSystemMetrics(SM_SWAPBUTTON)`)
  o botão principal é o `VK_RBUTTON`. Devolve 0 quando falha (por exemplo, com uma janela de administrador em
  primeiro plano): aí o ajudante não faz nada e fica como hoje.
- **O fluxo:** chega `window_managed` → se o botão está carregado, `command --id X set-floating --centered=false`
  → vê o botão a cada 50 ms (só enquanto há um arrasto) → ao largar, `command --id X set-tiling`. Uma janela que
  o Chrome já destruiu dá erro no `set-tiling`, que se ignora.
- **Arranque e fim:** uma linha nova nos `startup_commands` do `config.yaml` (`pyw.exe -I bar_helper.py …`, como
  as outras); quando o GlazeWM fecha, a ligação cai e o ajudante sai.
- **Risco por medir:** o `window_managed` chega depois de o GlazeWM já ter arrumado a janela, por isso pode ficar
  **um** salto curto (arrumar e soltar) em vez de muitos. Mede-se no teste do dono.
