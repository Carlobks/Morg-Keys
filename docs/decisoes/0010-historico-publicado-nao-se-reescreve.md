# 0010 — O histórico já publicado não se reescreve (caminho pessoal em commits antigos)

- **Estado:** aceite (2026-10-31, ML16 do plano Morg Laws, aprovado pelo dono).
- **Contexto:** a 2.ª verificação Morg Laws (`docs/morg-laws/verificacao-02-2026-10-31.md`, achado M1) contou 4
  commits de 2026-10-23 e 2026-10-24, já enviados para o `main` público, que ainda têm o caminho da conta do
  Windows do utilizador. A árvore atual está limpa desde a ML1, e o `tests/test_dados_pessoais.py` impede que o
  caminho volte. O plano já dizia que o histórico publicado não se reescreve (secção D7: o nome antigo, o
  `17ce46f`, os títulos longos).
- **Decisão:** não reescrever o histórico publicado. Os 4 commits ficam como estão, registados aqui como exceção.
  O caminho é o de uma pasta pessoal e não um segredo (nada a rodar ou revogar); o gitleaks não acusa nada em
  todo o histórico.
- **Consequências:**
  - Reescrever (com `git filter-repo` e um push forçado) mudaria os hashes do `main` público: quem já tem um clone
    ficaria com um histórico que não bate, as ligações para commits deixariam de funcionar, e as cópias e os
    índices de terceiros guardariam o original na mesma.
  - Se um dia o dono quiser apagar o caminho do histórico, é uma decisão nova, com o custo acima, e pede uma ADR
    que substitua esta.
  - Daqui para a frente, o portão do git (`pre-commit` com a lista negra e o teste dos dados pessoais) trava o
    caminho antes de ele chegar a um commit.
