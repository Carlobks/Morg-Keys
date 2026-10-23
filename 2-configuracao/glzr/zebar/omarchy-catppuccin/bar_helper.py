"""Ações da barra do Zebar e dos atalhos do GlazeWM que precisam do Windows.

  awake status    -> imprime "on" ou "off"
  awake toggle    -> liga/desliga o "não suspender" e imprime o novo estado
  awake off       -> desliga (usado ao fechar o GlazeWM)
  awake-hold      -> (interno) processo que mantém o PC acordado
  quick           -> carrega Win+A (Definições Rápidas: volume, Wi-Fi, Bluetooth)
  guide           -> Alt+K: mostra o guia de atalhos; se estiver visível, fecha-o
  guide-hide      -> esconde o guia (usado pela página: Esc, ✕, clicar fora)
  guide-ensure-hidden -> arranque: garante que o guia pré-carregado fica escondido
  bar toggle      -> Alt+Shift+Espaço: esconde/mostra a barra do Zebar
  restore-min     -> Alt+Shift+M: restaura a janela minimizada mais recente
  layout-save     -> grava em que workspace está cada janela (camada Alt+Esc, G)
  layout-restore  -> no arranque do GlazeWM: abre as apps e repõe o arranjo
  boot            -> arranque do PC: ecrã de arranque + barra + GlazeWM + apps + programas
                     .bat de arranque.txt (tarefa agendada)
  splash-ready    -> (interno) a página do ecrã de arranque avisa que já está desenhada
  animacao tap    -> Alt+Esc, E: tocar passa à animação seguinte (sem mostrar);
                     segurar mostra a escolhida ao largar a tecla
  animacao next   -> passa à animação seguinte (cafe -> ...) e mostra-a
  animacao <nome> -> escolhe essa animação (cafe, ...) e mostra-a
  animacao preview-> mostra a animação atual uns segundos
  apps-apply      -> Alt+Shift+R: aplica apps.txt (atalhos das apps) e recarrega
                     (--skip-missing: na instalação, comenta as apps que não existem)
  apps-edit       -> abre apps.txt no editor de texto
  panel           -> Alt+Esc, C: mostra o painel "Apps e arranque" (painel/apps.html)
  panel-hide      -> esconde esse painel
  panel state|apps|undo|do <b64> -> pedidos da página do painel (respondem em JSON)
  layer-show      -> mostra o painel de letras da camada Alt+Esc
  layer-hide      -> esconde esse painel
  on-exit         -> saída do GlazeWM: lança "after-exit" fora do job e sai
  after-exit      -> (interno) espera o GlazeWM terminar, desliga o "não
                     suspender" e volta a mostrar janelas escondidas
  lock            -> bloqueia o PC
  power reboot    -> pede confirmação e reinicia
  power shutdown  -> pede confirmação e desliga

Chamado por C:/Windows/pyw.exe (atalhos) ou C:/Windows/py.exe (barra), o
lançador oficial do Python: escolhe a versão instalada, por isso atualizar o
Python não parte nada.
"""

import sys
from pathlib import Path

# Com `py -I` (como os atalhos e a barra o chamam) a pasta deste ficheiro NÃO entra no sys.path:
# sem isto os módulos morg_*.py não se importam.
sys.path.insert(0, str(Path(__file__).resolve().parent))

from morg_acoes_windows import after_exit, lock, on_exit, power, quick_settings  # noqa: E402
from morg_acordado import awake_hold, awake_off, awake_status, awake_toggle  # noqa: E402
from morg_animacao import animacao_preview, animacao_set, animacao_tap  # noqa: E402
from morg_arranjo import layout_restore, layout_save  # noqa: E402
from morg_arranque import boot  # noqa: E402
from morg_atalhos import apps_apply, apps_edit  # noqa: E402
from morg_ecra_arranque import splash_ready  # noqa: E402
from morg_glaze import restore_minimized  # noqa: E402
from morg_janelas_zebar import (  # noqa: E402
    bar_toggle,
    guide,
    guide_ensure_hidden,
    guide_hide,
    layer_hide,
    layer_show,
)
from morg_painel import panel_cli, panel_hide, panel_show  # noqa: E402


def main(argv):
    cmd = argv[1:] or [""]
    if cmd == ["awake", "status"]:
        print(awake_status())
    elif cmd == ["awake", "toggle"]:
        print(awake_toggle())
    elif cmd == ["awake", "off"]:
        print(awake_off())
    elif cmd == ["awake-hold"]:
        awake_hold()
    elif cmd == ["quick"]:
        quick_settings()
    elif cmd == ["guide"]:
        guide()
    elif cmd == ["guide-hide"]:
        guide_hide()
    elif cmd == ["guide-ensure-hidden"]:
        guide_ensure_hidden()
    elif cmd == ["bar", "toggle"]:
        bar_toggle()
    elif cmd == ["restore-min"]:
        restore_minimized()
    elif cmd == ["layout-save"]:
        layout_save()
    elif cmd == ["layout-restore"]:
        layout_restore()
    elif cmd == ["boot"]:
        boot()
    elif cmd == ["splash-ready"]:
        splash_ready()
    elif cmd[0] == "animacao" and len(cmd) <= 2:
        if len(cmd) == 2 and cmd[1] == "preview":
            animacao_preview()
        elif len(cmd) == 2 and cmd[1] == "tap":
            animacao_tap()
        else:
            animacao_set(cmd[1] if len(cmd) == 2 and cmd[1] != "next" else None)
    elif cmd == ["apps-apply"]:
        apps_apply()
    elif cmd == ["apps-apply", "--skip-missing"]:
        apps_apply(skip_missing=True)
    elif cmd == ["apps-edit"]:
        apps_edit()
    elif cmd == ["panel"]:
        panel_show()
    elif cmd == ["panel-hide"]:
        panel_hide()
    elif cmd[0] == "panel":
        panel_cli(cmd[1:])
    elif cmd == ["layer-show"]:
        layer_show()
    elif cmd == ["layer-hide"]:
        layer_hide()
    elif cmd == ["on-exit"]:
        on_exit()
    elif cmd == ["after-exit"]:
        after_exit()
    elif cmd == ["lock"]:
        lock()
    elif len(cmd) == 2 and cmd[0] == "power" and cmd[1] in ("reboot", "shutdown"):
        power(cmd[1])
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
