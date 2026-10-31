# Fragmentos do changelog

Cada mudança que quem instala o Morg Keys nota leva um ficheiro aqui: `AAAA-MM-DD-assunto.md`, com o assunto
em minúsculas e hífenes. Mudanças internas (refatoração, testes, documentação de trabalho) não levam.

```
Categoria: Corrigido
Incompatível: o que quem instala tem de mudar (linha opcional)

- O que mudou, escrito para quem usa o Morg Keys.
  Uma linha de continuação começa por dois espaços.
```

Categorias, por esta ordem: Adicionado, Alterado, Obsoleto, Removido, Corrigido, Segurança.

- O portão `commit-msg` recusa um `feat` ou `fix` que mexa em `2-configuracao/`, no instalador ou no
  desinstalador sem um fragmento no mesmo commit, ou sem a linha `Sem-changelog: <motivo>`.
- O `tests/test_changelog.py` confere o nome e o formato de cada fragmento.
- A linha `Incompatível:` só entra quando quem instala tem de mudar algo (um atalho, o `arranque.txt`); sobe o
  MAIOR da versão (no 0.x, o MENOR).
- `py -I scripts/changelog/juntar_changelog.py` junta-os no `CHANGELOG.md`, calcula a versão seguinte pelas
  categorias, escreve-a no `VERSION` e apaga os fragmentos (ADR 0011).
