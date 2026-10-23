# Método do Fabio Akita para trabalhar com agentes

Pesquisa de 2026-10-23 (blog akitaonrails.com e repositórios públicos github.com/akitaonrails).
Não foram vistos vídeos do YouTube.

## Pedir bem (os quatro blocos)
Objetivo · abordagem · **o que não fazer** · como validar. O agente faz um plano, o humano aprova, só depois
executa (ele usa um ficheiro-flag para impedir a fase seguinte sem aprovação). Passos idempotentes; base de
conhecimento viva em `docs/`.
- https://akitaonrails.com/2026/04/15/como-falar-com-o-claude-code-efetivamente/

## CLAUDE.md
- "curto, imperativo, orientado a ação"; o modelo dele tem **menos de 100 linhas** (~500 tokens).
- Cobre: estilo, comentários, testes, dependências, estrutura, formatação, logging.
- Nos repositórios: CLAUDE.md curto (17–20 linhas) que aponta para AGENTS.md; AGENTS.md com Overview,
  Commands, Architecture, Tests, **Do**, **Don't**, **PR Checklist**. Há projetos dele com 195–218 linhas e
  um de 831 (que aponta para `docs/ARCHITECTURE.md` e `docs/design-decisions.md`).
- https://akitaonrails.com/2026/04/20/clean-code-para-agentes-de-ia/

## Código para agentes
- Ficheiros: **abaixo de 500 linhas, idealmente 200–300** (o agente lê 2000 linhas por leitura).
- Funções: 4–20 linhas.
- Nomes: evitar `data`, `handler`, `Manager`: o grep devolve dezenas de resultados. Critério: um nome deve dar
  **menos de 5 resultados no grep**.
- Comentários: manter os que explicam o **porquê** e a origem (bug, restrição, commit); tirar os óbvios.

## Testes
- "TDD é mais importante com IA, não menos". Cada função nova leva teste; cada bug, teste de regressão.
- Testes correm sem intervenção humana.
- Cobertura no projeto dele: **acima de 80 % (95 %+ na lógica de negócio)** — não pede 100 %.
- Projeto de exemplo: 1323 testes, mais linhas de teste do que de código; a CI apanhou 50+ bugs reais.
- https://akitaonrails.com/2026/02/20/do-zero-a-pos-producao-em-1-semana-como-usar-ia-em-projetos-de-verdade-bastidores-do-the-m-akita-chronicles/

## Ciclos e commits
Commits pequenos e frequentes, cada commit pronto para produção; refatoração contínua ("O agente empilha
código"). Pesquisar alternativas antes de implementar e guardar a pesquisa em `docs/<tema>_plan.md`.
- https://akitaonrails.com/2026/03/05/meu-primeiro-fracasso-com-vibe-code-e-como-consertei-frank-yomik/

## Memória/documentação
`docs/` com um ficheiro por tema (arquitetura, decisões, armadilhas) e índice ligado do CLAUDE.md;
"O agente não vai fazer isso sozinho" — tem de ser pedido.
- https://akitaonrails.com/2026/05/18/memoria-agentes-karpathy-llm-wiki-agentmemory/

## Contradição a notar
Num post de fevereiro fala de um CLAUDE.md de 702 linhas como "documento vivo"; o modelo de abril tem < 100.
