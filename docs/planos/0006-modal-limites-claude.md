# Plano P7: modal dos limites do Claude (2026-11-03/04)

> Cópia do plano aprovado (o original vive na aba Plano do Claude). Atualizada no fim de cada fase,
> no mesmo commit que fecha a fase.

## Contexto

O clique no ✻ da barra abria `claude.ai/settings/usage`. Os números da barra só chegam do
`~/.claude/rate_limits.json`, que só a statusLine do Claude Code no terminal escreve. O dono usa a aplicação de
ambiente de trabalho, por isso a barra ficava sem valores ou com valores velhos. Pedido: o clique abre um modal
pequeno para pôr à mão, depressa, com o rato ou o teclado, o % das 5 h, o % da semana e a hora do reset.

**Decisões do dono (2026-11-03, todas a recomendada):**
- um widget novo do Zebar (`limites`), pequeno, por baixo da barra, à direita; fecha com Esc, com um clique fora
  ou ao gravar, e devolve o foco à janela de antes;
- o reset das 5 h num só campo: a hora (`14:30`; se já passou, amanhã) ou o tempo que falta (`2h15`, `45m`);
- a semana: o % e um campo opcional para o dia e a hora (`qui 16:00`); vazio mantém o anterior;
- grava no mesmo `rate_limits.json`, com `"origem": "manual"` e `captured_at`; a statusLine põe por cima depois;
- a página de uso passa para o botão direito no ✻, e o modal tem um link para ela.

## Fora do escopo

Ler os números sozinho da conta ou da página (as regras da Anthropic não deixam, `docs/pesquisa/quota-claude.md`);
mudar a statusLine; o resto da barra.

## Passos

Com teste vermelho primeiro:
- [x] **P7.0 Pesquisa** (`6366dc8`, `docs/pesquisa/modal-limites.md`): `anchor: top_right` com `-8px`/`34px`
  (píxeis escalados como a barra, lido no código do Zebar 3.3.1); o foco segue o padrão do painel das apps.
- [x] **P7.1 Lógica em Python** (`83ccd47` estrutura, `70bb2ac`): o `morg_limites.py` lê o % e o reset
  (tempo que falta, hora, dia e hora; recusa o que passa da janela) e grava só as janelas que mudam, de forma
  atómica. Subcomandos `limites`, `limites-hide` e `limites state|set <b64>`; 23 testes.
- [x] **P7.2 Página e widget** (`9da1b0e`): `limites/limites.html`, `limites.mjs` (cola, verificada à mão) e
  `limites-logica.mjs` (6 testes). O reset atual fica só na dica ("vazio: fica 2h15"): um "2h15" velho escrito
  por cima gravaria uma hora errada. Vista em `?preview`.
- [x] **P7.3 Barra** (`45c54ba`): o clique pede `bar_helper.py limites`, o botão direito abre a página de uso e,
  durante 1 min depois do clique, a barra relê de 3 em 3 s (`ligarClaude` no `claude.mjs`). A dica diz "Valores
  postos à mão há …"; o `claude_usage.py` devolve a origem.
- [x] **P7.4 Fecho:** 14 estragos novos (`3690913`), o `limites` pré-carregado no `settings.json` do Zebar (o 1.º
  clique fica rápido), a validação manual, o changelog (`Adicionado`), este plano, os pendentes, a arquitetura e
  o handoff.

## Lições

- As catracas não deixam crescer os `noqa`, os `node:coverage disable` nem os `<script>` em linha: a cola foi para
  um `.mjs` que nenhum teste carrega, e os cliques da barra para uma função testada.
- O heredoc do Bash estraga as barras invertidas: os scripts com `\\` escrevem-se com o Write.

## Prova

- [x] cada teste vermelho antes e verde depois; `testar.ps1` verde; os 14 estragos novos apanhados;
- [x] a página vista em `limites/limites.html?preview`;
- [x] **o teu teste real** (feito pelo dono a 2026-11-04: "Funcionou."):
  1. clicar no ✻;
  2. pôr `40` nas 5 h, `2h15` no reset e `70` na semana, e carregar em Enter;
  3. a barra mostra logo `5h 40% · sem 70% · ↺ 2h15`;
  4. Esc fecha sem gravar;
  5. o botão direito abre a página de uso.
