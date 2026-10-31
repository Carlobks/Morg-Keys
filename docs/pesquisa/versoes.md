# Número de versão do Morg Keys (2026-10-31, P3c)

**Pergunta:** que número dá a versão do Morg Keys, quando sobe e como se guarda o histórico? O relatório de erros
dizia "Morg Keys: desconhecida", porque o projeto não tinha versão nenhuma: nem `VERSION`, nem secções no
`CHANGELOG.md`, e a única tag era `exp-a-medida`.

## Fontes (lidas a 2026-10-31)

- [Semantic Versioning 2.0.0](https://semver.org/lang/pt-BR/) (SemVer), a convenção mais usada:
  - o formato é `MAIOR.MENOR.CORREÇÃO`, com inteiros sem zeros à esquerda;
  - o **MAIOR** sobe numa mudança incompatível da API pública, e o MENOR e a CORREÇÃO voltam a 0;
  - o **MENOR** sobe numa funcionalidade nova compatível, ou quando algo passa a obsoleto, e a CORREÇÃO volta a 0;
  - a **CORREÇÃO** sobe com correções compatíveis;
  - o **0.y.z** é o desenvolvimento inicial: tudo pode mudar, e a API não é estável. A **1.0.0** define a API
    pública estável;
  - a pré-versão vai depois de um hífen (`1.0.0-alpha.1`) e fica abaixo da versão normal;
  - os **metadados da compilação** vão depois de um `+` (`1.0.0+20130313144700`), só com `[0-9A-Za-z-]` separados
    por pontos, e **não contam** para comparar versões;
  - **uma versão lançada não muda**: qualquer mudança sai numa versão nova.
- [Keep a Changelog 1.1.0](https://keepachangelog.com/pt-BR/1.1.0/), já usado no `CHANGELOG.md` (ver
  [changelog.md](changelog.md)): uma secção por versão, a mais recente primeiro, com a data, e links no fim para
  comparar cada versão com a anterior. O próprio texto recomenda o SemVer.
- [CalVer](https://calver.org/) (versões pela data, ex.: Ubuntu `26.04`, Twisted `YY.M.MICRO`, yt-dlp
  `YYYY.0M.0D`):
  - o site recomenda-o para projetos de âmbito grande ou que mudam sempre, para lançamentos marcados pelo
    calendário e para quem não precisa de saber se uma mudança parte algo;
  - quando outros dependem do projeto, recomenda um esquema formal como o SemVer. O CalVer não diz se uma mudança
    é incompatível.
- [Pro Git, 2.6 Tagging](https://git-scm.com/book/en/v2/Git-Basics-Tagging):
  - a tag **anotada** (`git tag -a`) é um objeto completo, com o autor, a data e a mensagem, e é a recomendada;
  - a tag leve é só um ponteiro;
  - o `git push` **não envia tags** sem as pedir (`git push origin <tag>` ou `--follow-tags`).

## O que se decidiu (ADR 0011)

- **SemVer 2.0.0**, adaptado a um produto que se instala. Aqui, a "API pública" é o que quem instala usa: os
  atalhos, o `arranque.txt`, as opções do instalador e os ficheiros em `~\.glzr`.
- **A versão sobe só no lançamento**, calculada pelas categorias dos fragmentos de `changelog.d/`:

  | Sobe | Categoria do fragmento |
  |---|---|
  | MAIOR (no 0.x: MENOR) | `Removido`, ou um fragmento com a linha `Incompatível: <o que muda>` |
  | MENOR | `Adicionado`, `Alterado`, `Obsoleto` |
  | CORREÇÃO | `Corrigido`, `Segurança` |

  O `Removido` conta como incompatível porque tira algo que quem instala usava (o `Alt+Esc G`, por exemplo).
- **Uma só fonte:** o ficheiro `VERSION` na raiz, uma linha, escrito pelo `juntar_changelog.py` na mesma corrida
  que escreve a secção do `CHANGELOG.md`.
- **O que o instalador grava** no `instalacao.json`: a versão e, nos metadados da compilação, o ramo e o commit, ex.:
  `0.1.0+exp-a.c3b57e3`. O `/` do ramo passa a `-`, porque o SemVer não o aceita ali.
- **Histórico:** o `CHANGELOG.md`, uma tag anotada `vX.Y.Z` por versão e os links de comparação no fim do changelog.
- **A 1.ª versão é a 0.1.0**, porque o projeto ainda está em desenvolvimento. A 1.0.0 é quando o dono o declarar
  estável.
- **CalVer não**, porque não diz a quem instala se uma atualização parte algo, e as categorias do changelog já
  fazem essa ligação.

## O que não se verificou

- **Como o GitHub mostra as tags anotadas**, e se convém criar Releases no GitHub. Fica para o primeiro push de uma
  tag, que pede o "sim" do dono.
- **Se a regra do `Removido` é sempre certa.** Uma remoção interna não leva fragmento, porque o fragmento é só para
  o que quem instala nota, por isso, na prática, todo o `Removido` é visto de fora. Se aparecer um caso que não
  parte nada, escreve-se como `Alterado`.
