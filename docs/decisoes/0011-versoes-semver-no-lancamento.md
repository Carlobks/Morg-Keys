# 0011 — Versões SemVer, calculadas no lançamento

- **Estado:** aceite (2026-10-31, P3c, aprovado pelo dono: "siga a sua recomendação" nas três perguntas).
- **Contexto:** o relatório de erros dizia "Morg Keys: desconhecida", porque o projeto não tinha número de versão
  (nem `VERSION`, nem secções no `CHANGELOG.md`; a única tag era `exp-a-medida`) e o instalador não gravava nada.
  Sem versão, um relatório não diz o que estava instalado, e quem instala não sabe se uma atualização parte algo.
  Pesquisa em `docs/pesquisa/versoes.md`.
- **Decisão:**
  - **SemVer 2.0.0.** A "API pública" é o que quem instala usa: atalhos, `arranque.txt`, opções do instalador e
    `~\.glzr`;
  - **o número sobe só no lançamento**, pelo `scripts/changelog/juntar_changelog.py`, a partir das categorias dos
    fragmentos:
    - `Removido` ou `Incompatível:` sobe o MAIOR (no 0.x, o MENOR);
    - `Adicionado`, `Alterado` ou `Obsoleto` sobe o MENOR;
    - `Corrigido` ou `Segurança` sobe a CORREÇÃO;
  - **uma só fonte**, o `VERSION` na raiz, escrito na mesma corrida que a secção do `CHANGELOG.md`;
  - o instalador grava `<versão>+<ramo>.<commit>` no `instalacao.json`;
  - uma tag anotada `vX.Y.Z` por versão. O push das tags pede o "sim" do dono, como qualquer push;
  - a 1.ª versão é a **0.1.0**.
- **Consequências:**
  - Uma versão lançada não muda: o portão `commit-msg` recusa mudar uma secção lançada do `CHANGELOG.md` sem a
    linha `Changelog-corrigido: <motivo>`, e recusa mudar o `VERSION` sem a secção nova no mesmo commit.
  - Os testes conferem que o `VERSION` segue o SemVer, que é igual à secção mais recente do changelog, que as
    versões só sobem e que cada tag `v*` tem a sua secção.
  - O CalVer fica de fora, porque não diz se uma mudança é incompatível.
  - Enquanto a versão for 0.x, uma mudança incompatível sobe só o MENOR. Passar à 1.0.0 é uma decisão do dono.
