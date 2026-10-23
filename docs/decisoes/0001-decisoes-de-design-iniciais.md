# 0001 — Decisões de design iniciais

- **Estado:** aceite (anteriores a 2026-10-22; vindas do projeto original)
- **Contexto:** reproduzir o Omarchy 4 no Windows 11 com o teclado PT/ES e o Raycast já em uso.
- **Consequências:** estas decisões não se mudam sem perguntar ao mantenedor.

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
