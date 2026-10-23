"""Ações do Windows: Definições Rápidas (Win+A), bloquear, reiniciar/desligar e saída do GlazeWM."""

import ctypes
import subprocess
import time
from ctypes import wintypes

from morg_acordado import awake_off
from morg_processos import CREATE_NO_WINDOW, HERE, _spawn_detached
from morg_win32 import user32


# --- Definições Rápidas (Win+A) -------------------------------------------------
def quick_settings():
    """Envia Win+A com SendInput (o mesmo que carregar nas teclas)."""
    VK_LWIN, VK_A, KEYUP = 0x5B, 0x41, 0x0002

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD), ("dwFlags", wintypes.DWORD),
                    ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.c_size_t)]

    class INPUT(ctypes.Structure):
        class _U(ctypes.Union):
            _fields_ = [("ki", KEYBDINPUT), ("_pad", ctypes.c_byte * 32)]
        _anonymous_ = ("u",)
        _fields_ = [("type", wintypes.DWORD), ("u", _U)]

    def key(vk, up=False):
        i = INPUT(type=1)
        i.ki = KEYBDINPUT(vk, 0, KEYUP if up else 0, 0, 0)
        return i

    seq = (INPUT * 4)(key(VK_LWIN), key(VK_A), key(VK_A, True), key(VK_LWIN, True))
    user32.SendInput(4, seq, ctypes.sizeof(INPUT))



# --- Saída do GlazeWM -----------------------------------------------------------
# Os processos que o GlazeWM lança ficam no mesmo "job" do Windows e morrem
# quando ele termina — por isso os shutdown_commands não podem fazer trabalho
# demorado. "on-exit" só lança um processo independente (fora do job) e sai;
# esse processo ("after-exit") espera que o GlazeWM termine e então desliga o
# "não suspender" e volta a mostrar janelas que tenham ficado escondidas.
UNCLOAK_PS1 = HERE / "uncloak.ps1"



def on_exit():
    _spawn_detached("after-exit")


def after_exit():
    def glaze_running():
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq glazewm.exe", "/NH"],
                             capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
        return "glazewm.exe" in out.stdout.lower()

    deadline = time.monotonic() + 20
    while glaze_running() and time.monotonic() < deadline:
        time.sleep(0.5)
    awake_off()
    if UNCLOAK_PS1.exists():
        subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                        "-File", str(UNCLOAK_PS1), "-WaitForGlazeExit"],
                       creationflags=CREATE_NO_WINDOW)



# --- Sistema --------------------------------------------------------------------
def lock():
    user32.LockWorkStation()


def power(action):
    """Reiniciar/desligar só depois de confirmar (o botão por omissão é "Não")."""
    texts = {"reboot": ("Reiniciar o computador agora?", "/r"),
             "shutdown": ("Desligar o computador agora?", "/s")}
    question, flag = texts[action]
    MB_YESNO, MB_ICONQUESTION, MB_DEFBUTTON2 = 0x4, 0x20, 0x100
    MB_SETFOREGROUND, MB_TOPMOST, IDYES = 0x10000, 0x40000, 6
    answer = user32.MessageBoxW(None, question, "Sistema",
                                MB_YESNO | MB_ICONQUESTION | MB_DEFBUTTON2 | MB_SETFOREGROUND | MB_TOPMOST)
    if answer == IDYES:
        subprocess.run(["shutdown", flag, "/t", "0"], creationflags=CREATE_NO_WINDOW)
