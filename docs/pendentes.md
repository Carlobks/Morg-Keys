# Pendentes (por ordem)

Trabalho combinado com o utilizador e ainda não feito. Quando um item começa, ganha plano próprio (ou ADR);
quando acaba, sai daqui.

1. **Experiência 0001 — cobertura A contra C** (em curso): `experiencias/0001-cobertura-a-vs-c.md`.

Depois da experiência:

2. **Quota do Claude Code na barra** (pedido de 2026-10-23): melhorar a ligação ou, em alternativa, dar
   opção de a ocultar. Hoje o `claude_usage.py` só lê `~/.claude/rate_limits.json`, que o
   `~/.claude/statusline.py` escreve quando uma sessão do Claude Code **no terminal** recebe `rate_limits`;
   a aplicação de ambiente de trabalho não corre a statusLine, por isso os valores ficam desatualizados
   (a barra mostra a idade). Investigar uma fonte mais direta; se não houver, opção de ocultar.
   **Pedido de 2026-10-23:** ver se dá para usar o projeto de código aberto do Fabio Akita
   https://github.com/akitaonrails/ai-usagebar no Morg Keys, ou aprender como ele obtém o uso do Claude e
   replicar. Verificar: licença (compatível com GPL-3.0?), de onde lê os dados (API oficial, ficheiros locais
   do Claude Code, sessão do claude.ai), se corre no Windows, dependências, e como encaixaria na barra do Zebar
   (o `claude_usage.py` só pode usar a biblioteca padrão do Python).
3. **Fundo à vista no arranque** (9,3 s = 3,3 s até a tarefa criar o `pythonw` + 5,8 s do Python a frio).
   **Investigado em 2026-10-29:** o mesmo código, noutro PC (Windows 11, tarefa com `Priority 4` e sem atraso), dá
   **1,0 s** (0,04 s até ao `pythonw` + 0,9 s de Python com os 15 módulos). A causa está no PC lento, não no código.
   Feito: o instalador já não aceita uma tarefa antiga com prioridade ≠ 4 ou com atraso, e a cortina abre antes de
   importar os outros módulos (`abrir_cedo`). **Falta**, no PC lento, ver qual destas é (só leitura):
   - tarefa: `schtasks /query /tn "GlazeWM (arranque)" /xml | Select-String 'Priority|Delay|LogonType'` (esperado:
     `Priority 4`, sem `Delay`);
   - Python: `py -0p` (o `pyw.exe` usa o marcado com `*`; o da Microsoft Store arranca mais devagar a frio);
   - medição depois de reiniciar: as linhas `medição:` do `.layout-restore.log`;
   - carga do arranque do Windows: Gestor de Tarefas > Aplicações de arranque; outro antivírus além do Defender.
   Se nada disto explicar: decidir fundo preto e/ou cortina sem Python.
4. **Ícone de bateria na barra**, só se o PC tiver bateria.
5. **Bug antigo (encontrado na fase 2a):** `bar_helper.py` sem argumentos (ou com um comando desconhecido)
   imprime a ajuda e rebenta num terminal cp1252 por causa do carácter "✕" (`UnicodeEncodeError`). Corrigir
   com teste de regressão (ex.: escrever em UTF-8 ou trocar o carácter).
6. **Desinstalar incompleto** (encontrado em 2026-10-24): o `desinstalar.ps1` não tira as pastas do próprio
   Zebar (`%APPDATA%\zebar` e `%LOCALAPPDATA%\com.glzr.zebar`, com a cache do WebView2). Movê-las para
   `.removido-<data>`, como faz com a `~\.glzr`, e testar com Pester.
7. **Aviso "sem a app: claude-code"** em todas as instalações deste PC, com o Claude Code instalado. Ver
   porque o `apps-apply` não o encontra.
8. **Confirmação do utilizador** do painel `Alt+Esc, C` depois das correções A25 (foco) e A26 (ícones).
