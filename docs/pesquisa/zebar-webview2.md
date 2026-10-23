# Zebar 3.3.1, Tauri e WebView2 — o que se aprendeu lendo o código

Pesquisa de 2026-10-22/23 (código-fonte em github.com/glzr-io/zebar, tag v3.3.1, lido com `gh api`).

| Tema | Facto verificado | Onde | Consequência |
|---|---|---|---|
| Ficheiros servidos | Só ficheiros **dentro da pasta do pack** e que batam com o `includeFiles` (união de todos os widgets) | `asset_server.rs` l.169–194; `widget_pack.rs` l.47–53 | Um só pack com `vendor/` partilhado (A23) |
| Raiz servida | A raiz é a pasta do pack, não a do HTML | `widget_factory.rs` l.294–299 | `../vendor/` funciona a partir de subpastas |
| Posição/tamanho | Em Windows usa pixels **físicos** | `widget_factory.rs` l.349–360 | A percentagem é do ecrã físico |
| Arrastar (DnD) | Não chama `disable_drag_drop_handler`; no Tauri v2/Windows o DnD HTML5 fica bloqueado | `widget_factory.rs` (builder) | Painel por "escolher e enviar" |
| Permissões JS | `widget.json` não concede `core:window:allow-set-focus` | `capabilities/widget.json` | `setFocus()` em JS é recusado (A25) |
| Foco do teclado | wry chama `MoveFocus(PROGRAMMATIC)` no `WM_SETFOCUS` da janela de topo; a janela `Chrome_RenderWidgetHostHWND` não trata foco | wry 0.54.3 `webview2/mod.rs` ~l.1249; Chromium `legacy_render_widget_host_win.cc` | `SetFocus` na janela de topo + `WM_SETFOCUS` (A25) |
| Ícones em canvas | Às vezes saem vazios/estragados no WebView2 (não reproduzido no Chromium) | observado no ecrã | Ícones em SVG (A26) |

Versões no Cargo.lock do Zebar 3.3.1: tauri 2.10.3, wry 0.54.3, tao 0.34.6, webview2-com 0.38.2.
Issues relacionadas: https://github.com/tauri-apps/tauri/issues/15624 ,
https://github.com/MicrosoftEdge/WebView2Feedback/issues/4147
