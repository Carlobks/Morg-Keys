"""Cada função do Windows que devolve um handle ou um ponteiro tem o restype declarado (ctypes).

Sem restype, o ctypes devolve um int de 32 bits: num Python de 64 bits o endereço fica cortado. Regressão de
2026-10-31: o kernel32.GetModuleHandleW(None) da cortina do arranque (e do bat_tray.py) devolvia 0xffffffffea740000
em vez de 0x7ff6ea740000; o RegisterClassW e o CreateWindowExW recebiam esse hInstance inválido e o Windows dava
3 "access violation" em cada arranque (apanhados e ignorados por ele; o faulthandler do relatório de erros
mostrou-os no rebentamentos.log).
"""

import re
import sys
import unittest

from sistema_falso import PASTA_PACK

if str(PASTA_PACK) not in sys.path:
    sys.path.insert(0, str(PASTA_PACK))
import morg_win32

# Funções do Windows usadas no pack que devolvem um handle ou um ponteiro (64 bits num Windows de 64 bits).
DEVOLVEM_HANDLE = {"FindWindowW", "GetForegroundWindow", "CreateMutexW", "OpenMutexW", "CreateEventW", "OpenEventW",
                   "GetModuleHandleW", "GetCurrentProcess", "OpenProcess", "CreateWindowExW", "LoadIconW",
                   "SetThreadDpiAwarenessContext", "CreatePopupMenu", "ExtractIconW", "GetStockObject", "ShellExecuteW"}


class RestypeDosHandles(unittest.TestCase):

    def test_cada_funcao_que_devolve_um_handle_tem_restype(self):
        codigo = "\n".join(p.read_text(encoding="utf-8") for p in sorted(PASTA_PACK.glob("*.py")))
        usadas = set(re.findall(r"\b(?:kernel32|user32|gdi32|shell32)\.(\w+)\(", codigo)) & DEVOLVEM_HANDLE
        self.assertIn("GetModuleHandleW", usadas)
        sem = sorted(nome for nome in usadas if not re.search(rf"\.{nome}\.restype\s*=", codigo))
        self.assertEqual(sem, [], "sem restype o handle fica cortado a 32 bits")

    def test_o_get_module_handle_devolve_o_endereco_inteiro(self):
        self.assertGreater(morg_win32.kernel32.GetModuleHandleW(None), 0xFFFFFFFF)  # o python.exe fica acima de 4 GB


if __name__ == "__main__":
    unittest.main()
