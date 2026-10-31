# Plano P3: relatório de erros (2026-10-31)

> Cópia do plano aprovado (o original vive na aba Plano do Claude). Atualizada no fim de cada fase,
> no mesmo commit que fecha a fase.

## Contexto

 o 1.º item de `docs/pendentes.md`, pedido pelo dono a 2026-10-31. Hoje, quando um ajudante Python
(`bar_helper.py`, o arranque) rebenta, o erro perde-se: o `pythonw` não tem consola e só algumas partes escrevem um
registo. O pedido:
- um popup com o erro, ligado por omissão e desligável;
- quem usa escolhe onde guardar o relatório, para o juntar a uma issue no GitHub;
- o relatório leva o que é preciso para corrigir e nada de pessoal.

A pesquisa (`docs/pesquisa/relatorio-de-erros.md`, commit da pesquisa) diz o que o relatório leva: o resumo; a
hora, as versões e o subcomando; a exceção (tipo, mensagem, stack trace e gravidade, como o OpenTelemetry); as
últimas linhas do registo do arranque; e os campos que quem envia preenche (passos, o que esperava, o que
aconteceu). A limpeza troca a pasta pessoal por `~` e o nome da conta por `<utilizador>`, e não leva títulos de
janelas.

## Fora do escopo

- os erros das páginas do Zebar (JavaScript), que ficam para depois;
- enviar o relatório sozinho para algum lado: nunca sai sem quem usa o ler e anexar;
- mexer no PC instalado sem o teu OK.

## Passos

, um commit por grupo, cada um com um teste vermelho primeiro:
- [x] **P3.1 O relatório** (2026-10-31, `c876696`; o teste apanhou uma fuga: a mensagem de um OSError mostra o
  caminho com as barras a dobrar, e essa forma escapava à limpeza; agora conta também):
  - `montar_relatorio(exc, subcomando, contexto)` devolve o texto em Markdown, com as secções da pesquisa;
  - `limpar(texto)` troca a pasta pessoal por `~` e o nome da conta e o do `arranque.txt` por `<utilizador>`. Os
    testes usam a "Ana" como conta falsa;
  - os argumentos em base64 do painel ficam de fora;
  - a versão do Morg Keys vem do `instalacao.json`, que o instalador já grava; se faltar, diz "desconhecida".
- [x] **P3.2 O popup e o guardar** (2026-10-31: `7b1f8e2` com o popup desligável e as cópias, `65db12c` com o
  popup, o "Guardar como" e o gancho. A cola com o Windows ficou testada com o Windows simulado, sem `pragma`. A
  estrutura `OPENFILENAMEW` foi conferida: 152 bytes. **Achado (A50):** o teste que corre o `bar_helper.py` no
  processo dos testes passou a instalar o gancho e a criar `~\.glzr\erros` no PC real; agora simula-o. **Não feito:**
  o instalador ainda não grava a versão no `instalacao.json`, por isso o relatório diz "desconhecida"):
  - o `bar_helper.py` passa a apanhar a exceção no topo (`main`) e o `faulthandler` escreve num ficheiro os
    rebentamentos em C (o ctypes);
  - popup nativo do Windows (`MessageBoxW`), que aparece mesmo com o Zebar em baixo, que é quando os erros mais
    importam: mostra o resumo e pergunta "Guardar o relatório?";
  - com "Sim", abre a janela "Guardar como" do Windows (`GetSaveFileNameW`, só biblioteca padrão). A pasta proposta
    é Documentos, e quem usa escolhe;
  - `erros = mostrar | esconder` no `arranque.txt` (por omissão `mostrar`). Com `esconder`, não há popup, mas o
    relatório fica na mesma em `~\.glzr\erros\` (os últimos 10), para se poder ir buscar depois;
  - a cola com o Windows fica excluída da cobertura, com o motivo e o passo manual em `docs/validacao-manual.md`.
- [x] **P3.3 A issue no GitHub** (`d2869eb`; a etiqueta "erro" ainda tem de ser criada no GitHub): formulário `.github/ISSUE_TEMPLATE/erro.yml` com o resumo, os passos, o que
  esperava, o que aconteceu e o relatório colado (`render: shell`). O README "Para quem contribui" aponta para ele.
- [x] **P3.4 Fecho** (6 estragos novos, todos apanhados; mínimo dos estragos 80 → 86; armadilha A50):
  - fragmento do changelog;
  - estragos novos para o relatório e a limpeza;
  - o `docs/pendentes.md` perde o item;
  - plano em `docs/planos/0002-relatorio-de-erros.md`, handoff e memória.

## Prova

- cada teste vermelho antes, depois verde;
- `testar.ps1` verde;
- estragos sem nenhum a escapar;
- um relatório de exemplo gerado nos testes (com a "Ana"), conferido sem nenhum caminho pessoal;
- **o teu teste real**, depois de reinstalar com o teu OK: provocar um erro de propósito (um subcomando de teste,
  `bar_helper.py erro-de-teste`), ver o popup, guardar o relatório e lê-lo.
