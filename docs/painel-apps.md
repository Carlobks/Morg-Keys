# Painel "Apps e arranque" (Alt+Esc, C) — plano

Data: 2026-10-22. Estado: construído; verificação estática e de lógica feita; falta o teste real depois de instalar.

## Objetivo

Configurar, **sem abrir ficheiros de texto nem correr comandos**:

- os atalhos das apps (hoje: `apps.txt` + `Alt+Shift+R`);
- que apps abrem em cada workspace no arranque (hoje: `layout.json`, gravado com `Alt+Esc, G`).

Tudo por **escolher e enviar** (rato ou só teclado), num painel leve no mesmo estilo do guia (`Alt+K`) e do painel do sistema (`Alt+Esc`).

## Decisões do utilizador

| Tema | Decisão |
|---|---|
| Origem das apps | Lista **dentro do painel** com as apps do menu Iniciar e uma pesquisa (o WebView2 não recebe o caminho de ícones arrastados do Explorador). |
| Atalhos | **Teclado desenhado**: larga-se a app numa tecla → `Alt+Shift+tecla`. |
| Arranque | **10 caixas de workspace**; larga-se a app numa caixa → abre lá no arranque. O `Alt+Esc, G` continua (grava o arranjo atual e substitui o do painel). |
| Abrir | `Alt+Esc, C` (deixa de abrir o `apps.txt` no editor). |
| Aplicar | **Logo a cada envio**, com botão **Desfazer**. |
| Interação (2026-10-22) | **Sem arrastar**: escolhe-se uma app (rato, ou ↑ ↓ e Enter) e aparece "Enviar … para" com os destinos acesos; clica-se no destino ou carrega-se a letra (tecla) / número (workspace), Del tira, Esc cancela. Motivo: o Tauri do Zebar não deixa o arrastar HTML5 funcionar no Windows. |
| Âmbito v1 | Apps do menu Iniciar, Terminal / Claude Code / Explorador, e **sites** (`web:`). Programas `.bat` ficam para depois. |
| Onde | Morg Keys (depois de instalado, substitui a versão anterior neste PC). |

## Regras a seguir (do projeto)

- Estilo: Catppuccin Mocha; secções `--mantle` com título colorido em maiúsculas; ícones Nerd Font em caixinha `color-mix(cor 16%)` desenhados em `<canvas>` (`drawIcons`); teclas `kbd` escuras com contorno; animação de abrir/fechar como o guia.
- A9: **só o `bar_helper.py` mexe na visibilidade** (`panel` mostra e dá foco; a página pede `panel-hide`).
- A8: a página só corre `py.exe`/`pyw.exe` com argumentos que batam no `argsRegex`. Os pedidos com dados vão num único argumento base64url (`panel do <b64>`), para o `argsRegex` ficar fechado (`[A-Za-z0-9_-]`).
- A7/A23: widget novo no mesmo pack (`painel/apps.html`); reiniciar o Zebar depois de mudar o `zpack.json`.
- A20: Python só biblioteca padrão; saída JSON em ASCII (`ensure_ascii`), porque o stdout do `py.exe` não é UTF-8.
- A2: não arrancar GlazeWM/Zebar/boot a partir de um terminal de agente; testes reais pela tarefa agendada.
- Nunca deixar o `config.yaml`/`apps.txt` num estado inválido: cada mudança valida antes de gravar; com erro, nada muda e o painel mostra a mensagem.

## Como funciona

### Página `painel/apps.html` (widget `apps`)
- Esquerda: **Apps** (pesquisa + lista; ↑ ↓ e Enter escolhem) e, por baixo, **+ site** (endereço → item `web:`).
- Direita, em cima: **Atalhos** — teclado QWERTY de `Alt+Shift+letra` mais `Alt+Enter` e `Alt+Shift+Enter`. Teclas usadas pelo sistema aparecem bloqueadas. Cada tecla com app mostra o ícone e o nome; ✕ ao passar o rato limpa; escolher uma tecla e enviá-la para outra move.
- Direita, em baixo: **Arranque** — workspaces 1–5 e 6–10, cada um uma caixa que aceita apps; ✕ tira; escolher uma app de uma caixa e enviá-la para outra move.
- Rodapé: estado ("Guardado", erros) e dica. Cabeçalho: título, dica, pesquisa, **Desfazer**, ✕.
- Pré-carregado escondido com o Zebar (como o guia); `Esc`, ✕ ou clicar fora fecham.

### `bar_helper.py`
- `panel` / `panel-hide`: mostrar com foco / esconder (como `guide`).
- `panel state`: JSON com atalhos (`apps.txt`), teclas bloqueadas (`config.yaml`) e apps por workspace (`layout.json`).
- `panel apps`: lista do menu Iniciar (`Get-StartApps`), guardada também em cache para o `apps-apply` ser rápido.
- `panel do <b64>`: uma operação (`key`, `unkey`, `ws-add`, `ws-del`, `ws-move`). Guarda um passo de desfazer, aplica (`apps-apply` sem janelas de erro) e devolve o novo estado.
- `panel undo`: repõe o passo anterior (até 20).
- `layout.json` ganha, por entrada, `label` e `launch` (como abrir). Entradas do painel cujo processo não se sabe à partida aprendem-no no primeiro arranque (a janela nova que aparece depois de abrir a app). `layout-save` (`Alt+Esc, G`) mantém `label`/`launch` das apps que já conhecia.

### Ligações
- `zpack.json`: widget `apps` + permissões; `settings.json`: pré-carregar `apps`.
- `config.yaml`: `Alt+Esc, C` → sair da camada, esconder o painel do sistema, `panel`.
- `sistema.html` e `guia.html`: "C — Apps e arranque".
- Documentação: `docs/` (arquitetura, armadilhas, receitas), `Tutorial.html`, `LEIA-ME.txt`, `README.md`.

## Verificação
1. Estática: AST dos `.ps1`, `compile()` do Python, JSON válido, `argsRegex` contra os argumentos reais.
2. Lógica Python testada com cópias temporárias de `apps.txt`/`layout.json`/`config.yaml` (sem GlazeWM).
3. Página aberta no navegador (modo `file:`, dados de exemplo) para ver o visual e testar escolher/enviar com rato e teclado.
4. Teste real pelo utilizador depois de instalar (tarefa agendada / reinício).
