# Plano P3c: o sistema e a versão no relatório de erros (2026-10-31)

> Cópia do plano aprovado (o original vive na aba Plano do Claude). Atualizada no fim de cada fase,
> no mesmo commit que fecha a fase.

## Contexto

No relatório que o dono gerou, aparecem duas coisas erradas. A investigação foi só de leitura.
- **"Windows-10-10.0.26200":** o relatório usa o `platform.platform()`. O Windows 11 diz internamente que é a
  versão 10.0, e só o build (≥ 22000) o distingue; o Python 3.11.9 do PC repete esse "10". Até o `ProductName` no
  registo diz "Windows 10 Pro".
- **Versão "desconhecida":** o `versao_instalada()` lê a chave `versao` do `~\.glzr\instalacao.json`, mas o
  `AjustarAmbienteDeTrabalho` (`scripts/instalar.ps1:409`) nunca a grava. E o projeto não tem número de versão
  (nem `VERSION`, nem versões no `CHANGELOG.md`; a única tag é `exp-a-medida`).

## Decisões do dono (2026-10-31), todas as recomendadas

- **SemVer 2.0.0**, adaptado a um produto. O contrato com quem instala é o que ela usa: atalhos, `arranque.txt`,
  opções do instalador, `~\.glzr`;
- **a 1.ª versão é a 0.1.0**. Enquanto for 0.x, uma mudança incompatível sobe só o MENOR; a 1.0.0 é quando o
  dono a declarar estável;
- **regra VERSÃO SÓ NO LANÇAMENTO** no `CLAUDE.md`, com os portões como barreira.

## Como a versão sobe

Só no lançamento, nunca em cada commit. O `juntar_changelog.py` passa a correr sem número,
calcula o próximo pelas categorias dos fragmentos e escreve o `VERSION` (uma linha, na raiz, a única fonte) e a
secção do `CHANGELOG.md`. Depois cria-se a tag anotada `vX.Y.Z`.

| Sobe | Categoria do fragmento |
|---|---|
| MAIOR (no 0.x: MENOR) | `Removido`, ou um fragmento com a linha `Incompatível: <o que muda>` |
| MENOR | `Adicionado`, `Alterado`, `Obsoleto` |
| CORREÇÃO | `Corrigido`, `Segurança` |

## O que o instalador grava

A versão e, depois do `+`, o ramo e o commit, ex.: `0.1.0+exp-a.c3b57e3`. É o campo
"build metadata" do SemVer, que não conta para comparar versões; o `/` passa a `-`. Sem git (instalação a partir de
um ZIP) fica só `0.1.0`; sem `VERSION`, "desconhecida".

## Fora do escopo

- releases no GitHub e o push das tags (pedem o teu "sim", à parte);
- o resto do relatório, e o Claude no arranque (P2.1), que é outro ciclo;
- reinstalar ou mexer no PC sem o teu OK.

## Passos

Com teste vermelho primeiro:

- [x] **P3c.1 Nome do Windows** (`be5d5cd`; vermelho com 3 erros, verde depois; o registo real dá "Windows 11 (build 26200.9457, 25H2)"), em `morg_relatorio_erros.py`:
  - `nome_do_windows(build, revisao, edicao)`: "Windows 11 (build 26200.9457, 25H2)" a partir do build 22000;
    abaixo, "Windows 10 (build …)". Sem dados, cai no `platform.platform()`;
  - leitura com o `winreg` (biblioteca padrão), do `CurrentBuild`, do `UBR` e do `DisplayVersion` em
    `HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion`. Testada com o registo simulado, para os 100 %;
  - o `montar_relatorio` passa a usá-la no campo do sistema;
  - uma nota na `docs/pesquisa/relatorio-de-erros.md`, com a fonte certa: a tabela de lançamentos do Windows 11
    começa no build 22000 (oficial). O limite é uma prática da comunidade, não uma recomendação da Microsoft, que
    recomenda testar a funcionalidade e não a versão. Aqui é só um rótulo para quem lê.
- [x] **P3c.2 Pesquisa e decisão** (`docs`; a da Microsoft em `be5d5cd`, a das versões e a ADR 0011 em `ac85134`). As duas pesquisas desta conversa ficam escritas com o formato do
  `docs/pesquisa/` (pergunta, fontes com a data de leitura, o que se mediu, o que não se verificou, conclusão):
  - **a situação da Microsoft**, numa secção nova da `docs/pesquisa/relatorio-de-erros.md`:
    - a Operating System Version da Microsoft dá o Windows 11 e o 10 como `10.0` e recomenda testar a
      funcionalidade, não a versão;
    - a tabela de lançamentos do Windows 11 começa no build 22000, o que se confirmou (nenhum é mais baixo);
    - o limite 22000 vem do Microsoft Q&A e da comunidade (Dell), não de uma recomendação oficial;
    - o que se mediu neste PC: o `platform.platform()` do Python 3.11.9, o `sys.getwindowsversion()` e o
      `ProductName` do registo ("Windows 10 Pro" num 25H2);
    - **a correção da afirmação errada** que fiz na conversa ("a regra que a Microsoft recomenda");
  - `docs/pesquisa/versoes.md`: SemVer 2.0.0 (as regras de MAIOR, MENOR e CORREÇÃO, o 0.y.z, o build metadata
    depois do `+` e a imutabilidade de uma versão lançada), Keep a Changelog 1.1.0, CalVer (e porque não) e as
    tags anotadas;
  - as duas no índice `docs/pesquisa/README.md` (o teste dos índices exige-o);
  - ADR 0011 "Versões SemVer, calculadas no lançamento";
  - índices dos docs.
- [x] **P3c.3 Cálculo e lançamento** (`857bfb5`; vermelho com 11 falhas e 13 erros. **Achado (A53):** a corrida vermelha correu o código antigo sobre o repositório, que leu `--rascunho` como versão e juntou os fragmentos a sério; repostos do `HEAD`) (`feat(changelog)`), em `scripts/changelog/juntar_changelog.py`:
  - `proxima_versao(atual, categorias, incompativel)` com as regras da tabela e as do 0.x;
  - o `main` aceita a corrida sem número (calcula-o) e escreve o `VERSION`. O `--rascunho` mostra o número
    calculado e não grava nada;
  - os fragmentos aceitam a linha opcional `Incompatível: <o que muda>`, e o `test_changelog.py` confere-a;
  - testes unitários: um por categoria, a mistura, o 0.x, `VERSION` em falta ou mal escrito.
- [x] **P3c.4 Barreiras** (`8e3806b`; o portão vermelho sem o módulo; o `test_versao` apanhou um `VERSION` e uma tag `v9.9.9` temporários) (`test` + portão), cada uma vista a falhar com um estrago temporário:
  - `tests/test_versao.py`:
    - o `VERSION` segue o formato SemVer;
    - é igual à secção mais recente do `CHANGELOG.md`;
    - as versões do changelog só descem de cima para baixo e não se repetem;
    - cada tag local `v*` tem a sua secção;
  - no `commit-msg` (`scripts/portoes/mensagem_commit.py`), duas recusas:
    - mudar uma secção já lançada do `CHANGELOG.md` sem a linha `Changelog-corrigido: <motivo>`;
    - mudar o `VERSION` sem a secção nova no mesmo commit, ou seja, à mão;
  - regra VERSÃO SÓ NO LANÇAMENTO no `CLAUDE.md` (cabe nas 100 linhas) e no `docs/regras-e-barreiras.md`.
- [x] **P3c.5 Versão gravada pelo instalador** (`b550bca`; Pester vermelho com 4 falhas, verde depois; cobertura 13/13; neste repositório dá `desconhecida+exp-a.8e3806b` até haver `VERSION`) (`fix(instalador)`):
  - `scripts/instalar.ps1` tem 498 linhas (limite 500). Por isso, a função `VersaoDoPacote($pasta)` fica num
    ficheiro novo, `scripts/instalar-versao.ps1`, carregado pelo instalador com uma linha `. …`;
  - a função lê o `VERSION` e junta `+<ramo>.<commit>` quando o `git -C $pasta` responde;
  - o `AjustarAmbienteDeTrabalho` grava `versao` no `instalacao.json`;
  - testes Pester: com e sem `VERSION`, com e sem git (simulado), e o `instalacao.json` com `versao`. A cobertura
    do Pester inclui o ficheiro novo. O `desinstalar.ps1` não muda (ignora as chaves que não conhece).
- [x] **P3c.6 Lançar a 0.1.0** (`0e7064d` e a tag anotada `v0.1.0`, só local, com o OK do dono; o instalador passa a gravar
  `0.1.0+exp-a.0e7064d`. **Não feito:** os links de comparação no fim do `CHANGELOG.md`: cada lançamento acrescentaria
  uma linha depois das versões lançadas, e o portão `versao_lancada.py` recusá-lo-ia; o histórico fica nas tags. O
  teste das várias linhas passou a saltar o `VERSION`, que tem uma linha por definição) (só local):
  - `juntar_changelog.py --rascunho` para veres a secção. Depois, com o teu OK, a corrida a sério: o `VERSION` passa
    a `0.1.0`, os fragmentos de `changelog.d/` passam para o `CHANGELOG.md`, e cria-se a tag anotada `v0.1.0`;
  - links de comparação no fim do `CHANGELOG.md`;
  - o push da tag fica para quando disseres "sim".
- [x] **P3c.7 Fecho** (`0ba9086`, `ebe79ce`; estragos **96/96** numa cópia. A 1.ª corrida deu 95/96: com todos os
  portões na lista, um estrago antigo deixou de ser único; a lista passou a ter só os ficheiros com estragos):
  - estragos novos (o limite 22000, as regras do cálculo e a chave `versao`), todos apanhados; o mínimo sobe;
  - plano em `docs/planos/0004-versao-e-sistema-no-relatorio.md`, handoff e memória.

## Prova

- cada teste vermelho antes, depois verde (o do Windows: "Windows-10-…" ≠ "Windows 11 (build 26200…)");
- `testar.ps1` verde e estragos sem nenhum a escapar;
- cada barreira nova vista a recusar (o `VERSION` à mão, uma secção lançada mudada, uma versão a descer);
- daqui, sem arrancar nada: o `nome_do_windows` com o registo real devolve "Windows 11 (build 26200.9457, 25H2)",
  e o `VersaoDoPacote` com este repositório devolve `0.1.0+exp-a.<commit>`;
- **o teu teste real**, depois de reinstalar com o teu OK: o `erro-de-teste` (passo 9 do `docs/validacao-manual.md`)
  e, no relatório, as linhas do sistema e da versão.
