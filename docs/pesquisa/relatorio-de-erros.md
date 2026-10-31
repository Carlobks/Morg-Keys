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

## Adenda (2026-10-31): o nome do Windows no relatório

**Pergunta:** o 1.º relatório real dizia "Windows-10-10.0.26200" num Windows 11. Porquê, e como se escreve o nome
certo?

**Fontes (lidas a 2026-10-31):**
- **Microsoft, [Operating System Version](https://learn.microsoft.com/en-us/windows/win32/sysinfo/operating-system-version)**:
  a tabela dá o Windows 11 e o Windows 10 com o mesmo número, `10.0`. A página recomenda testar a funcionalidade
  que se quer usar, e não a versão do sistema.
- **Microsoft, [Windows 11 release information](https://learn.microsoft.com/en-us/windows/release-health/windows11-release-information)**:
  a tabela de lançamentos começa no build 22000 (21H2); nenhum build do Windows 11 é mais baixo.
- **Microsoft Q&A, [How to differentiate between Windows 10 and Windows 11](https://learn.microsoft.com/en-us/answers/questions/605991/how-to-differentiate-between-windows-10-and-window.html)**
  e **[Win32 API to detect Windows 11](https://learn.microsoft.com/en-us/answers/a/556672)**, e a
  **[comunidade da Dell](https://www.dell.com/community/Windows-11/Windows-11-some-apps-called-Windows-10/m-p/8077452)**:
  respostas da comunidade que usam o build 22000 como limite.

**O que se mediu neste PC** (Windows 11 25H2):
- o `platform.platform()` do Python 3.11.9 dá `Windows-10-10.0.26200-SP0`;
- o `sys.getwindowsversion()` dá `major=10, minor=0, build=26200`;
- o registo (`HKLM\SOFTWARE\Microsoft\Windows NT\CurrentVersion`) dá `ProductName = Windows 10 Pro`,
  `DisplayVersion = 25H2`, `CurrentBuild = 26200` e `UBR = 9457`.

**O que não se verificou:** se as versões mais novas do Python (3.12 em diante) já escrevem "11". Não importa aqui,
porque o Morg Keys usa o Python que estiver instalado.

**Conclusão:**
- o relatório escreve "Windows 11 (build 26200.9457, 25H2)" quando o `CurrentBuild` é 22000 ou mais, e
  "Windows 10 (build …)" abaixo. Se o registo não se ler, fica o `platform.platform()`;
- o limite 22000 é um facto da tabela oficial de lançamentos, mas usá-lo para distinguir os dois sistemas é uma
  **prática da comunidade, não uma recomendação da Microsoft**. Na conversa de 2026-10-31 escrevi que era "a regra
  que a própria Microsoft recomenda", e isso estava errado;
- aqui o nome é só um rótulo para quem lê o relatório e não decide nada no código, por isso a recomendação da
  Microsoft (testar a funcionalidade) não se aplica.
