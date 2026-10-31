# Validação manual

> Numeração das secções (§N) mantida do antigo `COMO-FOI-FEITO.md`; mapa em `docs/README.md`.

O que os testes automáticos não cobrem e como se verifica à mão (com o passo e o resultado esperado).

## 10. Verificação (depois de instalar ou alterar)

1. Termine a sessão e volte a entrar: o ambiente de trabalho escurece aos poucos até ao preto; a chávena entra, "Muito bem-vindo, <nome>", a hora e a frase do dia, e a lista por baixo; depois o ambiente pronto, sem clarões nem piscar. (Os segundos de papel de parede antes do escurecer são a A38, por resolver.)
2. A barra no topo tem ícones (não quadrados) e mostra o relógio e os workspaces.
3. `Alt+K` abre o guia e fecha com `Esc`, `Alt+K` e com um clique fora. Segurar `Alt+K` abre uma só vez.
4. `Alt+Esc` mostra o painel; `Esc` fecha. `Alt+Esc`, `I` faz aparecer o café. `Alt+Esc`, tocar `E`: o painel mostra "Animação: X" (muda quando há mais de uma). Segurar `E`: ao largar, a animação aparece uns segundos.
4b. Cada `.bat` de `arranque.txt` tem o seu ícone junto ao relógio. Com endereço, "Abrir no navegador" funciona.
5. `Alt+Enter` abre o terminal. As apps de `apps.txt` abrem com os seus atalhos.
5b. `Alt+Esc, C` abre o painel. Clicar numa app e depois numa tecla livre (ou ↓, Enter e a letra): o atalho funciona logo. Clicar numa app e depois no workspace 3 (ou carregar `3`): aparece na caixa; depois de reiniciar, a app abre no 3. Desfazer volta atrás. Teclas cinzentas não aceitam apps.
6. Pôr apps no arranque pelo painel (`Alt+Esc, C`), reiniciar: as apps abrem nos seus workspaces.
7. `Alt+Esc, Q` (sair do GlazeWM): todas as janelas ficam visíveis. Para voltar, correr a tarefa `Start-ScheduledTask "GlazeWM (arranque)"`.
8. Com Claude Code: depois de uma resposta, a barra mostra `5h …% · sem …%`.
9. Relatório de erros: correr `C:\Windows\pyw.exe -I "%USERPROFILE%\.glzr\zebar\omarchy-catppuccin\bar_helper.py" erro-de-teste`. Aparece o aviso "Morg Keys: erro" com o resumo; "Sim" abre o "Guardar como" em Documentos; o ficheiro guardado não tem o nome da conta nem o caminho pessoal. Fica também uma cópia em `.glzr\erros`. Com `erros = esconder` no `arranque.txt`, não há aviso, mas a cópia aparece. `Alt+Esc`, `V`: a linha "Aviso de erros" do painel passa a "desligado" (e volta a "ligado" com outro `V`), e o `arranque.txt` muda com ela.

Registos: `~\.glzr\instalacao.log`, `glazewm\errors.log`, `zebar\errors.log`, `zebar\omarchy-catppuccin\.layout-restore.log`, `.uncloak.log` e `arranque\<nome>.log` (um por `.bat`).

## Excluído da cobertura

O `scripts\testar.ps1` exige 100 % de linhas e ramos na lógica do pack (Python e `.mjs`) e 100 % dos comandos do
`scripts\instalar.ps1`. Fica de fora só a cola com o sistema que um teste não pode correr sem mexer no PC (ou sem
página, no caso do DOM). Cada exclusão está marcada no código com o motivo e verifica-se à mão assim:

| Ficheiro | Função | Motivo | Como se verifica à mão |
|---|---|---|---|
| `morg_cortina.py` | `_BlackCover._run` (`# pragma: no cover`) | Janela Win32 em camadas, temporizador e laço de mensagens. | §10, passo 1: o ambiente de trabalho escurece aos poucos (não de repente) e passa ao ecrã de boas-vindas sem piscar. Medido a 2026-10-24 com um script: brilho do ecrã 88 → 31 → 1 → 0 em 1,5 s. |
| `painel/apps.mjs` | tudo depois dos `import` (`/* node:coverage disable */`) | Ligação ao DOM e ao Zebar (WebView2, Tauri). As decisões e o HTML estão em `apps-logica.mjs`, testados; o `tests/paginas.test.mjs` só carrega a página num DOM falso. | `painel/apps.html?preview` (servidor `pack-preview` do `.claude/launch.json`): escolher uma app e uma tecla, mover e tirar de um workspace, "+ site", filtro, setas, Esc. No Zebar: §10, passo 5b. |
| `guia/guia.mjs` | tudo depois dos `import` (`/* node:coverage disable */`) | Ligação ao DOM e ao Zebar; tabela, HTML e filtro estão em `guia-logica.mjs` e `partilhado/paineis.mjs`, testados. | `guia/guia.html?preview`: quatro colunas, filtro e Esc. No Zebar: §10, passo 3. |
| `bar.html` | o `<script>` em linha | Ligação ao DOM, ao canvas dos ícones e ao Zebar (providers, `shellExec`, cliques). O HTML de cada zona, o relógio, o volume, a chávena e os comandos estão em `bar-logica.mjs`, `partilhado/bateria.mjs` e `partilhado/claude.mjs`, testados; o `tests/paginas-em-linha.test.mjs` confirma que os nomes importados existem. | No Zebar: ícones e relógio (§10, passo 2); clicar num workspace e rodar a roda sobre eles; minimizar uma janela e clicar na etiqueta (volta e recebe o foco); `Alt+R` mostra o modo e clicar nele sai; clique no relógio (notificações) e botão direito (formato longo com a semana); som: roda (passos de 5), botão direito (silencia), clique (Definições Rápidas); rede: clique; chávena (§10, passo 4); Claude (§10, passo 8). |
| `arranque/splash.html` | o `<script>` em linha | Ligação ao DOM, ao canvas, às transições e ao Zebar (`progress.json`, `splash-ready`, fechar o widget). Os tempos, a saudação, os ícones, o estado das etapas e quando sair estão em `splash-logica.mjs`, testados. | `arranque/splash.html?preview`: a chávena, "Muito bem-vindo, Ana", a hora, a frase com o autor e duas etapas. No Zebar: §10, passo 1 (a lista enche-se, as linhas ficam feitas e o ecrã sai sozinho). |
| `guia/sistema.html` | o `<script>` em linha | Ligação ao DOM, aos ícones em SVG e ao Zebar (esconder, `layer-hide`, ler o `arranque.txt`). Os grupos, o seu HTML, o nome da animação e a camada ativa estão em `sistema-logica.mjs`, testados (incluindo que cada tecla tem ação no `config.yaml`). | `guia/sistema.html` aberto como ficheiro: cinco grupos com ícones e teclas. No Zebar: §10, passo 4. |
| `scripts\instalar.ps1` | `Sair` | `exit 1` terminaria o próprio Pester. | Correr o `INSTALAR.cmd` num caso que pare (ex.: pasta do utilizador com espaços): mensagem `ERRO:` e sai. |
| `scripts\instalar.ps1` | `BuildDoWindows`, `EAdministrador`, `TipoDaUnidade`, `PastaDocumentos` | Perguntas ao .NET sobre o Windows real (build, administrador, disco de rede, pasta Documentos). | `instalacao.log` tem "Windows build …"; como administrador pergunta "Continuar? (S/N)"; corrido de uma unidade de rede para; `Documentos\Guia de Atalhos` abre a pasta `guia`. |
| `scripts\instalar.ps1` | `NomeDaConta` | .NET `UserPrincipal.Current`: o nome da conta real do Windows. | A pergunta do nome mostra "(Enter = <1.º nome>)" numa conta Microsoft com nome; numa conta local sem nome completo, "(Enter = sem nome)". |
| `scripts\instalar.ps1` | `PythonServe`, `CorrerAppsApply`, `CorrerPython` | Correm o `py.exe` real (versão do Python, `apps-apply`, statusLine no `settings.json`). | Com Python ≥ 3.10 o passo dos programas diz "Já está tudo instalado"; o `instalacao.log` tem a saída do `apps-apply` e os atalhos das apps funcionam (§10, passo 5); `~\.claude\settings.json` tem a `statusLine` (§10, passo 8). |
| `scripts\instalar.ps1` | `AtivarTls12` | Muda o TLS do processo (.NET `ServicePointManager`). | Num PC sem os programas, os instaladores descarregam-se e verificam-se ("descarregado e verificado"). |
| `scripts\instalar.ps1` | `CarregarGdi`, `RegistarFonteNoWindows`, `AvisarMudancaDeFontes` | `Add-Type` com gdi32/user32: instala a fonte na sessão real e avisa todas as janelas. | Depois de instalar, a barra mostra ícones e não quadrados (§10, passo 2); a fonte aparece em Definições > Tipos de letra. |
| `scripts\instalar.ps1` | `GlazeSair`, `MatarArvore` | Fecham processos reais (`glazewm.exe command wm-exit`, `taskkill`). | Reinstalar com o ambiente a correr: a pasta `~\.glzr` passa a `~\.glzr.copia-…` sem erro. |
| `scripts\instalar.ps1` | `RemoverJuncao` | `cmd /c rmdir` da junction real (A10: nunca `Remove-Item`). | Reinstalar: `Documentos\Guia de Atalhos` continua a abrir a pasta `guia` nova. |
| `scripts\instalar.ps1` | ponto de entrada (última linha, `Instalar`) | Só corre pelo `INSTALAR.cmd`; os testes carregam o ficheiro com `. instalar.ps1`. | O `INSTALAR.cmd` instala (todos os passos do registo, do "Verificações" ao "Concluído"). |
| `scripts\desinstalar.ps1` | `GlazeSair`, `MostrarJanelasEscondidas` | Mexem na sessão real (`glazewm.exe command wm-exit`, `uncloak.ps1`). | Correr o `DESINSTALAR.cmd` com o ambiente ligado: a barra e o GlazeWM fecham e nenhuma janela fica escondida. |
| `scripts\desinstalar.ps1` | `PastaDocumentos`, `RemoverJuncao`, `CorrerPython` | Pasta Documentos real, `cmd /c rmdir` da junction (A10) e `py.exe` real (tirar a `statusLine`). | Depois de desinstalar: `Documentos\Guia de Atalhos` já não existe; `~\.claude\settings.json` sem `statusLine`. |
| `scripts\desinstalar.ps1` | ponto de entrada (última linha, `Desinstalar`) | Só corre pelo `DESINSTALAR.cmd`. | `~\.glzr`, `AppData\Roaming\zebar` e `AppData\Local\com.glzr.zebar` passam a `….removido-<data>`. |

A lista das funções excluídas do instalador, com o motivo, está em `$FuncoesExcluidas` no `tests\instalar.Preparacao.ps1`:
o `testar.ps1` lê-a de lá e os testes trocam essas funções por bombas (rebentam se um teste lá chegar sem o prever).
