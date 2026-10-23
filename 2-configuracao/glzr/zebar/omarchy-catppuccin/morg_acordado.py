"""Não suspender (chávena da barra): processo "awake-hold" com mutex e evento com nome."""

import ctypes
import subprocess
import time

from morg_processos import BAR_HELPER, PYTHONW
from morg_win32 import (
    ERROR_ALREADY_EXISTS,
    EVENT_MODIFY_STATE,
    INFINITE,
    SYNCHRONIZE,
    _NamedMutex,
    kernel32,
)

# --- Não suspender (chávena) ---------------------------------------------------
# O processo "awake-hold" é dono do mutex AWAKE_ALIVE enquanto está vivo: é a
# prova de que está ligado (sem ficheiros de PID que sobrevivam a um reinício).
# Para o desligar, sinaliza-se o evento AWAKE_STOP e ele sai sozinho.
AWAKE_ALIVE = "Local\\OmarchyAwakeAlive"
AWAKE_STOP = "Local\\OmarchyAwakeStop"
AWAKE_TOGGLE = "Local\\OmarchyAwakeToggle"


def awake_status():
    handle = kernel32.OpenMutexW(SYNCHRONIZE, False, AWAKE_ALIVE)
    if handle:
        kernel32.CloseHandle(handle)
        return "on"
    return "off"


def _awake_stop():
    handle = kernel32.OpenEventW(EVENT_MODIFY_STATE, False, AWAKE_STOP)
    if handle:
        kernel32.SetEvent(handle)
        kernel32.CloseHandle(handle)
    for _ in range(40):  # até 2 s para o processo sair
        if awake_status() == "off":
            break
        time.sleep(0.05)


def awake_toggle():
    with _NamedMutex(AWAKE_TOGGLE) as owned:  # dois cliques rápidos não criam dois processos
        if not owned:
            return awake_status()
        if awake_status() == "on":
            _awake_stop()
            return awake_status()

        # Processo independente: sobrevive ao fecho do Zebar e não abre janela.
        flags = 0x00000008 | 0x00000200  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
        args = [str(PYTHONW), "-I", str(BAR_HELPER), "awake-hold"]
        try:
            subprocess.Popen(args, creationflags=flags | 0x01000000, close_fds=True)  # + BREAKAWAY_FROM_JOB
        except OSError:
            subprocess.Popen(args, creationflags=flags, close_fds=True)
        for _ in range(60):  # confirma que arrancou (até 3 s)
            if awake_status() == "on":
                break
            time.sleep(0.05)
        return awake_status()


def awake_off():
    with _NamedMutex(AWAKE_TOGGLE):
        _awake_stop()
    return awake_status()


def awake_hold():
    alive = kernel32.CreateMutexW(None, True, AWAKE_ALIVE)
    if not alive or ctypes.get_last_error() == ERROR_ALREADY_EXISTS:
        return  # já há outro a manter o PC acordado
    stop = kernel32.CreateEventW(None, True, False, AWAKE_STOP)
    ES_CONTINUOUS, ES_SYSTEM_REQUIRED, ES_DISPLAY_REQUIRED = 0x80000000, 0x1, 0x2
    # Sistema e ecrã acordados, como o "Stay Awake" do Omarchy (sem proteção
    # de ecrã nem bloqueio). 0 = o Windows recusou: sai para a chávena não mentir.
    if not kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED):
        return
    kernel32.WaitForSingleObject(stop, INFINITE)  # o estado vale enquanto esta thread existir
    kernel32.SetThreadExecutionState(ES_CONTINUOUS)
