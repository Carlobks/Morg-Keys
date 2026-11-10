"""Plano 0008 (8.3): o ajudante pequeno da chávena (morg_acordado_estado.py) e a página que o chama.

A barra perguntava "a chávena está ligada?" com o bar_helper.py inteiro (~85 ms de CPU, 1 440 processos por hora).
O ajudante novo só usa o ctypes e tem de olhar para o MESMO mutex que o `awake-hold` cria.
"""

import json
import re
import sys
import unittest
from types import SimpleNamespace

from sistema_falso import PASTA_PACK, carregar_bar_helper
from test_programas_e_config import correr_como_programa

carregar_bar_helper()
ESTADO = __import__("morg_acordado_estado")
ACORDADO = sys.modules["morg_acordado"]
ZPACK = json.loads((PASTA_PACK / "zpack.json").read_text(encoding="utf-8"))
BAR_HTML = (PASTA_PACK / "bar.html").read_text(encoding="utf-8")


def kernel32_falso(existe):
    chamadas = []

    def abrir(acesso, herda, nome):
        chamadas.append(("OpenMutexW", acesso, herda, nome))
        return 7 if existe else 0

    def fechar(handle):
        chamadas.append(("CloseHandle", handle))

    return SimpleNamespace(OpenMutexW=abrir, CloseHandle=fechar), chamadas


class EstadoDaChavena(unittest.TestCase):

    def test_o_nome_do_mutex_e_o_do_awake_hold(self):
        self.assertEqual(ESTADO.AWAKE_ALIVE, ACORDADO.AWAKE_ALIVE)

    def test_ligada_abre_fecha_e_diz_on(self):
        k32, chamadas = kernel32_falso(True)
        self.assertEqual(ESTADO.estado(k32), "on")
        self.assertEqual(chamadas, [("OpenMutexW", 0x00100000, False, ACORDADO.AWAKE_ALIVE), ("CloseHandle", 7)])

    def test_desligada_diz_off_sem_fechar_nada(self):
        k32, chamadas = kernel32_falso(False)
        self.assertEqual(ESTADO.estado(k32), "off")
        self.assertEqual([c[0] for c in chamadas], ["OpenMutexW"])

    def test_como_programa_imprime_on_ou_off(self):
        codigo, saida = correr_como_programa("morg_acordado_estado.py", ["morg_acordado_estado.py"])
        self.assertIsNone(codigo)
        self.assertIn(saida, ("on", "off"))

    def test_nao_importa_o_bar_helper_nem_o_morg_win32(self):
        texto = (PASTA_PACK / "morg_acordado_estado.py").read_text(encoding="utf-8")
        importados = set(re.findall(r"^\s*(?:import|from)\s+([\w.]+)", texto, re.MULTILINE))
        self.assertEqual(importados, {"ctypes", "sys"})


class PermissaoNoZpack(unittest.TestCase):

    def _regex(self):
        barra = next(w for w in ZPACK["widgets"] if w["name"] == "bar")
        comandos = barra["privileges"]["shellCommands"]
        self.assertEqual([c["program"] for c in comandos], ["C:\\Windows\\py.exe"])
        return comandos[0]["argsRegex"]

    def _aceita(self, args):
        return re.match(self._regex().replace("{{HOME_RE}}", "C:/Users/Ana"), args) is not None

    def test_aceita_o_ajudante_novo_e_os_antigos(self):
        base = "-I C:/Users/Ana/.glzr/zebar/omarchy-catppuccin/"
        for resto in ("morg_acordado_estado.py", "claude_usage.py", "bar_helper.py awake toggle",
                      "bar_helper.py awake status", "bar_helper.py quick", "bar_helper.py limites"):
            with self.subTest(resto=resto):
                self.assertTrue(self._aceita(base + resto))

    def test_recusa_argumentos_a_mais_ou_outro_ficheiro(self):
        base = "-I C:/Users/Ana/.glzr/zebar/omarchy-catppuccin/"
        for resto in ("morg_acordado_estado.py extra", "morg_acordado_estado.pyc", "outro.py",
                      "bar_helper.py awake-hold"):
            with self.subTest(resto=resto):
                self.assertFalse(self._aceita(base + resto))


class ChavenaNaBarra(unittest.TestCase):

    def test_a_pagina_chama_o_ajudante_novo_e_nao_o_bar_helper(self):
        self.assertIn("morg_acordado_estado.py", BAR_HTML)
        self.assertNotIn("'status'", BAR_HTML)

    def test_a_verificacao_lenta_e_de_60_s(self):
        self.assertRegex(BAR_HTML, r"AWAKE_EVERY_MS\s*=\s*60_000")


if __name__ == "__main__":
    unittest.main()
