"""Caminhos dos programas e lançamento de processos (ShellExecute, fora do job, widgets do Zebar)."""

import os
import subprocess
import sys
import time
from pathlib import Path

from morg_win32 import shell32

HERE = Path(__file__).resolve().parent
BAR_HELPER = HERE / "bar_helper.py"  # ponto de entrada (os processos relançam-se por ele)
PYTHONW = Path(sys.executable).with_name("pythonw.exe")
PROGRAM_FILES = Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
ZEBAR = PROGRAM_FILES / "glzr.io" / "Zebar" / "zebar.exe"
GLAZE_CLI = PROGRAM_FILES / "glzr.io" / "GlazeWM" / "cli" / "glazewm.exe"
CREATE_NO_WINDOW = 0x08000000


def _shell_open(launch, log=None):
    """Abre {"file", "args"} por ShellExecute (como o os.startfile, mas com argumentos).
    ShellExecute: o GlazeWM e apps com uiAccess só arrancam assim (armadilha A1)."""
    rc = shell32.ShellExecuteW(None, "open", launch["file"], launch.get("args") or None, None, 1)
    ok = (rc or 0) > 32
    if log:
        log(f"abri {launch['file']} {launch.get('args') or ''}".rstrip() if ok else f"não consegui abrir {launch['file']} ({rc})")
    return ok



def _start_widget(pack, widget):
    if not ZEBAR.exists():
        return False
    try:
        subprocess.Popen(
            [str(ZEBAR), "start-widget-preset", "--pack", pack, "--widget-name", widget,
             "--preset", "default"],
            creationflags=CREATE_NO_WINDOW, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        return True
    except OSError:
        return False



def _popen_detached(cmd, **kw):
    """Lança fora do job da tarefa agendada (sobrevive ao fim da tarefa)."""
    flags = 0x00000008 | 0x00000200  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    try:
        return subprocess.Popen(cmd, creationflags=flags | 0x01000000, close_fds=True, **kw)  # + BREAKAWAY
    except OSError:
        return subprocess.Popen(cmd, creationflags=flags, close_fds=True, **kw)


def _wait_for(predicate, timeout, poll=0.1):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        result = predicate()
        if result:
            return result
        time.sleep(poll)
    return None



def _spawn_detached(*args):
    flags = 0x00000008 | 0x00000200  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    cmd = [str(PYTHONW), "-I", str(BAR_HELPER), *args]
    try:
        subprocess.Popen(cmd, creationflags=flags | 0x01000000, close_fds=True)  # + BREAKAWAY_FROM_JOB
    except OSError:
        subprocess.Popen(cmd, creationflags=flags, close_fds=True)
