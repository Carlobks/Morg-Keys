# 0007 — Foco do teclado nas páginas do Zebar pela janela de topo

- **Estado:** aceite (2026-10-23)
- **Contexto:** o painel aparecia mas não recebia teclas; o ajudante dava o foco à janela interna
  `Chrome_RenderWidgetHostHWND`, que não trata foco; `setFocus()` em JS está bloqueado pelo Zebar.
- **Decisão:** `SetFocus` na janela de topo + `WM_SETFOCUS` (o wry faz `MoveFocus` para a página); ao
  esconder, devolver o primeiro plano à janela de antes.
- **Consequências:** A25. Verificado por captura no ecrã real (abrir, escrever, Esc, reabrir, escrever).
