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
