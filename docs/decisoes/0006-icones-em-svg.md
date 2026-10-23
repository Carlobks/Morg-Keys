# 0006 — Ícones das páginas em SVG em vez de canvas

- **Estado:** aceite (2026-10-23)
- **Contexto:** no WebView2 do Zebar, ícones desenhados em `<canvas>` saíam às vezes vazios ou estragados
  (Energia e Reiniciar no `Alt+Esc`, teclas do painel), sem padrão e sem se reproduzir no Chromium normal.
- **Decisão:** desenhar os ícones Nerd Font como `<text>` num SVG, com a mesma centragem medida por
  `measureText`; os painéis redesenham-nos a cada abertura. Os ícones (códigos) não mudam.
- **Consequências:** A26. O `splash.html` ainda usa canvas (não deu problemas; rever se der).
