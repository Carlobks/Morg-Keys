# Plano P2: bug do painel "Apps e arranque" (2026-10-31)

> Cópia do plano aprovado (o original vive na aba Plano do Claude). Atualizada no fim de cada fase,
> no mesmo commit que fecha a fase.

## Contexto

 o 2.º item de `docs/pendentes.md`. Três sintomas relatados pelo dono:
1. ao ligar o PC, o Claude abre no workspace 5 sem estar configurado;
2. as apps postas no arranque trocam de workspace depois de fechar o painel;
3. o `Alt+Esc G` faz o som de erro do Windows e não mostra nada.

## O que a auditoria encontrou

 (`morg_arranjo.py`, `morg_painel.py`, os ficheiros do PC e uma consulta só de
leitura ao GlazeWM):
- **Sintomas 2 e 3:** o `Alt+Esc G` (`layout_save`) e o painel escrevem no mesmo `~\.glzr\layout.json`.
  - O G reescreve o ficheiro só com as janelas abertas nesse momento: as apps do painel que não estão abertas
    desaparecem, e as outras ficam no workspace em que estão agora.
  - Sem nenhuma janela aberta, toca `MessageBeep(MB_ICONHAND)` e não grava nada. É o "som de erro sem nada no ecrã".
- **Sintoma 1, duas causas possíveis** (o `layout.json` do PC está vazio desde as 07:49, por isso já não se vê qual
  foi):
  - um G antigo com o Claude aberto no 5 deixou uma entrada "claude", que o restauro abre pela tabela `LAUNCH`;
  - uma corrida no `_restore_aprender_processos`: uma app do painel sem processo conhecido (as da Store) fica com a
    **primeira janela nova** que aparecer em 12 s. Se o Claude abrir sozinho no arranque do Windows nesse
    intervalo, a app "aprende" o processo `claude`, o Claude é movido para o workspace dela, e o erro fica gravado
    no `layout.json`.
- **Decisão do dono (2026-10-31): tirar o `Alt+Esc G`.** O painel passa a ser o único sítio do arranque.

## Fora do escopo

- mudar o restauro das entradas antigas (`LAUNCH`): continuam a abrir para quem já as tem;
- o resto do painel;
- mexer no PC instalado: só se reinstala com o teu OK.

## Passos

, um commit por grupo:
## Feito

**Feito (2026-10-31):**
- P2.1: o commit da correção;
- P2.2: o commit que tira o G;
- P2.3: pendentes renumerados, armadilhas A48 (dois escritores no mesmo ficheiro) e A49 (o `git checkout` apagou-me
  a correção do P2.1, ainda por commitar: refeita a seguir).

Prova:
- P2.1: vermelho com `'claude' != 'Notas'`, depois verde; os 2 estragos novos apanhados;
- P2.2: vermelho em 15 sítios, depois verde;
- `testar.ps1` verde (443 testes Python a 100 %, 72 Pester).

Por fazer: o teu teste real, depois de reinstalar com o teu OK.

- [x] **P2.1 Aprender o processo certo** (sintoma 1, corrida):
  - teste vermelho: uma app do painel sem processo; durante a espera aparece a janela de um processo que **já
    corria antes** de a abrir (o Claude do arranque do Windows). Hoje aprende-o; deve ignorá-lo;
  - correção: guardar os processos em execução (`_running_images`) antes de abrir, e aceitar só janelas de
    processos que não estavam lá;
  - mais um teste: a janela certa, de um processo novo, continua a ser aprendida;
  - estragos novos para a correção.
- [x] **P2.2 Tirar o `Alt+Esc G`** (sintomas 2 e 3, `refactor` + `feat`):
  - sai a tecla G da camada `sistema` no `config.yaml`, a linha do guia do sistema (`sistema-logica.mjs`) e do guia
    (`guia-logica.mjs`), o subcomando `layout-save` do `bar_helper.py` e a função `layout_save`;
  - os textos do painel que falam do G (`apps.mjs`, `apps-logica.mjs`, `morg_painel.py`) e os docs (`arquitetura`,
    `painel-apps`, `validacao-manual`);
  - teste vermelho: nenhuma tecla, subcomando ou texto vivo cita o `layout-save` ou o "Alt+Esc G". O teste do
    `sistema-logica` que confere cada tecla contra o `config.yaml` continua a passar;
  - os testes e os estragos do `layout_save` saem com o código. O mínimo dos estragos desce só o que sair, e os
    novos do P2.1 repõem-no, com `Teste-mudado:` a dizer porquê;
  - fragmento do changelog: "Removido: Alt+Esc G; o arranque configura-se só no painel".
- [x] **P2.3 Fecho:**
  - `docs/pendentes.md` perde o item 1 (o plano Morg Laws, feito) e o item 2 (este);
  - armadilha nova: dois escritores no mesmo ficheiro com significados diferentes;
  - plano, handoff e memória.

## Prova

- cada teste vermelho antes da correção, depois verde;
- `testar.ps1` verde;
- estragos sem nenhum a escapar;
- **o teu teste real**, depois de reinstalar com o teu OK: pôr 2 apps no arranque pelo painel, fechar o painel,
  reiniciar, e ver cada app no seu workspace e o Claude onde o Windows o abrir. O `Alt+Esc G` deixa de fazer
  qualquer coisa.
