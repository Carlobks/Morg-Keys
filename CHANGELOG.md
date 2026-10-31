# Changelog

As mudanças do Morg Keys que se notam por quem o instala. Segue o [Keep a Changelog 1.1.0][kac]: a versão
mais recente primeiro, as datas em AAAA-MM-DD e as mudanças agrupadas por categoria.

O que ainda não foi lançado está em `changelog.d/`, um ficheiro por mudança (formato em
`changelog.d/README.md`). Na hora de lançar uma versão, `py -I scripts/changelog/juntar_changelog.py` junta-os
aqui, calcula a versão seguinte pelo [SemVer 2.0.0][semver] (ADR 0011), escreve-a no `VERSION` e apaga-os; com
`--rascunho` só mostra a secção.

[kac]: https://keepachangelog.com/pt-BR/1.1.0/
[semver]: https://semver.org/lang/pt-BR/
