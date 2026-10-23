# Instalação, desinstalação e montagem do pacote

> Numeração das secções (§N) mantida do antigo `COMO-FOI-FEITO.md`; mapa em `docs/README.md`.

## 6. Instalação

### 6.1 Automática

Duplo clique em `INSTALAR.cmd`, com a sessão iniciada **na conta do utilizador final**. Ele corre `scripts\instalar.ps1`, que faz:

1. **Verifica:**
   - Windows 11 (build ≥ 22000);
   - `%USERPROFILE%` sem espaços (ver A6);
   - pacote numa pasta local (um admin elevado não vê unidades de rede mapeadas);
   - se está elevado, avisa e pede confirmação.

   No fim desta etapa faz `Unblock-File` a tudo.
1b. **Pergunta** (feita depois dos passos 2 e 3, logo antes da configuração; só se não houver já um `arranque.txt` de uma instalação anterior, e sem `-SemPerguntas`/`-Animacao`/`-Bat`): em ciclo, o caminho de cada `.bat`, o endereço e o nome (Enter vazio = terminar). A animação fica `cafe` (a única, por agora).

   Cada `.bat` é validado: tem de existir e ser `.bat` ou `.cmd`, e o endereço tem de começar por `http(s)://`. Se o `.bat` usa npm/node e o Node.js não está instalado, só avisa. Sem perguntas: `-Animacao cafe` e `-Bat "caminho|endereço|nome"` (vários separados por `;`).
2. **Programas em falta.** Os instaladores **não vêm no repositório**. Para cada programa em falta, usa o ficheiro de `1-instaladores\` se lá estiver e passar na verificação; senão **descarrega-o do site oficial** para lá e verifica-o. Um ficheiro que não passe **nunca** é executado (o `.part` é apagado e a instalação para).

   | Programa | Endereço oficial | Verificação |
   |---|---|---|
   | GlazeWM + Zebar | `github.com/glzr-io/glazewm/releases/download/v3.10.1/glazewm-v3.10.1.exe` | SHA-256 fixo (§7; igual ao `digest` publicado no release do GitHub) |
   | Python 3.11.9 | `www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe` | SHA-256 fixo (§7; o MD5 bate com o publicado em python.org) |
   | VC++ 2015-2022 x64 | `aka.ms/vs/17/release/vc_redist.x64.exe` | Assinatura Authenticode válida de `O=Microsoft Corporation` (a Microsoft atualiza o ficheiro no mesmo endereço, por isso não há hash fixo) |

   Sem internet: pôr os ficheiros com os nomes de §7 em `1-instaladores\` antes de correr. Depois corre `scripts\instalar-programas.ps1` com `-Verb RunAs` (**um** UAC). Esse script instala só o que falta:

   | Programa | Argumentos |
   |---|---|
   | VC++ | `/install /quiet /norestart` |
   | GlazeWM + Zebar | `/quiet /norestart` |
   | Python 3.11.9 | `/quiet InstallAllUsers=1 Include_launcher=1 InstallLauncherAllUsers=1 PrependPath=0 Include_test=0 Include_doc=0 Shortcuts=0` |

   Depois tira entradas Run ou Startup que mencionem glaze ou zebar. O Python é para todos os utilizadores porque, com UAC de outra conta, uma instalação "por utilizador" iria para o perfil do admin.
3. **Fonte.** Copia os 4 TTF para `%LOCALAPPDATA%\Microsoft\Windows\Fonts` e regista-os em `HKCU\…\Fonts` como `JetBrainsMono NF <estilo> (TrueType)`. Depois faz `AddFontResourceW` e `WM_FONTCHANGE`. Não precisa de admin.
4. **Configuração:**
   1. Se a GlazeWM estiver a correr, faz `wm-exit`; mata o Zebar.
   2. Uma `~\.glzr` existente passa a `~\.glzr.copia-<data>`.
   2b. Fecha os ajudantes Python ainda a correr (`pythonw` com `.glzr` na linha de comandos: café, ícones dos `.bat`) com os seus filhos (`taskkill /T`). Senão a tarefa lançaria uma segunda cópia de cada `.bat`, e a pasta podia não se deixar renomear.
   3. Copia `2-configuracao\glzr` para `~\.glzr`, trocando os marcadores (ver a tabela abaixo). Escreve UTF-8 sem BOM.
   4. O `arranque.txt` recebe a animação e as linhas `bat =` respondidas (ver o passo 1b).
   5. Numa reinstalação, recupera da cópia `apps.txt`, `layout.json`, `arranque.txt` (se não houve perguntas) e a pasta `arranque\`. Aceita também a estrutura antiga (pack `guia-atalhos` separado): os ficheiros vão para `omarchy-catppuccin\guia\`. Se o `arranque.txt` recuperado tiver uma animação que já não existe, passa a `cafe`.
   6. Falha se ficar algum `{{` por substituir.
   7. Cria a junction `Documentos\Guia de Atalhos` → `~\.glzr\zebar\omarchy-catppuccin\guia`.

   | Marcador | Valor | Exemplo |
   |---|---|---|
   | `{{HOME}}` | `%USERPROFILE%` com `/` | `C:/Users/joao` |
   | `{{HOME_RE}}` | o mesmo, escapado para regex dentro de JSON | — |
   | `{{ANIMACAO}}` | nome da animação (só em `arranque.txt`) | `cafe` |
5. **Apps.** Corre `py -I bar_helper.py apps-apply --skip-missing`.
6. **Claude Code**, se existir `~\.claude` ou `~\.local\bin\claude.exe`. Copia `statusline.py`; se havia um diferente, guarda-o como `.bak`. Junta `statusLine` ao `settings.json` com um script Python, **sem mexer** numa statusLine alheia.
7. **Windows.** `HideIcons=1` (exceto com `-ManterIcones`) e barra de tarefas a esconder-se (`StuckRects3`, byte 8 = 3; exceto com `-ManterBarraWindows`). Reinicia o Explorador. Guarda os valores anteriores em `instalacao.json`.
8. **Tarefa agendada** `GlazeWM (arranque)`:
   - ação: `C:\Windows\pyw.exe -I "<HOME>\.glzr\zebar\omarchy-catppuccin\bar_helper.py" boot`;
   - gatilho: AtLogOn do utilizador;
   - principal: o próprio utilizador, Interactive, RunLevel Limited;
   - definições: sem limite de tempo, `IgnoreNew`, `Priority 4`, a correr também com bateria.
9. Arranca a tarefa, exceto com `-NaoIniciar`.

### 6.2 À mão (se o script não puder correr)

Seguir exatamente os passos de §6.1, por ordem. Os pontos críticos:
- **Os marcadores têm de ficar todos trocados.** Os `argsRegex` do `zpack.json` (um por widget) têm de bater **exatamente** com os argumentos que as páginas e o GlazeWM passam; senão o Zebar recusa o comando, em silêncio. O caminho do `bar_helper.py` está na constante `PACK` de `bar.html`, na `HELPER` de `guia.html` e `sistema.html`, e escrito diretamente na chamada `splash-ready` de `splash.html`.
- **O bloco das apps fica vazio até correr `apps-apply`.** Sem ele, `Alt+Enter` não faz nada.
- **A tarefa tem de chamar `pyw.exe … boot`.** Não pode chamar `glazewm.exe` diretamente (ver A1).

### 6.3 Desinstalação

`DESINSTALAR.cmd` → `scripts\desinstalar.ps1`, que faz:

1. Remove a tarefa.
2. Fecha o GlazeWM, o Zebar e os `pythonw` cuja linha de comandos contém `.glzr`.
3. Corre `uncloak.ps1`.
4. Repõe `HideIcons` e a barra de tarefas a partir de `instalacao.json`.
5. Tira a `statusLine` do Claude Code, só se for a nossa.
6. Remove a junction com `cmd /c rmdir` (ver A10).
7. **Move** `~\.glzr` para `~\.glzr.removido-<data>`. Nunca apaga.

Os programas ficam instalados.

## 7. Como o pacote foi montado

Os três `.exe` **não estão no repositório** (estão no `.gitignore`): o instalador descarrega-os (§6.1, passo 2). Os nomes abaixo são os que ele procura em `1-instaladores\`.

| Peça | Origem | SHA-256 |
|---|---|---|
| `GlazeWM-3.10.1-com-Zebar.exe` | `github.com/glzr-io/glazewm/releases/download/v3.10.1/glazewm-v3.10.1.exe` (o instalador oficial já traz o Zebar 3.3.1) | `469F8675F5AD1353BDA9CEDE7CBB0E320E1B9A1D5657DA709B60A51D86E95020` |
| `Python-3.11.9-amd64.exe` | `www.python.org/ftp/python/3.11.9/python-3.11.9-amd64.exe` (MD5 publicado: `e8dcd502e34932eebcaf1be056d5cbcd`) | `5EE42C4EEE1E6B4464BB23722F90B45303F79442DF63083F05322F1785F5FDDE` |
| `VisualC++-Redistribuivel-x64.exe` | Microsoft (VC++ 2015-2022 x64, `aka.ms/vs/17/release/vc_redist.x64.exe`). Muda de versão no mesmo endereço. | verificado pela assinatura da Microsoft |
| `JetBrainsMonoNerdFont-{Regular,Medium,SemiBold,Bold}.ttf` (no repositório, com `OFL.txt`) | Nerd Fonts, release `JetBrainsMono.zip` | Regular `C8AF9DFD…6925F`, Medium `F7523DBC…1C76A`, SemiBold `387FD979…A40E1`, Bold `546D7F5E…0B8DA` |
| `vendor\zebar-3.3.1.mjs` | `npm i zebar@3.3.1` + `esbuild --bundle --format=esm`, num só ficheiro, para não depender de CDN. A versão tem de bater com o `zebar.exe` (3.0 não tinha `tauriWindow`). **Uma só cópia**: o Zebar só serve a cada página ficheiros de dentro da pasta do seu pack que batam com o `includeFiles` (código do Zebar 3.3.1: `asset_server.rs`, `widget_factory.rs`); por isso todas as páginas estão no mesmo pack. | `E160BB83…1929FA` |
| `cafe.bmp` | `scripts\gerar-cafe-bmp.ps1`: desenha com System.Drawing (GDI+) a mesma geometria do `<svg id="cafe">`, sem vapor, a 280×280, em BMP 24-bit, em fundo preto. Não precisa de navegador. | — |
| `2-configuracao\` | `scripts\gerar-modelos.ps1` no PC onde se mantém a configuração (ver abaixo). | — |

**Atualizar o pacote depois de mudar a configuração ativa (`~\.glzr`):** correr `scripts\gerar-modelos.ps1`. Ele:
1. confirma que todos os ficheiros da lista existem em `~\.glzr` (senão para **sem apagar nada**) e copia-os. Ficam de fora logs, ficheiros com ponto (estado), `progress.json`, `layout.json` e `__pycache__`;
2. troca a pasta do utilizador por `{{HOME}}` ou `{{HOME_RE}}` (nos `zpack.json`); o `arranque.txt` pessoal **não** vai, e em seu lugar vai `scripts\arranque-modelo.txt`;
3. esvazia o bloco das apps;
4. copia `~\.claude\statusline.py`.

**Ficheiro novo no `.glzr`?** Acrescentá-lo à lista `$files` do `gerar-modelos.ps1`.

**Validação usada:** aplicar a substituição do instalador a uma pasta temporária com o próprio utilizador. Os ficheiros saem iguais byte a byte aos ativos; só difere o bloco das apps. Depois correr `apps-apply --skip-missing` nessa cópia (com `USERPROFILE` a apontar para ela e `python.exe` direto, porque o lançador `py.exe` falha com o `USERPROFILE` trocado). O `config.yaml` resultante fica igual ao ativo, exceto as apps em falta, que ficam comentadas.
