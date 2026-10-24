# Arranque do Windows: o que se aprendeu (início de sessão, cortina, ecrã de boas-vindas)

Pesquisa de 2026-10-24, neste PC: Windows 11 Pro 26200, ecrã 1920×1080 a 125 %, Python 3.11.9 e Zebar 3.3.1.
As fontes são a documentação da Microsoft e o código do Zebar (lido com `gh api`). As medições vêm dos registos
reais. O que for suposição está marcado.

## 1. Linha do tempo de um início de sessão (medida sem administrador)
| Evento | Onde se lê | Exemplo (13:21) |
|---|---|---|
| Autenticação | Winlogon/Operational, evento 1 | 03.080 |
| Início de sessão | System, evento 7001 | 03.116 |
| `explorer.exe` criado | hora de criação do processo (`GetProcessTimes`) | 03.990 (ainda está o "Bem-vindo") |
| **O ambiente de trabalho aparece** | Microsoft-Windows-Shell-Core/Operational 9648/9649 (WaitForDesktopVisuals → **SignalDesktopSwitch**) | 06.370 |
| `pythonw` da tarefa criado | hora de criação do processo | 06.418 |
| 1.ª linha do nosso código (`morg_inicio.T_INICIO`) | registo `.layout-restore.log`, linha "medição" | 11.991 (**+5,6 s, CPU ≈ 0**) |
| `boot()` e a cortina | idem | 12.630 / 12.653 |

- **A referência certa é o `SignalDesktopSwitch`**, não a criação do explorador: o papel de parede só se vê a
  partir daí.
- O registo `Microsoft-Windows-TaskScheduler/Operational` vem **desligado** de origem: ligá-lo é uma definição do
  sistema, que não mudámos.

## 2. A paragem de ~5 s depois do ambiente de trabalho aparecer (por resolver)
- **O que se viu.** Logo a seguir ao `SignalDesktopSwitch`, os processos novos ficam uns segundos parados quase
  sem CPU:
  - o `pythonw` ficou 5,6–9,6 s antes da 1.ª linha (3 medições);
  - o PowerToys, nativo em C++ e lançado também por uma tarefa de logon, ficou 3,65 s antes da 1.ª linha do
    registo dele.
- **O que já foi descartado:**
  - **o nosso código:** os módulos carregam em 0,04 s a quente e 0,6 s nesse arranque;
  - **o Python:** a quente arranca em 14 ms e o lançador `pyw.exe` acrescenta ~12 ms;
  - **DLLs injetadas no `pythonw`:** não há; só carrega o `python311`, o `vcruntime` e DLLs do sistema;
  - **o disco:** um terminar sessão (morno) foi mais lento do que um reinício a frio;
  - **a prioridade:** a tarefa tem `Priority 4` (normal) e o `boot` põe `NORMAL_PRIORITY_CLASS`.
- **O que corre ao mesmo tempo:** o WebView2 da Pesquisa e do Iniciar, o Raycast (com node), o Lenovo Vantage, o
  nvcontainer, o SearchIndexer, componentes do Defender ainda a arrancar (DefenderAiPlatformHost, NisSrv), e as
  apps da chave Run (Steam, Razer, Riot, Spotify, Edge).
- **Suposição, ainda não provada:** espera de I/O e da análise do antivírus na abertura de ficheiros. Essa análise
  corre no MsMpEng, por isso o nosso processo fica a 0 de CPU.
- **O atraso das "apps de arranque"** (`HKCU\...\Explorer\Serialize\StartupDelayInMSec`) só está documentado para a
  pasta Arranque e para a chave Run, não para tarefas agendadas. Neste PC a chave `Serialize` não existe.
- **Como diagnosticar (ferramenta oficial, já vem com o Windows), como administrador:**
  ```
  wpr -boottrace -addboot GeneralProfile -filemode
  ```
  Reiniciar. Depois de entrar:
  ```
  wpr -boottrace -stopboot arranque.etl "fundo à vista ao entrar"
  ```
  Fonte: [WPR Command-Line Options](https://learn.microsoft.com/en-us/windows-hardware/test/wpt/wpr-command-line-options).
  O `-addboot` só escreve a configuração do autologger; o traço começa no arranque seguinte. O `-cancelboot`
  desfaz. O `.etl` lê-se com o WPA, ou em texto com o `tracerpt arranque.etl -o arranque.xml` (também vem com o
  Windows).

## 3. O que se tentou para tapar o fundo e porque saiu
- **Protetor de ecrã "Em branco"** (`C:\Windows\System32\scrnsave.scr /s`), lançado por uma 2.ª tarefa de logon,
  "Morg Keys (ecrã preto)".
  - Testado a quente:
    - está assinado pela Microsoft e fica visível em 12–24 ms, `topmost`, em ecrã inteiro;
    - fecha com `WM_CLOSE`;
    - **não bloqueia a sessão**, porque o bloqueio só acontece quando é o Winlogon a lançá-lo;
    - a classe da janela vem traduzida ("Proteção de Tela em Branco"): para o encontrar, procura-se pelo processo.
  - **No início de sessão real não resolveu** (teste do utilizador): provavelmente fica preso na mesma paragem. Saiu.
- **As ações de uma tarefa agendada correm em sequência** ("are executed sequentially"). Uma ação que não termina
  (como o `.scr`) prende as seguintes; por isso era preciso uma tarefa à parte.
- **Papel de parede preto:** recusado pelo utilizador ("mal feito").

## 4. A cortina nativa que escurece (`morg_cortina.py`)
- É uma janela em camadas: `WS_EX_LAYERED` mais
  [`SetLayeredWindowAttributes`](https://learn.microsoft.com/en-us/windows/win32/api/winuser/nf-winuser-setlayeredwindowattributes)
  `(hwnd, 0, alfa, LWA_ALPHA = 0x2)`. Com alfa 0 fica totalmente transparente, com 255 opaca.
- Nasce escondida, com alfa 0. Depois `ShowWindow(SW_SHOWNOACTIVATE)` e um `SetTimer` de 16 ms que sobe o alfa até 255
  em 1,2 s, em *ease-out* (função `_alfa`, testada).
- Medido no ecrã: o brilho médio do ecrã foi 88 → 67 → 31 → 11 → 1 → 0 aos 0,1/0,35/0,6/0,9/1,5 s, e voltou a 86
  ao fechar.
- **DPI:** um `pythonw` sem perceção de DPI vê 1536×864 a 125 %. Com
  `SetThreadDpiAwarenessContext(-4)` (por monitor, v2) só nessa thread, `GetSystemMetrics` dá os 1920×1080 físicos.
- Antes a cortina desenhava um BMP do 1.º quadro da chávena (A21). Com o escurecer e a chávena só no HTML, o BMP
  deixou de ser preciso, e com ele o acerto de geometria.

## 5. A passagem cortina → ecrã de boas-vindas sem piscar
- **Zebar 3.3.1** (`widget_factory.rs` l.314–347): a janela do widget nasce **visível**, antes de a página carregar.
  Só depois leva `set_always_on_top` e o tamanho. Com `transparent: true`, o que o WebView2 ainda não pintou
  deixa ver o que está por baixo.
- **Um `setTimeout` não garante que algo já foi pintado:** os temporizadores correm mesmo com a página tapada ou
  sem quadros. O `requestAnimationFrame` só corre quando o renderizador está mesmo a produzir quadros.
  - Por isso a página só avisa `splash-ready` no fim da transição, depois de 2 quadros e mais 50 ms.
  - Há uma rede de segurança de 4 s.
- Enquanto espera, o `boot` põe o splash por cima da cortina a cada 100 ms (`_splash_to_top`): tapado, o WebView2
  não pinta. Antes de fechar a cortina faz 2 `DwmFlush`.

## 6. Ecrã de boas-vindas
- A chávena entra (CSS `@keyframes`, 700 ms). Depois aparecem:
  - "Muito bem-vindo, {nome}" (`nome =` no `arranque.txt`; o instalador pergunta);
  - a hora (`Intl.DateTimeFormat('pt-PT')`, como o relógio da barra);
  - a frase do dia (`frases.txt`, 31 linhas `frase | personagem | obra`, escolhida pelo dia do mês em
    `_frase_do_dia`).
- O nome e a frase chegam à página no `progress.json`. A pré-visualização é `arranque/splash.html?preview` no
  servidor `pack-preview`.
- **Nome por omissão:** `UserPrincipal.Current.DisplayName`. Numa conta local sem nome completo vem vazio (é o caso
  deste PC, com `USERNAME` = "Usuario"). Nesse caso a saudação fica "Muito bem-vindo", sem nome.

### Fontes das frases (por ordem de linha do `frases.txt`)
Traduções curtas, com a atribuição. Quase todas vêm da Wikiquote em inglês (`en.wikiquote.org/wiki/<obra>`).
- **1–2:** Naruto; Naruto: Shippūden.
- **3–4:** One Piece.
- **5:** Fullmetal Alchemist.
- **6:** Fullmetal Alchemist: Brotherhood (anime).
- **7:** Cowboy Bebop.
- **8:** Hunter × Hunter.
- **9:** Spirited Away.
- **10–11:** Neon Genesis Evangelion.
- **12:** Attack on Titan.
- **13:** Code Geass.
- **14–15:** Princess Mononoke.
- **16:** The Wind Rises.
- **17–18:** Bleach (manga).
- **19:** Gintama.
- **20–21:** Trigun.
- **22:** Samurai Champloo.
- **23:** Vinland Saga — Goodreads (mangá, vol. 1).
- **24–25:** Demon Slayer — The Movie: Infinity Castle (Wikiquote).
- **26:** Rurouni Kenshin.
- **27:** Hikaru no Go.
- **28–30:** Goodreads, enviadas por leitores:
  - Your Lie in April;
  - Frieren (falante não indicado na fonte; atribuída à Frieren);
  - Haikyuu!! vol. 9.
- **31:** Death Note.

## 7. Cuidados com ferramentas deste PC
- **Fins de linha.** O `Path.write_text` do Python no Windows troca `\n` por `\r\n`, e o `sed -i` do Git Bash troca
  CRLF por LF. Num ficheiro com estragos de várias linhas, isto faz os estragos "escaparem" porque deixam de se
  aplicar.
  - Gravar com `write_bytes`.
  - Ver o `file` antes e depois.
- **Variáveis do PowerShell não distinguem maiúsculas** (A37). Um `foreach ($nome …)` no código dos testes deixou
  `$nome` visível ao instalador, que tem o parâmetro `-Nome`.
