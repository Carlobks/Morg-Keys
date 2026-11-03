# Plano P6: reinstalar sem esconder as janelas (2026-11-03)

> Cópia do plano aprovado (o original vive na aba Plano do Claude). Atualizada no fim de cada fase,
> no mesmo commit que fecha a fase.

## Contexto

Relato do dono (2026-11-01): ao reinstalar, as janelas abertas desaparecem (ficam escondidas, sem botão na barra),
em vez de serem arrumadas de novo. O GlazeWM esconde (cloak) as janelas dos workspaces que não se veem, e a 3.10.1
às vezes não as mostra ao sair. Para isso existe o ajudante `after-exit` (`morg_acoes_windows.py`), que espera o
GlazeWM sair e corre o `uncloak.ps1`. Mas o `FecharAmbienteAntigo` do instalador mandava o GlazeWM sair, esperava
2 s e fechava todos os `pythonw` com `.glzr` no comando, **incluindo o `after-exit`**. Prova: nenhuma das 11 cópias
da `~\.glzr` tinha o `.uncloak.log`, que o `uncloak.ps1` escreve sempre que acaba. As apps com bandeja (Claude,
Steam) só "sobreviveram" por ficarem em segundo plano; o Chrome fechou.

## Feito

**Feito (2026-11-03):** `0288adc` (estrutura) e `f94679c` (correção). Os testes novos foram vistos a falhar antes e
depois ficaram verdes; `testar.ps1` verde (80 Pester, cobertura a 100 % nos quatro scripts PowerShell). Os 4
estragos à mão do `instalar-ambiente-antigo.ps1` foram todos apanhados, numa cópia `git worktree`, porque o
`estragos.py` só estraga `.py` e `.mjs`. **Falta o teu teste real.**

## Fora do escopo

O GlazeWM em si; as janelas escondidas por outras razões; o resto do instalador.

## Passos

Com teste vermelho primeiro:
- [x] **P6.1 Estrutura** (`refactor(instalador)`, `0288adc`): o `FecharAmbienteAntigo`, a cola que só ele usa
  (`GlazeSair`, `MatarArvore`) e o `$GlazeCli` passam para `scripts/instalar-ambiente-antigo.ps1`. O instalador
  carrega-o como carrega o `instalar-versao.ps1` e desce de 499 para 485 linhas. A cobertura e a preparação seguem o
  mesmo padrão; os testes de antes passam sem mudanças.
- [x] **P6.2 A correção** (`fix(instalador)`, `f94679c`):
  - o `after-exit` deixa de ser fechado: o instalador espera até 45 s que ele acabe, o tempo que ele e o
    `uncloak.ps1` esperam pelo GlazeWM, e fecha os outros ajudantes;
  - se ele não existir ou não acabar a tempo, o instalador fecha-o e corre ele próprio o `uncloak.ps1` com
    `-WaitForGlazeExit`, só se o GlazeWM estava a correr;
  - o `instalacao.log` diz qual dos dois caminhos correu: "repostas pelo ajudante after-exit" ou "pelo instalador
    (uncloak.ps1)";
  - os testes estão em `tests/instalar-ambiente-antigo.Tests.ps1` (4); a armadilha é a A54; o fragmento do
    changelog é `2026-11-03-reinstalar-sem-esconder-janelas.md`.
- [x] **P6.3 Fecho:** os estragos à mão, este plano, os pendentes, o handoff e a memória.

## Prova

- [x] cada teste vermelho antes e verde depois; `testar.ps1` verde; nenhum estrago escapou;
- [ ] **o teu teste real**, com o teu OK:
  1. abrir janelas no workspace 1 e no 2;
  2. reinstalar;
  3. ver que as janelas continuam lá e são arrumadas;
  4. ver que a cópia antiga (`~\.glzr.copia-…`) tem o `.uncloak.log` e que o `instalacao.log` diz o caminho que
     correu.
