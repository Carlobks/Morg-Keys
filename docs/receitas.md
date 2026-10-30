# Receitas de alteração

> Numeração das secções (§N) mantida do antigo `COMO-FOI-FEITO.md`; mapa em `docs/README.md`.

## 9. Receitas de alteração

1. **Novo atalho fixo.** Acrescentar ao `keybindings:` do `config.yaml`, **fora** do bloco das apps. Testar com `glazewm command wm-reload-config` (ou `Alt+Shift+R`) e ver `glazewm\errors.log`. Acrescentar a linha à tabela `SECTIONS` de `guia/guia-logica.mjs`.
2. **Nova letra na camada `Alt+Esc`.** No modo `sistema`, copiar uma entrada e mudar a ação, sem esquecer `wm-disable-binding-mode --name sistema` e `layer-hide`. Acrescentar a letra a `sistema.html` e à tabela `SECTIONS` de `guia/guia-logica.mjs`.
3. **Novo comando chamado por uma página do Zebar.** Implementar a função no módulo `morg_*.py` da responsabilidade (ou num novo, < 500 linhas) e acrescentar o ramo no `main` do `bar_helper.py`, com teste. Alargar o `argsRegex` do `zpack.json` do widget e reiniciar o Zebar (A7, A8).
4. **Mudar a barra.** `bar.html`, `styles.css` e `icons.css`; as cores Catppuccin Mocha estão em variáveis CSS. Recarregar: fechar o Zebar e correr `zebar.exe startup`.
5. **Mudar o desenho de uma animação.** Trocar o SVG em `splash.html`. A cortina nativa já não desenha nada (só escurece), por isso não há BMP para acertar.
5b. **Nova animação** (ex.: `montanha`):
   1. **`splash.html`:** um `<svg id="montanha" class="anim" data-anim="montanha">` no lugar do `#cafe` (mesma posição e tamanho; a entrada `@keyframes entrar` aplica-se a ele também se a regra o incluir). Acrescentar `body.a-montanha #montanha` à regra que mostra o SVG escolhido e uma entrada `montanha: { first(){…}, start(){…; return setInterval(…)} }` em `ANIMS`.
   2. **`morg_config_arranque.py`:** `ANIMACOES["montanha"] = "Montanha"`. A ordem da tabela é a ordem do `Alt+Esc, E`.
   3. **Documentação:** acrescentar o nome ao comentário do `guia\arranque.txt` (modelo), ao `ValidateSet` de `-Animacao` do `instalar.ps1`, ao objeto `NOMES` de `sistema.html` e ao Tutorial.
   4. **Testar:** `splash.html?preview` no servidor `pack-preview`; depois `Alt+Esc, E` (pré-visualização) e reiniciar a sessão.
5c. **Trocar as frases do dia:** editar `Documentos\Guia de Atalhos\frases.txt` (`frase | personagem | obra`, uma por linha; a 1.ª é a do dia 1). Para o pacote, o modelo está em `guia\frases.txt`.
6. **Atualizar GlazeWM ou Zebar.** No `instalar.ps1`, tabela `$Instaladores`: novo `Url` e novo `Sha256` (o GitHub publica-o no campo `digest` de cada ficheiro do release: `gh api repos/glzr-io/glazewm/releases/tags/<versão>`). Mudar o nome do ficheiro também em `instalar-programas.ps1`. Gerar de novo `vendor\zebar-<versão>.mjs` com a versão igual (**um** ficheiro). Atualizar os `import` nas 4 páginas, o `$schema` do `zpack.json` e do `settings.json`. Ler as notas da versão para mudanças no `config.yaml`.
7. **Depois de qualquer alteração aprovada:** `scripts\testar.ps1` verde e reinstalar com o `INSTALAR.cmd` (o repositório é a fonte; não se copia nada do `~\.glzr` de volta).
