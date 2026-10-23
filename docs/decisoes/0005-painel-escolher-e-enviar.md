# 0005 — Painel "Apps e arranque": escolher e enviar, sem editar ficheiros

- **Estado:** aceite (2026-10-22/23)
- **Contexto:** o utilizador quer mudar atalhos de apps e apps do arranque por workspace sem abrir `.txt` nem
  correr comandos, no estilo do projeto, por `Alt+Esc, C`.
- **Decisão:** lista das apps do menu Iniciar dentro do painel (com pesquisa, especiais e sites); teclado desenhado
  (`Alt+Shift+letra`, `Alt+Enter`, `Alt+Shift+Enter`); 10 caixas de workspace; **escolher e enviar** com rato
  ou só teclado (o arrastar HTML5 é bloqueado pelo Tauri do Zebar); cada envio aplica logo, com **Desfazer** (até
  20, recusa se os ficheiros mudaram fora do painel); `.bat` ficam para depois.
- **Consequências:** o `bar_helper.py` ganhou `panel …`; o `layout.json` ganhou `label/value/launch` e
  aprende o processo de apps novas no 1.º arranque. Plano: `docs/painel-apps.md`.
