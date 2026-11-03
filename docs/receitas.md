# Receitas de alteração

> Numeração das secções (§N) mantida do antigo `COMO-FOI-FEITO.md`; mapa em `docs/README.md`.

## 9. Receitas de alteração

1. **Novo atalho fixo.** Acrescentar ao `keybindings:` do `config.yaml`, **fora** do bloco das apps. Testar com `glazewm command wm-reload-config` (ou `Alt+Shift+R`) e ver `glazewm\errors.log`. Acrescentar a linha à tabela `SECTIONS` de `guia/guia-logica.mjs`.
2. **Nova letra na camada `Alt+Esc`.** No modo `sistema`, copiar uma entrada e mudar a ação, sem esquecer `wm-disable-binding-mode --name sistema` e `layer-hide`. Acrescentar a letra a `sistema.html` e à tabela `SECTIONS` de `guia/guia-logica.mjs`.
3. **Novo comando chamado por uma página do Zebar.** Implementar a função no módulo `morg_*.py` da responsabilidade (ou num novo, < 500 linhas) e acrescentar o ramo no `main` do `bar_helper.py`, com teste. Alargar o `argsRegex` do `zpack.json` do widget e reiniciar o Zebar (A7, A8).
4. **Mudar a barra.** `bar.html`, `styles.css` e `icons.css`; as cores Catppuccin Mocha estão em variáveis CSS. Recarregar: fechar o Zebar e correr `zebar.exe startup`.
5. **Mudar o desenho de uma animação.** Trocar o SVG em `splash.html` e gerar de novo o BMP com o mesmo tamanho e posição (`cafe.bmp`: `scripts\gerar-cafe-bmp.ps1`). Os tamanhos estão em `ANIMACOES` e `ANIM_CY` no `morg_config_arranque.py`. Sem isso, a passagem cortina→animação dá um salto (A21).
5b. **Nova animação** (ex.: `montanha`):
   1. **`splash.html`:** um `<svg id="montanha" class="anim" data-anim="montanha">` com posição CSS `left: calc(50% - L/2)`, `top: calc(38% - A/2)` e tamanho L×A. Acrescentar `body.a-montanha #montanha` à regra que mostra o SVG escolhido, e uma entrada `montanha: { first(){…}, start(){…; return setInterval(…)} }` em `ANIMS`. A lista fica por baixo: ajustar `body.a-montanha #list { top: … }`.
   2. **BMP:** desenhar `montanha.bmp` L×A, igual ao que `first()` mostra (copiar a ideia de `gerar-cafe-bmp.ps1`), em `omarchy-catppuccin\arranque\`.
   3. **`morg_config_arranque.py`:** `ANIMACOES["montanha"] = ("Montanha", "montanha.bmp", L, A)`. A ordem da tabela é a ordem do `Alt+Esc, E`.
   4. **Documentação:** acrescentar o nome ao comentário de `scripts\arranque-modelo.txt` (e ao do `guia\arranque.txt` dos modelos), ao objeto `NOMES` de `sistema.html` e ao Tutorial. O `instalar.ps1` não precisa de mudar: aceita em `-Animacao` (e mantém numa reinstalação) qualquer animação que tenha o seu `.bmp` em `arranque\` (A39).
   5. **Pacote:** acrescentar o BMP à lista `$files` do `gerar-modelos.ps1` e correr esse script.
   6. **Testar:** `pyw -I bar_helper.py animacao montanha` (pré-visualização). Depois reiniciar a sessão para ver a passagem da cortina.
6. **Atualizar GlazeWM ou Zebar.** No `instalar.ps1`, tabela `$Instaladores`: novo `Url` e novo `Sha256` (o GitHub publica-o no campo `digest` de cada ficheiro do release: `gh api repos/glzr-io/glazewm/releases/tags/<versão>`). Mudar o nome do ficheiro também em `instalar-programas.ps1`. Gerar de novo `vendor\zebar-<versão>.mjs` com a versão igual (**um** ficheiro). Atualizar os `import` nas 4 páginas, o `$schema` do `zpack.json` e do `settings.json`. Ler as notas da versão para mudanças no `config.yaml`.
7. **Depois de qualquer alteração aprovada:** correr `scripts\gerar-modelos.ps1` para o pacote a levar.
