# CLAUDE.md — Morg Keys

Windows 11 conduzido pelo teclado ao estilo Omarchy: GlazeWM 3.10.1 + Zebar 3.3.1 (páginas HTML em WebView2)
+ ajudantes Python 3 (só biblioteca padrão) + instalador PowerShell 5.1. Documentação completa: `docs/README.md`.

## Regra n.º 1 — nunca arrancar o ambiente a partir daqui
- IMPORTANT: Não corra `glazewm.exe`, `zebar.exe`, `bar_helper.py boot|layout-restore` nem `animacao` com o
  Zebar fechado: herdam `CLAUDE*`/`ANTHROPIC_BASE_URL` deste terminal (A2). Peça ao utilizador para usar a
  tarefa agendada, ou use `Start-ScheduledTask "GlazeWM (arranque)"`; abra `.cmd` só via `explorer.exe`.
- Pode correr: `glazewm command …` (incl. `wm-exit`, `wm-reload-config`), leituras de ficheiros e registos.

## Antes de cada fase
- Escreva um plano curto: objetivo, como, o que NÃO fazer, como validar. Espere o OK em trabalho grande,
  irreversível ou que mexa no PC do utilizador.
- Releia as regras deste ficheiro e as armadilhas em `docs/armadilhas.md` que tocam no que vai mexer.
- Pesquise antes de implementar algo novo; guarde a pesquisa em `docs/pesquisa/<topico>.md` e no índice.

## Testes (obrigatórios)
- Corra tudo com um comando: `powershell -File scripts/testar.ps1` (Python unittest + `node --test` + Pester).
- Escreva o teste antes do código e confirme que falha; depois implemente até ficar verde.
- Depois de corrigir um bug, deixe um teste de regressão que falhe com o código antigo (mostre as duas corridas).
- Cubra 100 % das linhas e ramos da lógica testável. Isole a cola com o sistema (ctypes/Win32, WebView2,
  GlazeWM, arranque) em funções finas, exclua-a da cobertura com o motivo escrito, e liste-a em
  `docs/validacao-manual.md` com o passo para a verificar à mão.
- Nunca apague, desligue nem enfraqueça um teste para ficar verde.
- Não diga "feito" sem mostrar a saída dos testes. O que não puder validar, diga-o e demonstre como se valida.

## Código
- Mantenha cada ficheiro abaixo de 500 linhas (alvo 200–300) e cada função pequena (4–20 linhas), com uma
  responsabilidade por ficheiro.
- Dê nomes únicos que digam a função; o nome deve dar menos de 5 resultados no grep. Não use `data`,
  `handler`, `helper`, `utils`, `manager`, `tmp`, `info` soltos.
- Preserve todos os comentários ao refatorar; atualize-os se o código mudar, nunca os apague em silêncio.
- Python: chame sempre `C:\Windows\py.exe -I` / `pyw.exe -I`; não existe `python` no PATH.
- PowerShell: guarde `.ps1` em UTF-8 **com** BOM; escreva JSON/YAML/HTML com UTF-8 **sem** BOM (A16).
- Em substituições em massa, use Python com `assert` de "exatamente 1 ocorrência" (A27).
- Não misture mudança de estrutura e de comportamento no mesmo commit.

## Documentação (obrigatória)
- Registe cada decisão em `docs/decisoes/NNNN-titulo.md` (contexto, decisão, consequências; nunca reutilize
  números; marque "substituída por").
- Registe cada problema encontrado e a lição em `docs/armadilhas.md` (A1, A2, …) com a regra para o evitar.
- Atualize `docs/README.md` (índice) quando criar um `.md`. Mantenha este ficheiro com no máximo 100 linhas:
  detalhe vai para `docs/`.

## Commits e publicação
- Faça commits pequenos, só com os testes verdes, com `Co-Authored-By` do modelo.
- Peça confirmação antes de `git push`, de publicar ou de mexer em tarefas, registo ou ficheiros do utilizador.
- Corra `scripts/gerar-modelos.ps1` só depois de comparar com `~\.glzr` (apaga `2-configuracao`).

## Arquitetura (detalhe em `docs/arquitetura.md`)
- `2-configuracao/glzr/` → copiado para `~\.glzr` pelo instalador (marcadores `{{HOME}}`, `{{HOME_RE}}`).
  - `glazewm/config.yaml`: atalhos, modos `sistema`/`resize`, bloco de apps gerado por `apps-apply`.
  - `zebar/omarchy-catppuccin/`: o único pack do Zebar (`zpack.json`, 5 widgets).
    - `bar.html` barra · `guia/` guia (Alt+K) e painel do sistema (Alt+Esc) + `apps.txt`, `arranque.txt`
    - `painel/apps.html` painel Apps e arranque (Alt+Esc, C) · `arranque/splash.html` ecrã de arranque
    - `bar_helper.py` ajudante (subcomandos: ver docstring) · `bat_tray.py` · `vendor/zebar-3.3.1.mjs`
- `scripts/` instalar, desinstalar, gerar modelos, testar · `tests/` testes · `docs/` documentação.
- Páginas só pedem ao `bar_helper.py` (argsRegex do `zpack.json`); só o ajudante mexe na visibilidade (A9).
