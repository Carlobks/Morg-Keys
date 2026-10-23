"""Ecrã de arranque (widget splash): progress.json, aviso de "pronto" e manter no topo."""

import json
import os
import time

from morg_config_arranque import SPLASH_DIR
from morg_win32 import EVENT_MODIFY_STATE, HWND, kernel32, user32

PROGRESS_FILE = SPLASH_DIR / "progress.json"
SPLASH_TITLE = "Zebar - omarchy-catppuccin / splash"

SPLASH_READY = "Local\\MorgSplashReady"

class _Progress:
    """progress.json escrito de forma atómica (tmp + replace, com novas tentativas)."""

    def __init__(self, animacao="cafe", preview=False):
        self.data = {"boot_id": str(time.time_ns()), "started": time.time(), "animacao": animacao,
                     "preview": preview, "steps": [], "fim": False}
        self.save()

    def save(self):
        tmp = PROGRESS_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.data, ensure_ascii=False), encoding="utf-8")
        for _ in range(10):
            try:
                os.replace(tmp, PROGRESS_FILE)
                return
            except PermissionError:  # o Zebar pode estar a ler neste instante
                time.sleep(0.02)

    def step(self, sid, label, state="a_carregar"):
        for s in self.data["steps"]:
            if s["id"] == sid:
                s["state"] = state
                break
        else:
            self.data["steps"].append({"id": sid, "label": label, "state": state})
        self.save()

    def finish(self):
        self.data["fim"] = True
        self.save()



def _splash_to_top():
    """O guia e o painel (também top_most) nascem depois do splash e ficariam
    por cima dele: volta a pô-lo no topo, sem o ativar."""
    hwnd = user32.FindWindowW(None, SPLASH_TITLE)
    if hwnd:
        HWND_TOPMOST, SWP_NOSIZE, SWP_NOMOVE, SWP_NOACTIVATE = HWND(-1), 0x1, 0x2, 0x10
        user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOSIZE | SWP_NOMOVE | SWP_NOACTIVATE)



def splash_ready():
    """Chamado pela página do splash quando já está desenhada por cima de tudo."""
    handle = kernel32.OpenEventW(EVENT_MODIFY_STATE, False, SPLASH_READY)
    if handle:
        kernel32.SetEvent(handle)
        kernel32.CloseHandle(handle)
