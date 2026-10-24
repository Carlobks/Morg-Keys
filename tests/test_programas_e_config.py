"""Os scripts do pack corridos como programa (`if __name__ == "__main__"`) e casos do arranque.txt.

O bar_helper.py corre com um pedido que não toca no sistema (`panel xyz`); o claude_usage.py com uma
pasta pessoal vazia; o bat_tray.py sem argumentos (sai com 2 antes de criar o mutex).
"""

import contextlib
import io
import json
import os
import runpy
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from sistema_falso import PASTA_PACK, SistemaFalso


def correr_como_programa(nome, argv, ambiente=None):
    saida = io.StringIO()
    with mock.patch.object(sys, "argv", argv), mock.patch.object(sys, "path", list(sys.path)), \
            mock.patch.dict(os.environ, ambiente or {}), contextlib.redirect_stdout(saida), \
            self_raises() as codigo:
        runpy.run_path(str(PASTA_PACK / nome), run_name="__main__")
    return codigo.get("codigo"), saida.getvalue()


@contextlib.contextmanager
def self_raises():
    """Apanha o sys.exit do script e guarda o código."""
    resultado = {}
    try:
        yield resultado
    except SystemExit as fim:
        resultado["codigo"] = fim.code


class ScriptsComoPrograma(unittest.TestCase):

    def test_bar_helper(self):
        codigo, saida = correr_como_programa("bar_helper.py", ["bar_helper.py", "panel", "xyz"])
        self.assertEqual((codigo, json.loads(saida)), (0, {"ok": False, "error": "Pedido desconhecido."}))

    def test_claude_usage(self):
        with tempfile.TemporaryDirectory() as casa:
            codigo, saida = correr_como_programa("claude_usage.py", ["claude_usage.py"],
                                                 {"USERPROFILE": casa, "HOME": casa})
        self.assertIsNone(codigo)
        self.assertEqual(set(json.loads(saida)), {"now", "captured_at", "five_hour", "seven_day"})

    def test_bat_tray_sem_bat(self):
        self.assertEqual(correr_como_programa("bat_tray.py", ["bat_tray.py"])[0], 2)


class ArranqueTxtCasos(unittest.TestCase):

    def test_bat_sem_caminho_e_ignorado(self):
        with SistemaFalso() as s:
            ficheiro = s.pasta / "arranque.txt"
            ficheiro.write_text("bat = | http://localhost:3000 | Sem caminho\n", encoding="utf-8")
            s.trocar("ARRANQUE_FILE", ficheiro)
            self.assertEqual(s.bh._arranque_cfg()["bats"], [])

    def test_set_animacao_sem_ficheiro_cria_o(self):
        with SistemaFalso() as s:
            ficheiro = Path(s.pasta) / "arranque.txt"
            s.trocar("ARRANQUE_FILE", ficheiro)
            s.bh._set_animacao("cafe")
            self.assertEqual(ficheiro.read_text(encoding="utf-8"), "animacao = cafe\n")


if __name__ == "__main__":
    unittest.main()
