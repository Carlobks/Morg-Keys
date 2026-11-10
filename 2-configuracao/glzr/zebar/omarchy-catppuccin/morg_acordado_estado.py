"""Estado da chávena (não suspender) para a barra: imprime "on" ou "off". Só `ctypes`, de propósito.

A barra pergunta isto de tempos a tempos e antes corria o bar_helper.py inteiro (importa metade do pack: ~85 ms de
CPU por pergunta). Aqui só se abre o mutex que o `awake-hold` cria (AWAKE_ALIVE em morg_acordado.py, um teste compara
os dois nomes) e não se importa nenhum outro módulo do pack. Plano 0008.
"""

import ctypes
import sys

AWAKE_ALIVE = "Local\\OmarchyAwakeAlive"
SYNCHRONIZE = 0x00100000


def estado(kernel32):
    handle = kernel32.OpenMutexW(SYNCHRONIZE, False, AWAKE_ALIVE)
    if handle:
        kernel32.CloseHandle(handle)
        return "on"
    return "off"


if __name__ == "__main__":
    kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
    kernel32.OpenMutexW.restype = ctypes.c_void_p
    kernel32.OpenMutexW.argtypes = [ctypes.c_uint32, ctypes.c_int, ctypes.c_wchar_p]
    kernel32.CloseHandle.argtypes = [ctypes.c_void_p]
    sys.stdout.write(estado(kernel32))
