# Changelog por fragmentos (2026-10-31, ML13)

**Pergunta:** como guardar as mudanças que quem instala o Morg Keys nota, sem um ficheiro único em que várias
sessões escrevem ao mesmo tempo?

## Fontes (lidas a 2026-10-31)

- [Keep a Changelog 1.1.0](https://keepachangelog.com/en/1.1.0/), a convenção mais usada:
  - escreve-se para pessoas, não para máquinas;
  - a versão mais recente vem primeiro, com a data em ISO 8601 (AAAA-MM-DD);
  - as mudanças agrupam-se por tipo, por esta ordem: Added, Changed, Deprecated, Removed, Fixed, Security;
  - o que ainda não foi lançado fica numa secção "Unreleased" no topo.
- [towncrier](https://towncrier.readthedocs.io/en/stable/tutorial.html), a ferramenta de fragmentos do pip, do
  pytest e do Twisted:
  - um ficheiro por mudança numa pasta própria, com um identificador e o tipo no nome;
  - na hora de lançar, `towncrier build` junta-os no ficheiro de notícias e apaga os fragmentos (`git rm`);
  - `--draft` só mostra o resultado.
- Skill `git-e-commits` (Morg Laws, §5): `changelog.d/`, um fragmento por mudança vista de fora; as mudanças
  internas não levam.

## O que se decidiu

- **Categorias do Keep a Changelog em português**, pela mesma ordem: Adicionado, Alterado, Obsoleto, Removido,
  Corrigido, Segurança.
- **Fragmentos à maneira do towncrier, sem o towncrier.** O projeto usa só a biblioteca padrão do Python, e o
  script `scripts/changelog/juntar_changelog.py` tem menos de 120 linhas, testado a 100 %.
- **O nome leva a data e o assunto** (`AAAA-MM-DD-assunto.md`) e não o número de uma issue: o projeto não usa
  issues para cada mudança. A skill sugere um hash no fim, mas o hash do commit não existe antes do commit.
- **A categoria vai na primeira linha do ficheiro** (`Categoria: Corrigido`) e não no nome, para que um nome
  errado não mude a categoria sem ninguém notar.
- **"Não lançado" é a pasta `changelog.d/`**, com `--rascunho` para a ver como secção, em vez de uma secção
  escrita à mão no `CHANGELOG.md`, que voltaria a colidir.

## O que não se verificou

- Ainda não se lançou nenhuma versão: o juntar só foi provado nos testes, com pastas temporárias. A primeira
  versão a sério (o número e o que entra) é decisão do dono.
