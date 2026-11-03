# Modal dos limites do Claude: posição, foco, gravação e desenho (2026-11-03)

**Pergunta:** como se faz um modal pequeno, colado ao ✻ da barra, onde o dono põe à mão o % das 5 h, o % da semana
e as horas de reset, sem estragar o que a statusLine escreve e sem dar à página mais privilégios do que precisa?
Pedido do dono, passou a ser a P7 a 2026-11-03.

**Estado:** pesquisa feita a partir do código do Zebar 3.3.1 e do código deste repositório. **Por validar no PC**
(posição com a escala a 125 %, foco), no teste real do fim da P7.

## Fontes (lidas a 2026-11-03)

- **Esquema do `zpack.json` do Zebar 3.3.1**
  ([`resources/zpack-schema.json`](https://github.com/glzr-io/zebar/blob/v3.3.1/resources/zpack-schema.json)):
  - `anchor` aceita `top_left`, `top_center`, `top_right`, `center_left`, `center`, `center_right`, `bottom_left`,
    `bottom_center` e `bottom_right`;
  - `zOrder` aceita `top_most`, `normal` e `bottom_most`;
  - `monitorSelection.type` aceita `all`, `primary`, `secondary`, `index` e `name`;
  - `offsetX`, `offsetY`, `width` e `height` são texto, e o esquema não diz mais nada.
- **[`widget_factory.rs`](https://github.com/glzr-io/zebar/blob/v3.3.1/packages/desktop/src/widget_factory.rs)**:
  - com `TopRight`, o canto fica em `(monitor.x + monitor_width - window_size.width, monitor.y)`, e a posição final
    é esse canto mais `offset_x` e `offset_y`;
  - os píxeis passam pelo `to_px_scaled` com a escala do monitor;
  - o `focused` só é lido na criação (`.focused(widget_config.focused)`), e não há nenhum `set_focus` depois.
- **[`common/length_value.rs`](https://github.com/glzr-io/zebar/blob/v3.3.1/packages/desktop/src/common/length_value.rs)**:
  - o padrão é `([+-]?\d+(?:\.\d+)?)(%|px)?`, por isso `-8px` é válido e um número sem unidade conta como píxeis;
  - os píxeis são multiplicados pela escala do monitor, e as percentagens não.
- **Este repositório:**
  - o `morg_painel.py` tem o `panel_show`, o `panel_hide` e o `_panel_release`, e o `morg_win32.py` tem o
    `_bring_to_front`, o `_focus_webview` e o `_hide_when_unfocused` (A25: o foco vai para a janela de topo);
  - o `claude_usage.py` só mostra uma janela com `used_percentage` numérico e `resets_at` no futuro;
  - o `~/.claude/statusline.py` grava o ficheiro inteiro, `{"captured_at", "rate_limits"}`, com um temporário e
    `os.replace`;
  - na barra, o `openWin` abre ligações com `shell-exec explorer <uri>` pelo provedor do GlazeWM, sem nenhuma
    entrada no `argsRegex`;
  - skill `desenhando-telas`.

## O que se concluiu

**Posição.** O widget `limites` usa `anchor: top_right`, `offsetX: -8px`, `offsetY: 34px` (os 30 px da barra mais
uma folga), `width: 300px`, `height: 250px`, `monitorSelection: primary` e `zOrder: top_most`. Como a barra também
está em píxeis, a escala não desalinha os dois. Fica perto do ✻, que está do lado direito da barra.

**Foco.** O padrão do painel das apps serve tal e qual, só com outro título de janela e outro ficheiro para a janela
de antes:
- o `limites` mostra o modal e, se ele já estiver aberto, esconde-o;
- guarda a janela que tinha o foco, chama o `_bring_to_front` e o `_focus_webview`, e deixa o
  `_hide_when_unfocused` como rede;
- o `limites-hide` faz o `_panel_release`.

Para não copiar código, o `_panel_release` passa a receber o ficheiro da janela de antes. Isso é uma mudança de
estrutura, num commit à parte.

**Gravação.** Ao gravar, o ficheiro passa a ter `origem: "manual"` e `captured_at` com a hora. As janelas que o modal
não muda ficam como estavam. Quando a statusLine voltar a correr no terminal, grava o ficheiro inteiro sem o campo
`origem`: os valores oficiais passam por cima dos manuais, como o dono decidiu. A troca usa um temporário na mesma
pasta e `os.replace`, como a statusLine, para a barra nunca ler meio ficheiro.

**Leitura dos campos** (decidida aqui; a lógica fica em Python e é testada):
- **hora:** `14:30` é hoje, ou amanhã se essa hora já passou;
- **tempo que falta:** combinações de `Nd`, `Nh` e `Nm` (`2h15`, `45m`, `1d5h`); um número solto depois de `h`
  conta como minutos, como no `fmtUntil` da barra;
- **dia e hora:** `qui 16:00`, com `seg`, `ter`, `qua`, `qui`, `sex`, `sáb`/`sab` e `dom`; se é hoje e a hora já
  passou, conta a próxima semana;
- a hora é a local do PC, a de Lisboa;
- **%:** um inteiro de 0 a 100, aceitando um `%` no fim; o resto é recusado com uma mensagem curta;
- **um reset vazio** mantém o anterior, se ainda estiver no futuro. Se não houver nenhum, o campo pede a hora: sem
  ela, o `claude_usage.py` não mostraria a janela, e gravar seria enganar.

**Privilégios (A9).** A página só pede `limites state`, `limites set <b64>` e `limites-hide`. A ligação para a
página de uso abre-se como na barra, pelo `shell-exec` do GlazeWM, sem nenhuma entrada nova. A barra ganha só
`bar_helper.py limites`.

**Desenho** (skill `desenhando-telas`):
- uma ação principal, "Gravar", com Enter;
- um botão secundário, "Fechar", com Esc;
- rótulos visíveis por cima de cada campo, e o erro em texto por baixo do campo, nunca só pela cor;
- o número atual como valor inicial, com `tabular-nums`;
- tamanhos em `rem`, contraste AA com as cores Catppuccin da barra, superfícies sólidas e um só contentor com borda;
- sem animação além da opacidade, e nenhuma com `prefers-reduced-motion`.

## O que não se verificou

- a posição real com a escala a 125 % e com mais de um monitor;
- se o `_focus_webview` dá o teclado ao campo logo à primeira, como no painel; a página foca o 1.º campo no evento
  `focus` da janela;
- se a aplicação de ambiente de trabalho do Claude vem a escrever o `rate_limits.json`; hoje não o escreve.
