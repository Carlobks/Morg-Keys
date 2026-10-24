"""O bar_helper.py corre como os atalhos e a barra o chamam: `py -I bar_helper.py …`, de qualquer pasta.

Regressão da fase 2a: com `-I` o Python não junta a pasta do script ao sys.path; sem a linha que o faz,
todos os `import morg_…` falham e nenhum atalho funciona. Usa-se um pedido que não toca no sistema
(`panel xyz` só responde "Pedido desconhecido." em JSON).
"""

import contextlib
import io
import json
import subprocess
import sys
import tempfile
import unittest
from typing import ClassVar
from unittest import mock

from sistema_falso import PASTA_PACK, SistemaFalso


class PontoDeEntrada(unittest.TestCase):

    def test_corre_com_py_isolado_noutra_pasta(self):
        with tempfile.TemporaryDirectory() as outra_pasta:
            resultado = subprocess.run([sys.executable, "-I", str(PASTA_PACK / "bar_helper.py"), "panel", "xyz"],
                                       cwd=outra_pasta, capture_output=True, text=True, timeout=60, check=False)
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual(json.loads(resultado.stdout), {"ok": False, "error": "Pedido desconhecido."})


class ListaDeComandos(unittest.TestCase):
    """Cada comando do docstring vai para a função certa (caracterização do `main` de 2026-10-23)."""

    DIRETOS: ClassVar[dict] = {
        ("awake-hold",): "awake_hold", ("quick",): "quick_settings", ("guide",): "guide",
        ("guide-hide",): "guide_hide", ("guide-ensure-hidden",): "guide_ensure_hidden", ("bar", "toggle"): "bar_toggle",
        ("restore-min",): "restore_minimized", ("layout-save",): "layout_save", ("layout-restore",): "layout_restore",
        ("boot",): "boot", ("splash-ready",): "splash_ready", ("apps-apply",): "apps_apply",
        ("apps-edit",): "apps_edit", ("panel",): "panel_show", ("panel-hide",): "panel_hide",
        ("layer-show",): "layer_show", ("layer-hide",): "layer_hide", ("on-exit",): "on_exit",
        ("after-exit",): "after_exit", ("lock",): "lock",
    }
    # Comandos que passam argumentos ou imprimem: (argv, função, argumentos esperados, imprime o resultado).
    COM_ARGUMENTOS: ClassVar[list] = [
        (["awake", "status"], "awake_status", (), True),
        (["awake", "toggle"], "awake_toggle", (), True),
        (["awake", "off"], "awake_off", (), True),
        (["apps-apply", "--skip-missing"], "apps_apply", ((), {"skip_missing": True}), False),
        (["animacao"], "animacao_set", ((None,), {}), False),
        (["animacao", "next"], "animacao_set", ((None,), {}), False),
        (["animacao", "cafe"], "animacao_set", (("cafe",), {}), False),
        (["animacao", "preview"], "animacao_preview", ((), {}), False),
        (["animacao", "tap"], "animacao_tap", ((), {}), False),
        (["panel", "state"], "panel_cli", ((["state"],), {}), False),
        (["power", "reboot"], "power", (("reboot",), {}), False),
        (["power", "shutdown"], "power", (("shutdown",), {}), False),
    ]

    @classmethod
    def setUpClass(cls):
        from sistema_falso import carregar_bar_helper
        carregar_bar_helper()
        cls.bh = sys.modules["bar_helper"]

    def chamar(self, argv, nome, devolve="x"):
        chamadas = []

        def gravador(*args, **kwargs):
            chamadas.append((args, kwargs))
            return devolve

        # As entradas da tabela calculam-se ANTES de trocar a função: depois da troca, `v is função` já não
        # bate e a tabela chamaria a função real (aconteceu: awake-hold real ficou pendurado — A34).
        original = getattr(self.bh, nome)
        na_tabela = {k: gravador for k, v in self.bh.COMANDOS.items() if v is original}
        saida = io.StringIO()
        # Dentro do sistema falso: se um comando real escapar, bate numa bomba em vez de mexer no PC.
        with SistemaFalso(), mock.patch.object(self.bh, nome, gravador), \
                mock.patch.dict(self.bh.COMANDOS, na_tabela), contextlib.redirect_stdout(saida):
            codigo = self.bh.main(["bar_helper.py", *argv])
        return codigo, chamadas, saida.getvalue()

    def test_comandos_diretos(self):
        for palavras, nome in self.DIRETOS.items():
            with self.subTest(comando=palavras):
                codigo, chamadas, _ = self.chamar(list(palavras), nome)
                self.assertEqual((codigo, chamadas), (0, [((), {})]))

    def test_comandos_com_argumentos_ou_que_imprimem(self):
        for argv, nome, esperado, imprime in self.COM_ARGUMENTOS:
            with self.subTest(comando=argv):
                codigo, chamadas, saida = self.chamar(argv, nome, devolve="on")
                self.assertEqual(codigo, 0)
                self.assertEqual(chamadas, [((), {})] if imprime else [esperado])
                self.assertEqual(saida, "on\n" if imprime else "")

    def test_desconhecido_mostra_a_ajuda_e_devolve_2(self):
        for argv in [[], ["xyz"], ["power", "agora"], ["animacao", "a", "b"], ["guide", "extra"]]:
            with self.subTest(argv=argv):
                saida = io.StringIO()
                with SistemaFalso(), contextlib.redirect_stdout(saida):
                    self.assertEqual(self.bh.main(["bar_helper.py", *argv]), 2)
                self.assertIn("layout-restore", saida.getvalue())


if __name__ == "__main__":
    unittest.main()
