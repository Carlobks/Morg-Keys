# TDD com agentes, cobertura e código difícil de testar

Pesquisa de 2026-10-23.

## TDD com agentes
- **Kent Beck** ("augmented coding"): `plan.md`, red → green → refactor; "Never mix structural and behavioral
  changes in the same commit"; commit só com testes verdes. Sinal de alarme: o agente apagar ou desligar
  testes. https://newsletter.kentbeck.com/p/augmented-coding-beyond-the-vibes
- **Simon Willison**: escrever o teste, **confirmar que falha**, depois implementar — um teste que passa antes
  da implementação não prova nada. https://simonwillison.net/guides/agentic-engineering-patterns/red-green-tdd/
- **Anthropic**: para um bug, teste que o reproduz primeiro. https://code.claude.com/docs/en/best-practices
- **Akita**: cada bug corrigido leva teste de regressão (ver metodo-akita.md).

## 100 % de cobertura — o que dizem as referências
- **Martin Fowler**: "I would be suspicious of anything like 100%"; código bem testado anda nos 80 altos/90.
  https://martinfowler.com/bliki/TestCoverage.html
- **Google** (via fontes secundárias; o post original não abriu): 60 % aceitável, 75 % louvável, 90 % exemplar;
  perseguir 100 % dá falsa segurança. https://testing.googleblog.com/search/label/Marko%20Ivankovi%C4%87
- **Akita**: > 80 %, 95 %+ na lógica de negócio.
- Mais forte do que cobertura: **testes de mutação** (a Google usa-os na revisão de código).
  https://research.google/pubs/state-of-mutation-testing-at-google/
- Conclusão para este projeto: 100 % das linhas e ramos **da lógica testável**; a cola com o sistema
  (Win32/ctypes, WebView2, GlazeWM, arranque) isolada, excluída com o motivo escrito e listada no que se
  valida à mão. Cobertura de 100 % não prova correção: os testes têm de falhar quando o código está errado.

## Código difícil de testar (Win32, interface)
- **Humble Object** (Fowler): tirar o máximo de lógica do elemento difícil de testar; o que sobra é cola fina.
  https://martinfowler.com/bliki/HumbleObject.html
- Prática: injetar os wrappers de sistema (ctypes, subprocess, ficheiros) nas funções → testáveis com mocks.

## Não verificado
Ferramentas de mutação para Python/JS (mutmut, Stryker) não foram avaliadas.
