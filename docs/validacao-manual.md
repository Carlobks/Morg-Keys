# Validação manual

> Numeração das secções (§N) mantida do antigo `COMO-FOI-FEITO.md`; mapa em `docs/README.md`.

O que os testes automáticos não cobrem e como se verifica à mão (com o passo e o resultado esperado).

## 10. Verificação (depois de instalar ou alterar)

1. Termine a sessão e volte a entrar: só ecrã preto com a animação e a lista, e depois o ambiente pronto, sem clarões.
2. A barra no topo tem ícones (não quadrados) e mostra o relógio e os workspaces.
3. `Alt+K` abre o guia e fecha com `Esc`, `Alt+K` e com um clique fora. Segurar `Alt+K` abre uma só vez.
4. `Alt+Esc` mostra o painel; `Esc` fecha. `Alt+Esc`, `I` faz aparecer o café. `Alt+Esc`, tocar `E`: o painel mostra "Animação: X" (muda quando há mais de uma). Segurar `E`: ao largar, a animação aparece uns segundos.
4b. Cada `.bat` de `arranque.txt` tem o seu ícone junto ao relógio. Com endereço, "Abrir no navegador" funciona.
5. `Alt+Enter` abre o terminal. As apps de `apps.txt` abrem com os seus atalhos.
5b. `Alt+Esc, C` abre o painel. Clicar numa app e depois numa tecla livre (ou ↓, Enter e a letra): o atalho funciona logo. Clicar numa app e depois no workspace 3 (ou carregar `3`): aparece na caixa; depois de reiniciar, a app abre no 3. Desfazer volta atrás. Teclas cinzentas não aceitam apps.
6. `Alt+Esc, G`, reiniciar: as apps voltam aos seus workspaces.
7. `Alt+Esc, Q` (sair do GlazeWM): todas as janelas ficam visíveis. Para voltar, correr a tarefa `Start-ScheduledTask "GlazeWM (arranque)"`.
8. Com Claude Code: depois de uma resposta, a barra mostra `5h …% · sem …%`.

Registos: `~\.glzr\instalacao.log`, `glazewm\errors.log`, `zebar\errors.log`, `zebar\omarchy-catppuccin\.layout-restore.log`, `.uncloak.log` e `arranque\<nome>.log` (um por `.bat`).

## Excluído da cobertura

O `scripts\testar.ps1` exige 100 % de linhas e ramos na lógica do pack (Python e `.mjs`) e 100 % dos comandos do
`scripts\instalar.ps1`. Fica de fora só a cola com o sistema que um teste não pode correr sem mexer no PC (ou sem
página, no caso do DOM). Cada exclusão está marcada no código com o motivo e verifica-se à mão assim:

| Ficheiro | Função | Motivo | Como se verifica à mão |
|---|---|---|---|
| `morg_cortina.py` | `_BlackCover._run` (`# pragma: no cover`) | Janela Win32 preta, laço de mensagens e pintura GDI do BMP. | §10, passo 1: ecrã preto com a animação, sem clarões nem salto para o SVG. |
| `painel/apps.mjs` | tudo depois dos `import` (`/* node:coverage disable */`) | Ligação ao DOM e ao Zebar (WebView2, Tauri). As decisões e o HTML estão em `apps-logica.mjs`, testados; o `tests/paginas.test.mjs` só carrega a página num DOM falso. | `painel/apps.html?preview` (servidor `pack-preview` do `.claude/launch.json`): escolher uma app e uma tecla, mover e tirar de um workspace, "+ site", filtro, setas, Esc. No Zebar: §10, passo 5b. |
| `guia/guia.mjs` | tudo depois dos `import` (`/* node:coverage disable */`) | Ligação ao DOM e ao Zebar; tabela, HTML e filtro estão em `guia-logica.mjs` e `comum.mjs`, testados. | `guia/guia.html?preview`: quatro colunas, filtro e Esc. No Zebar: §10, passo 3. |
| `scripts\instalar.ps1` | `Sair` | `exit 1` terminaria o próprio Pester. | Correr o `INSTALAR.cmd` num caso que pare (ex.: pasta do utilizador com espaços): mensagem `ERRO:` e sai. |
| `scripts\instalar.ps1` | `BuildDoWindows`, `EAdministrador`, `TipoDaUnidade`, `PastaDocumentos` | Perguntas ao .NET sobre o Windows real (build, administrador, disco de rede, pasta Documentos). | `instalacao.log` tem "Windows build …"; como administrador pergunta "Continuar? (S/N)"; corrido de uma unidade de rede para; `Documentos\Guia de Atalhos` abre a pasta `guia`. |
| `scripts\instalar.ps1` | `PythonServe`, `CorrerAppsApply`, `CorrerPython` | Correm o `py.exe` real (versão do Python, `apps-apply`, statusLine no `settings.json`). | Com Python ≥ 3.10 o passo dos programas diz "Já está tudo instalado"; o `instalacao.log` tem a saída do `apps-apply` e os atalhos das apps funcionam (§10, passo 5); `~\.claude\settings.json` tem a `statusLine` (§10, passo 8). |
| `scripts\instalar.ps1` | `AtivarTls12` | Muda o TLS do processo (.NET `ServicePointManager`). | Num PC sem os programas, os instaladores descarregam-se e verificam-se ("descarregado e verificado"). |
| `scripts\instalar.ps1` | `CarregarGdi`, `RegistarFonteNoWindows`, `AvisarMudancaDeFontes` | `Add-Type` com gdi32/user32: instala a fonte na sessão real e avisa todas as janelas. | Depois de instalar, a barra mostra ícones e não quadrados (§10, passo 2); a fonte aparece em Definições > Tipos de letra. |
| `scripts\instalar.ps1` | `GlazeSair`, `MatarArvore` | Fecham processos reais (`glazewm.exe command wm-exit`, `taskkill`). | Reinstalar com o ambiente a correr: a pasta `~\.glzr` passa a `~\.glzr.copia-…` sem erro. |
| `scripts\instalar.ps1` | `RemoverJuncao` | `cmd /c rmdir` da junction real (A10: nunca `Remove-Item`). | Reinstalar: `Documentos\Guia de Atalhos` continua a abrir a pasta `guia` nova. |
| `scripts\instalar.ps1` | ponto de entrada (última linha, `Instalar`) | Só corre pelo `INSTALAR.cmd`; os testes carregam o ficheiro com `. instalar.ps1`. | O `INSTALAR.cmd` instala (todos os passos do registo, do "Verificações" ao "Concluído"). |

A lista das funções excluídas do instalador, com o motivo, está em `$FuncoesExcluidas` no `tests\instalar.Comum.ps1`:
o `testar.ps1` lê-a de lá e os testes trocam essas funções por bombas (rebentam se um teste lá chegar sem o prever).
