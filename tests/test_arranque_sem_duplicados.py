"""Plano 0008 (8.1/8.2): no arranque do PC só pode haver UM pedido de abrir as páginas do pack.

O `boot` lançava `zebar startup` e, logo a seguir, o GlazeWM fazia outro com o 1.º `startup_commands`. Os dois
pedidos cruzam-se e o `apps` e o `limites` abriam a dobrar (~30 MB cada). Aqui contam-se os dois lados juntos.
"""

import re
import unittest

from carregar_por_caminho import RAIZ
from test_arranque import ArranqueFalso

CONFIG = RAIZ / "2-configuracao" / "glzr" / "glazewm" / "config.yaml"
PEDIDO_NO_CONFIG = re.compile(r"^\s*- 'shell-exec [^']*zebar\.exe startup'\s*$", re.MULTILINE)


class UmSoPedidoDeAbrirAsPaginas(unittest.TestCase):

    def test_o_config_tem_um_pedido_nos_startup_commands(self):
        texto = CONFIG.read_text(encoding="utf-8")
        inicio = texto.index("  startup_commands:")
        fim = texto.index("  shutdown_commands:")
        self.assertEqual(len(PEDIDO_NO_CONFIG.findall(texto[inicio:fim])), 1)

    def test_o_boot_nao_pede_o_que_o_glazewm_ja_pede(self):
        with ArranqueFalso() as s:
            s.bh.boot()
            zebar = str(s.zebar)
            no_boot = [cmd for cmd in s.lancados if cmd == [zebar, "startup"]]
            self.assertEqual(no_boot, [])
            # o passo de progresso "Barra" continua: o ecrã de arranque mostra-o até a barra existir
            self.assertIn("barra", [p["id"] for p in s.progresso()["steps"]])


if __name__ == "__main__":
    unittest.main()
