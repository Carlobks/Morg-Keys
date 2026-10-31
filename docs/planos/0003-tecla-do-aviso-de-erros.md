# Plano P3b: tecla do aviso de erros no Alt+Esc (2026-10-31)

> Cópia do plano aprovado (o original vive na aba Plano do Claude). Atualizada no fim de cada fase,
> no mesmo commit que fecha a fase.

## Contexto

 pedido do dono depois do P3: um botão na camada `Alt+Esc` para ligar e desligar o aviso de erro, com
um ícone pronto. Hoje só se desliga a editar `erros = esconder` no `arranque.txt`.

**Proposta:**
- a tecla **V** ("aViso"), livre na camada `sistema`, que hoje usa I, N, A, B, W, D, P, T, L, C, E, R, O e Q;
- o ícone **nf-md-alert-circle** (`0xf0028`, da mesma família Nerd Font dos outros);
- no painel do `Alt+Esc`, no grupo "Personalizar", uma linha nova: **"Aviso de erros: ligado"** (ou desligado), que
  se atualiza ao carregar no V, como o "Animação: …" se atualiza ao carregar no E. A camada fica aberta;
- o guia `Alt+K` ganha a mesma linha.

## Feito

**Feito (2026-10-31):** `79ab3cf`; testes vermelhos e depois verdes, `testar.ps1` verde (466 Python, 82 JS, 72 Pester), os 2 estragos novos apanhados (mínimo 88). Falta o teu teste real.

## Fora do escopo
 o resto do relatório de erros; mexer no PC instalado sem o teu OK.

## Passos

, com teste vermelho primeiro:
- [x] Python: `alternar_aviso()` em `morg_relatorio_erros.py` troca `erros = mostrar` ↔ `erros = esconder` no
  `arranque.txt`, mantendo o resto do ficheiro, como o `_set_animacao`. Subcomando `bar_helper.py erros toggle`.
- [x] Páginas: em `sistema-logica.mjs`, `avisoDeErros(texto)` e `rotulosDoArranque(texto)` (a animação e o aviso de
  uma vez, para o script em linha do `sistema.html` não crescer, por causa da catraca); a linha com o V em `GROUPS`;
  a linha no `guia-logica.mjs`; o `#erros` com o mesmo estilo do `#anim`.
- [x] A tecla V na camada `sistema` do `config.yaml`, sem sair da camada. O teste que confere cada tecla do painel
  contra o `config.yaml` cobre-a.
- [x] O modelo do `arranque.txt` e o passo manual 9 falam do `Alt+Esc, V`; fragmento do changelog; estragos.

## Prova

- testes vermelhos, depois verdes;
- `testar.ps1` verde;
- estragos sem nenhum a escapar;
- **o teu teste real**, depois de reinstalar: `Alt+Esc`, V, e ver a linha passar a "desligado"; o `bar_helper.py
  erro-de-teste` já não mostra o aviso; V outra vez e o aviso volta.
