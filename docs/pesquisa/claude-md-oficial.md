# CLAUDE.md segundo a documentação oficial da Anthropic

Pesquisa de 2026-10-23. Fontes oficiais atuais em `code.claude.com/docs/en/`. Marcação:
**[OFICIAL]** documentação atual · **[ANTIGO]** post de abril de 2025, marcado como "no longer maintained".

## Onde fica e como carrega [OFICIAL]
- Locais: política da organização, `~/.claude/CLAUDE.md` (pessoal), `./CLAUDE.md` ou `./.claude/CLAUDE.md`
  (projeto, no git), `./CLAUDE.local.md` (pessoal do projeto, no `.gitignore`).
- Os ficheiros da pasta atual e das de cima carregam no arranque; os de subpastas carregam quando o Claude
  mexe num ficheiro dessa subpasta. Todos se **somam**, nenhum substitui outro.
- Depois de `/compact`, o CLAUDE.md da raiz é relido do disco.
- Imports `@caminho/ficheiro.md`: no máximo 4 níveis; **não poupam contexto** (carregam junto).
  Para só mencionar um ficheiro sem o carregar: escrevê-lo entre crases.
- Comentários HTML `<!-- … -->` são retirados antes de chegar ao Claude (servem de notas para pessoas).
- `.claude/rules/*.md`: um tema por ficheiro; com `paths:` no cabeçalho YAML, só carregam quando o Claude
  lê/edita ficheiros que batem (ex.: regras só para `*.ps1`).
- O CLAUDE.md é **contexto, não configuração imposta**: o Claude pode não o cumprir.
- AGENTS.md só é lido se não houver CLAUDE.md (Claude Code v2.1.277+).
- Fontes: https://code.claude.com/docs/en/memory.md

## Tamanho e redação [OFICIAL]
- Alvo: **menos de 200 linhas** por CLAUDE.md; maior = mais contexto e menos cumprimento.
- Agrupar em títulos e listas. Instruções **concretas e verificáveis** ("Run `npm test` before committing",
  não "Test your changes").
- "IMPORTANT" só numa linha que o Claude insista em ignorar; ênfase em muitas linhas anula-se.
- Teste de corte para cada linha: "Would removing this cause Claude to make mistakes?" Se não, cortar.
- Incluir: comandos que o Claude não adivinha, estilo diferente do padrão, como testar, etiqueta do repo,
  decisões de arquitetura, armadilhas. Excluir: o que se percebe lendo o código, convenções padrão,
  documentação longa (pôr ligação), coisas que mudam muito, descrições ficheiro a ficheiro.
- Contradições entre regras: o Claude escolhe uma ao acaso → rever periodicamente.
- Fontes: https://code.claude.com/docs/en/best-practices.md, memory.md

## Quando usar outro mecanismo [OFICIAL]
- **Hook** (PreToolUse/Stop): para o que tem de acontecer **sempre** (bloquear um comando, correr testes antes
  de terminar). O CLAUDE.md é consultivo; o hook é determinístico. https://code.claude.com/docs/en/hooks-guide.md
- **Skill**: quando uma secção virou procedimento em vez de facto (SKILL.md < 500 linhas).
- **Regras com `paths`**: instruções que só valem para parte do código.

## Fluxo de trabalho [OFICIAL]
- Explorar → planear → implementar → commit; separar pesquisa e plano da implementação.
- Dar ao Claude algo que dê **passa/falha**; para um bug, "write a failing test that reproduces the issue,
  then fix it". Mostrar evidência em vez de afirmar sucesso. "If you can't verify it, don't ship it."
- Revisão por subagente num contexto limpo.
- Quando acrescentar ao CLAUDE.md: quando o Claude erra a mesma coisa duas vezes.

## [ANTIGO] TDD em quatro passos (post de 2025, não mantido)
Escrever testes a partir de pares entrada/saída → correr e confirmar que falham → commit dos testes →
implementar **sem alterar os testes**. https://www.anthropic.com/research/claude-code-best-practices

## Não encontrado na documentação oficial
Tamanho máximo de ficheiros de código, preservar comentários em refactors, ADR/CHANGELOG, organizar notas de
pesquisa, "dizer o que não conseguiu verificar" (o mais próximo: "show evidence").
