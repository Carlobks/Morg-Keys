"""O bar_helper.py corre como os atalhos e a barra o chamam: `py -I bar_helper.py …`, de qualquer pasta.

Regressão da fase 2a: com `-I` o Python não junta a pasta do script ao sys.path; sem a linha que o faz,
todos os `import morg_…` falham e nenhum atalho funciona. Usa-se um pedido que não toca no sistema
(`panel xyz` só responde "Pedido desconhecido." em JSON).
"""

import json
import subprocess
import sys
import tempfile
import unittest

from sistema_falso import PASTA_PACK


class PontoDeEntrada(unittest.TestCase):

    def test_corre_com_py_isolado_noutra_pasta(self):
        with tempfile.TemporaryDirectory() as outra_pasta:
            resultado = subprocess.run([sys.executable, "-I", str(PASTA_PACK / "bar_helper.py"), "panel", "xyz"],
                                       cwd=outra_pasta, capture_output=True, text=True, timeout=60, check=False)
        self.assertEqual(resultado.returncode, 0, resultado.stderr)
        self.assertEqual(json.loads(resultado.stdout), {"ok": False, "error": "Pedido desconhecido."})


if __name__ == "__main__":
    unittest.main()
