# CLAUDE.md — Morg Keys

Windows 11 conduzido pelo teclado ao estilo Omarchy: GlazeWM 3.10.1 + Zebar 3.3.1 (páginas HTML em WebView2), ajudantes
Python 3 (só biblioteca padrão) e instalador PowerShell 5.1. Documentação: `docs/README.md`. Regras gerais: Morg Laws.
Cada regra abaixo tem a barreira que a obriga em `docs/regras-e-barreiras.md`; o detalhe está nas skills e nos docs.

## Regra n.º 1

- **NUNCA ARRANCAR O AMBIENTE:** não correr `glazewm.exe`, `zebar.exe` (nem `zebar startup`), `bar_helper.py boot`,
  `layout-restore` ou `animacao` com o Zebar fechado. Pedir ao utilizador a tarefa agendada ou
  `Start-ScheduledTask "GlazeWM (arranque)"`; seguro daqui: `glazewm command …`, ler ficheiros e registos.
  · *Herdam `CLAUDECODE`/`ANTHROPIC_BASE_URL` deste terminal e o Claude Code aberto pelos atalhos passa a cobrar pela API (A2).*

## Núcleo

- **PLANO ANTES DE MEXER:** trabalho com vários ficheiros começa por um plano na aba Plano (objetivo, fora do escopo,
  prova) e pelo "sim" do dono. · *Cada palpite errado custa uma volta de retrabalho.*
- **DECISÃO É DO DONO:** uma decisão a meio vai ao dono, explicada, com a recomendada marcada. · *Não se decide o que é dele.*
- **COMMIT SEM PEDIDO, PUSH COM O SIM:** commitar não precisa de pedido; push e PR precisam do "sim", a cada vez. · *O push publica no momento em que sai.*
- **OS HOOKS SÃO A REDE:** nunca `--no-verify` nem desligar o `core.hooksPath`; hook recusou, corrige-se a causa. · *Saltado, deixa passar o erro.*
- **NÃO PIORAR:** o que já viola não pode piorar (catraca); ficheiro novo nasce limpo. · *Senão a dívida só cresce.*
- **SEM SILENCIAR ALARME:** nada de `noqa`, `pragma: no cover` ou regra desligada novos sem o motivo escrito ao lado.
  · *Um alarme calado sem motivo esconde o problema seguinte (Akita).*
- **BUG TRAZ TESTE:** antes de corrigir, um teste que falha (mostrar a corrida vermelha); depois, verde. Sem teste
  possível, o commit leva `Sem-teste: <motivo>`. · *Um teste que nunca falhou não prova nada.*
- **PROVAR MEDINDO:** "feito" só com o comando e a saída; dizer também o que não se verificou. · *Parecer certo não é prova.*
- **NOMES PESQUISÁVEIS:** nomes que dizem a função e dão menos de 5 resultados no grep; nada de `utils`, `helper`,
  `comum`, `data` soltos. · *Um nome genérico esconde onde está a lógica.*
- **TEXTO VIRA BARREIRA:** uma regra que tem de ser cumprida ganha hook, teste ou CI, e entra no mapa das barreiras. · *Texto é conselho; só a máquina obriga.*

## Nunca

- **SEM DADOS REAIS:** nada de nomes, contas, e-mails ou caminhos pessoais em testes, exemplos, docs ou commits; o
  nome fictício é "Ana". · *O repositório é público (ADR 0002).*
- **SEM SEGREDOS:** não ler `.env` nem chaves, não correr `curl | sh`, não mudar as próprias permissões.
  · *Um segredo lido vai para o contexto e pode sair num commit; um download corrido é código que ninguém leu.*
- **SÓ O PRÓPRIO TRABALHO:** commit por caminho (`git commit -F msg -- <ficheiros>`), nunca `git add -A`, `.` nem
  `commit -a`. · *Um commit de tudo leva o trabalho de outra sessão.*

## Testes

- **UM SÓ COMANDO:** `powershell -File scripts/testar.ps1` (unittest + `node --test` + Pester + lint), também no
  `pre-commit`. · *Dois comandos acabam com um esquecido.*
- **COBERTURA 100 %:** linhas e ramos da lógica testável; a cola com o sistema fica fina, com o motivo da exclusão e
  o passo manual em `docs/validacao-manual.md`. · *O que não se mede não se sabe se corre.*
- **NUNCA ENFRAQUECER UM TESTE:** não apagar, desligar nem afrouxar um teste para ficar verde; mudar um teste pede o porquê
  (`Teste-mudado:`). · *Um teste afrouxado fica verde e deixa de proteger.*

## Código

- **FICHEIROS PEQUENOS:** cada ficheiro abaixo de 500 linhas (alvo 200–300), cada função até 35 linhas, uma
  responsabilidade por ficheiro. · *Um ficheiro grande não cabe na cabeça de quem o lê, pessoa ou agente.*
- **PYTHON ISOLADO:** chamar sempre `C:\Windows\py.exe -I` ou `pyw.exe -I`; não há `python` no PATH.
  · *Sem `-I`, um ficheiro da pasta com o nome de um módulo corre no lugar dele.*
- **CODIFICAÇÃO:** `.ps1` em UTF-8 com BOM; JSON, YAML e HTML sem BOM (A16). No PowerShell, `$funcao`, nunca
  `$nome` em código que carrega o instalador (A37). · *O PowerShell 5.1 lê sem BOM como ANSI e estraga os acentos.*
- **FINS DE LINHA:** manter os de cada ficheiro (`git ls-files --eol`); editar em bytes, nunca `sed -i` nem
  `write_text` (A27, A45). · *Um ficheiro com os fins trocados faz os estragos parecerem escapar.*
- **SUBSTITUIÇÕES COM CONTAGEM:** substituições em massa com `assert` do número exato de ocorrências (A27). · *Uma troca a mais ou a menos passa calada.*
- **ESTRUTURA À PARTE:** não misturar mudança de estrutura e de comportamento no mesmo commit. · *Misturadas, a revisão não vê o que mudou de facto.*
- **COMENTÁRIOS FICAM:** ao refatorar, preservar os comentários e atualizá-los; nunca os apagar em silêncio. · *Guarda o porquê que o código não diz.*

## Documentação

- **DECISÕES EM ADR:** cada decisão num ficheiro NNNN-titulo.md em `docs/decisoes/` (contexto, decisão,
  consequências); os números nunca se reutilizam. · *Sem o contexto, a decisão volta a discutir-se.*
- **ARMADILHAS REGISTADAS:** cada problema e a regra para o evitar em `docs/armadilhas.md` (A1, A2, …). · *Uma lição que fica na conversa não volta a ser lida.*
- **ÍNDICE DOS DOCS:** cada `.md` novo tem linha em `docs/README.md` (pesquisa também em `docs/pesquisa/README.md`).
  · *Um documento fora do índice não se encontra.*
- **PESQUISA ANTES DE IMPLEMENTAR:** algo novo pede pesquisa nas fontes líderes, guardada em `docs/pesquisa/`. · *Adivinhar uma API custa mais do que lê-la.*

## Commits e publicação

- **FORMATO DOS COMMITS:** título `tipo(área): …` até 72 caracteres, linha em branco, corpo com o que mudou e
  porquê; mensagem num ficheiro (`-F`), com `Co-Authored-By` do modelo. · *A mensagem é tão pública como o código.*
- **CHANGELOG POR FRAGMENTO:** um feat ou fix no que se instala leva `changelog.d/AAAA-MM-DD-assunto.md` ou
  `Sem-changelog: <motivo>`. · *Quem instala precisa de saber o que mudou; um ficheiro único colide.*
- **REPOSITÓRIO PARA O PC:** editar no repositório e reinstalar; nunca copiar do `~\.glzr` para o repositório.
  · *Um só sentido: o que se copia de volta leva o que os testes nunca viram.*

## Arquitetura (detalhe em `docs/arquitetura.md`)

- `2-configuracao/glzr/` vai para `~\.glzr` pelo instalador (marcadores `{{HOME}}`, `{{HOME_RE}}`, `{{NOME}}`).
  - `glazewm/config.yaml`: atalhos, modos `sistema`/`resize`, bloco de apps gerado por `apps-apply`.
  - `zebar/omarchy-catppuccin/`: o único pack do Zebar (`zpack.json`, 5 widgets: bar, guia, sistema, apps, splash).
  - `bar_helper.py` é o ajudante (subcomandos na docstring); as páginas só lhe pedem o que o `argsRegex` deixa (A9).
- `scripts/`: instalar, desinstalar, testar, estragos e `portoes/` (hooks do git) · `tests/` · `docs/`.

## Quando ler que skill

| Situação | Skill |
|---|---|
| Vai mudar este CLAUDE.md, uma skill ou uma regra | `escrevendo-regras-de-agente` |
| Pedido grande sem limites ou sem forma de validar | `pondo-o-plano-a-prova` |
| Vai dividir trabalho entre sessões ou agentes, ou retomar | `orquestrando-sessoes` |
| Vai commitar ou fechar um ciclo de trabalho | `git-e-commits` |
| Vai corrigir um bug, testar ou provar que algo funciona | `testes-e-provas` |
| Vai criar ou rever uma página (barra, guia, painel, splash) | `desenhando-telas` |
| Vai fazer push, mexer em dependências ou no instalador | `auditoria-de-seguranca` |
