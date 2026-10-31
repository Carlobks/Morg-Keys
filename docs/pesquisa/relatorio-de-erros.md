# Relatório de erros para uma issue no GitHub (2026-10-31)

**Pergunta:** o que tem de levar o relatório que o Morg Keys grava quando algo falha, para quem o mantém o poder
corrigir a partir de uma issue no GitHub, sem levar dados pessoais a mais?

## Fontes (lidas a 2026-10-31)

- **OpenTelemetry, convenções semânticas das exceções** (o padrão aberto da CNCF, usado pela Google, pela Microsoft
  e pela AWS): [exceptions-logs](https://opentelemetry.io/docs/specs/semconv/exceptions/exceptions-logs/).
  - Uma exceção regista-se com `exception.type`, `exception.message` (pelo menos um dos dois) e
    `exception.stacktrace` (recomendado, no formato natural da linguagem).
  - A gravidade segue o impacto: FATAL quando a app pára, ERROR quando não pára, WARN quando era esperada.
  - O próprio padrão avisa que a mensagem "pode conter informação sensível".
- **IETF RFC 9457, Problem Details** (o padrão da IETF para descrever um erro):
  [rfc9457](https://www.rfc-editor.org/rfc/rfc9457.html).
  - Separa o **tipo** do problema (`type` e `title`, estáveis entre ocorrências) da **ocorrência** (`detail` e
    `instance`).
  - Avisa que a informação tem de ser revista antes de sair, porque pode ajudar um atacante ou expor a privacidade
    de quem usa, e que não se devem expor detalhes internos como o stack trace numa resposta.
- **Mozilla, guia para escrever um bug** (Bugzilla):
  [bug-writing](https://bugzilla.mozilla.org/page.cgi?id=bug-writing.html).
  - Um resumo curto e único, a versão, o sistema operativo e o build.
  - Passos para reproduzir numerados, com a frequência.
  - O resultado esperado e o que aconteceu, separados de suposições.
  - Nos crashes: o stack trace e a assinatura.
- **GitHub, formulários de issue**:
  [syntax-for-issue-forms](https://docs.github.com/en/communities/using-templates-to-encourage-useful-issues-and-pull-requests/syntax-for-issue-forms).
  - Ficam em `.github/ISSUE_TEMPLATE/*.yml`, com `name`, `description` e `body`.
  - Campos `textarea`, `input`, `dropdown`, `checkboxes` e `upload`.
  - `render: shell` formata o registo colado como código.
- **Python, `faulthandler` e `sys.excepthook`**
  ([faulthandler](https://docs.python.org/3/library/faulthandler.html)):
  - o `faulthandler` escreve o traceback de todas as threads num ficheiro quando o processo morre (ex.: um erro em
    C pelo ctypes) ou fica preso;
  - o `sys.excepthook` recebe as exceções que chegam ao topo sem ninguém as apanhar.
- **Microsoft, Windows Error Reporting**
  ([windows-error-reporting](https://learn.microsoft.com/en-us/windows/win32/wer/windows-error-reporting)).
  O relatório só sai com o consentimento de quem usa, que escolhe por aplicação; um administrador pode mudar isso.
- **RGPD, artigo 5.º, n.º 1, alínea c)** (minimização dos dados): só os dados necessários para a finalidade.
  Citado de memória; não foi relido hoje.

## O que se concluiu: o que o relatório leva

Juntando as fontes, um relatório do Morg Keys leva, por esta ordem:

1. **Resumo:** o que falhou, numa linha (o "tipo" da RFC 9457): ex. `bar_helper panel do: KeyError`.
2. **Quando e onde:** a hora em ISO 8601 com o fuso, a versão do Morg Keys (o ramo e o commit do instalador), a do
   Windows (`platform.version()`), a do Python, e as do GlazeWM e do Zebar.
3. **O que estava a fazer:** o subcomando e os argumentos do `bar_helper.py`. Os argumentos em base64 do painel
   ficam de fora, porque podem levar nomes de apps.
4. **A exceção** (OpenTelemetry): `exception.type`, `exception.message` e `exception.stacktrace`, com a gravidade.
5. **Contexto curto:** as últimas linhas do registo do arranque (`.layout-restore.log`), se o erro for no arranque.
6. **Para preencher por quem envia** (Mozilla): os passos para reproduzir, o que esperava e o que aconteceu.

**Limpeza antes de gravar** (RFC 9457, OpenTelemetry e RGPD):
- a pasta pessoal passa a `~`;
- o nome da conta do Windows e o nome do `arranque.txt` passam a `<utilizador>`;
- os títulos de janelas e os nomes de documentos não entram: o relatório leva os nomes dos processos e mais nada.

**Consentimento** (WER): o relatório nunca sai sozinho. O popup mostra o resumo e pergunta onde guardar; quem usa
lê o ficheiro antes de o juntar a uma issue. O popup pode ser desligado no `arranque.txt`.

**Issue:** um formulário `.github/ISSUE_TEMPLATE/erro.yml` com os campos acima e um campo `render: shell` onde se
cola o relatório.

## O que não se verificou

- **A ISO/IEC/IEEE 29119-3**, que define o relatório de incidente nos testes de software: a página da ISO recusou
  o acesso (403), por isso a norma não foi lida e não se cita nenhum campo dela.
- **O formato do `faulthandler` num erro dentro do ctypes no Windows** não foi provado aqui. Prova-se com um teste
  que provoca um erro falso.
- **Se o `MessageBoxW` aparece por cima de um jogo em ecrã inteiro.** Fica para o teu teste real.
