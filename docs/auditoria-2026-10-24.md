# Auditoria de 2026-10-24 (ramo `exp/a`)

Pedido do Carlos antes do envio para o GitHub: auditoria de segurança, código, pastas, regras do projeto e
recomendações das documentações oficiais; depois, corrigir o que se encontrou, com um teste para cada problema.

**Como se fez:** quatro auditores em paralelo, só a ler (Python; páginas do Zebar; instalador e repositório;
código e regras), sem verem as conclusões uns dos outros. Cada achado foi marcado CONFIRMADO (seguido no código)
ou PLAUSÍVEL. A seguir, o plano de correções (F0–F7) foi aprovado pelo Carlos.

**Resultado geral:** nenhum problema crítico ou alto de segurança; nenhum segredo no histórico do git (53
commits, todos os ramos); nenhum XSS explorável (todos os dados de fora passam por `esc()` ou `textContent`);
`argsRegex` todos ancorados. Quase todas as "injeções" dependem de ficheiros que só o próprio utilizador
escreve, por isso não atravessam nenhuma fronteira de privilégio. O risco real era de **disponibilidade**:
um erro de escrita num ficheiro do utilizador parava o arranque inteiro.

**Estado:** `por corrigir` → `corrigido (commit)` / `risco aceite (motivo)`. A coluna F diz a fase do plano.

## Antes da auditoria (encontrado no teste real)

| Achado | Estado |
|---|---|
| Reinstalar com `nome =` vazio no `arranque.txt` mantido não perguntava o nome | corrigido (`dbb7f96`) |
| O instalador reiniciava o Explorador mesmo sem mudar nada e fechava as janelas de pastas abertas (A39) | corrigido (`14241f4`) |
| `instalacao.json` guardava como "antes" os nossos próprios valores numa reinstalação: o desinstalar deixava os ícones e a barra escondidos | corrigido (`14241f4`) |
| O GlazeWM rebentou ao arrancar logo a seguir à reinstalação (`0xc0000409`, 1 vez em 7 dias) e o arranque não tentou outra vez (A40) | F1 |

## Segurança

| # | Grav. | Onde | Achado | F | Estado |
|---|---|---|---|---|---|
| S1 | média | `instalar.ps1` + `instalar-programas.ps1` | Os instaladores são verificados (SHA-256/assinatura) como utilizador normal e corridos como administrador sem nova verificação, a partir de uma pasta que o utilizador pode escrever (TOCTOU). | F3 | por corrigir |
| S2 | média | `bar.html`, `sistema.html` | O provider glazewm deixa a página mandar `shell-exec` de qualquer programa: os `argsRegex` não são a fronteira (A43). Sem CSP, uma injeção futura seria execução de código. | F6 | por corrigir |
| S3 | baixa | `instalar.ps1` | Python 3.11.9 fixado: o ramo 3.11 já não tem binários com as correções de segurança. | F3 | por corrigir |
| S4 | baixa | `instalar.ps1` | `Unblock-File` recursivo em toda a pasta do pacote (se a pasta for Transferências, tira a marca da Internet de tudo). | F3 | por corrigir |
| S5 | baixa | `instalar.ps1` | Uma tarefa antiga que não se deixa substituir fica se o programa for igual, sem ver se corre elevada. | F3 | por corrigir |
| S6 | baixa | `instalar.ps1`, `desinstalar.ps1` | A `statusLine` é tida como nossa por conter `statusline.py`: troca/apaga a de outra pessoa sem guardar a anterior; gravação não atómica. | F3 | por corrigir |
| S7 | baixa | `instalar-programas.ps1` | A parte de administrador escreve num registo fixo do `%TEMP%` do utilizador. | F3 | por corrigir |
| S8 | baixa | `bat_tray.py` | `cmd.exe /c` com o caminho sem aspas: `&`, `%` num caminho partem o comando. | F2 | por corrigir |
| S9 | baixa | `bat_tray.py` | Parar/Reiniciar matam qualquer processo que escute na porta, com a árvore. | F2 | por corrigir |
| S10 | baixa | `bat_tray.py` | "Ver registo": `;` no título parte o comando do `wt`; `'` no caminho parte o PowerShell. "Abrir no navegador" abre qualquer alvo, não só http(s). | F2 | por corrigir |
| S11 | baixa | `morg_atalhos.py`, `morg_painel.py`, `apps-logica.mjs` | `web:` aceita espaços e flags do Chrome (`--gpu-launcher=…`); caminhos `.exe` sem aspas. | F2 | por corrigir |
| S12 | baixa | `zpack.json` (py.exe) | O Zebar aceita `env`/`cwd` em `shellExec` sem verificar; com `VIRTUAL_ENV` o `py` correria outro Python. | F2 | por corrigir |
| S13 | baixa | `morg_janelas_zebar.py` e outros | As janelas do Zebar são encontradas só pelo título (uma janela `chrome --app` com o mesmo título seria confundida). | F2 | por corrigir |
| S14 | info | `bar_helper.py` | Nada limpa `CLAUDECODE`/`CLAUDE_CODE_*`/`ANTHROPIC_*` do ambiente (A2 depende só da disciplina). | F2 | por corrigir |
| S15 | info | `.claude/hooks/*.py` | Os hooks são guardas, não fronteiras (dá para os contornar). | — | risco aceite: servem para lembrar o agente, não para travar um atacante |
| S16 | info | GlazeWM (externo) | O servidor IPC (`ws://127.0.0.1:6123`) não verifica a origem (PLAUSÍVEL, não testado). | — | risco aceite: é do GlazeWM; anotado em A43 |
| S17 | info | `uncloak.ps1` | Pode mostrar janelas de outros ambientes de trabalho virtuais. | — | risco aceite: efeito visual, não segurança |

**Verificado e sem problemas:** downloads por HTTPS com SHA-256 fixo (GlazeWM, Python) e Authenticode da
Microsoft (VC++); tarefa agendada `Limited`, `Interactive`, só para o utilizador; registo só em HKCU; nada se
apaga em definitivo (renomeia-se); junções sempre com `rmdir` (A10); `package-lock.json` com `integrity` em
tudo; `claude_usage.py`/`statusline.py` não leem o token OAuth nem vão à rede; nenhum `eval`/`exec`/`pickle`/
`shell=True`; mutexes e eventos em `Local\`; títulos de janela guardados só como hash; `-I` em todas as
chamadas ao Python.

## Robustez (o arranque parava)

| # | Grav. | Onde | Achado | F | Estado |
|---|---|---|---|---|---|
| R1 | média | `morg_config_arranque.py`, `claude_usage.py`, `morg_atalhos.py`, `morg_painel.py` | Um `arranque.txt`/`frases.txt`/`apps.txt` gravado em ANSI dá `UnicodeDecodeError` (um `ValueError`), que não é apanhado: o `boot` morre sem cortina, barra nem GlazeWM (A41). | F1 | por corrigir |
| R2 | média | `morg_arranque.py`, `bat_tray.py` | Uma porta errada numa linha `bat =` (`:30000a`) faz `u.port` lançar `ValueError` fora do `try`: o arranque para a meio (A42). | F1 | por corrigir |
| R3 | média | `morg_arranjo.py` | `layout.json` com JSON válido mas forma errada (lista, entrada sem `workspace`) rebenta o `boot` e o restauro. | F1 | por corrigir |
| R4 | média | `morg_atalhos.py`, `morg_painel.py` | `apps.txt` gravado sem ser atómico, com fins de linha diferentes conforme quem grava, e gravado antes de verificar os erros. | F1 | por corrigir |
| R5 | info | vários | `.tmp` com nome fixo (dois escritores ao mesmo tempo). Ficheiros corrompidos ignorados sem registo. | F1 | por corrigir |

## Regras do projeto e organização

| # | Prio. | Achado | F | Estado |
|---|---|---|---|---|
| Q1 | alta | Os 100 % de cobertura têm buracos não registados: `statusline.py`, os hooks, a lógica dentro dos `<script>` de `bar.html`/`splash.html`/`sistema.html`, `instalar-programas.ps1`, `uncloak.ps1`. | F4/F6 | por corrigir |
| Q2 | alta | As regras que os hooks invocam (500 linhas, 35 linhas por função, 100 %) não estão no `CLAUDE.md`. | F4 | por corrigir |
| Q3 | média | Funções com mais de 35 linhas sem exceção registada (`statusline.main`, `_BlackCover._run` com motivo caducado, `main` do splash, `renderWorkspaces`); nada verifica a regra. | F4/F6 | por corrigir |
| Q4 | média | `uncloak.ps1` sem BOM e com acentos (A16). | F4 | por corrigir |
| Q5 | baixa | `noqa` para regras do ruff que não estão ativas. | F4 | por corrigir |
| Q6 | média | `instalar.ps1` com 498 de 500 linhas; funções repetidas nos dois instaladores. | F3 | por corrigir |
| Q7 | média | Lógica repetida nas páginas (`esc` 3×, centrar ícones 4×, tabela de ícones 4×); `bar.html` e `splash.html` ainda pintam ícones em `<canvas>` (contra a A26/ADR 0006). | F6 | por corrigir |
| Q8 | baixa | Código morto (`first()` do splash, `GRANDES_POR_DIVIDIR`); testes a importar ajudantes de outros testes. | F4 | por corrigir |
| Q9 | média | `.gitattributes` não bate com os ficheiros (CRLF/LF misturados; já causou 2 incidentes). | F5 | por corrigir |
| Q10 | baixa | Hook dos testes sem `onFailure: block`; PSScriptAnalyzer sem definições (avisos falsos escondem os reais); `ruff` sem `target-version`; `package.json` sem `engines`; hash do `vendor/zebar-3.3.1.mjs` sem teste. | F4 | por corrigir |
| Q11 | média | Documentação desatualizada: "uma pergunta" (README, LEIA-ME, Tutorial), restos do BMP, 3 widgets em vez de 4, ícones em canvas, `morg_inicio.py` fora do mapa, caminhos pessoais em 3 docs, planos já cumpridos no índice. | F5 | por corrigir |

**Verificado e sem problemas:** `testar.ps1` verde a 100 % (258 + 45 + 72 testes); ruff e Biome limpos; só
biblioteca padrão; chaves do `config.yaml` iguais às do exemplo oficial do GlazeWM 3.10.1; todos os links
relativos dos `.md` existem.

## Aprendizados

Ficam em `armadilhas.md` (A39–A43) e, no fim, aqui um resumo do que mudou.
