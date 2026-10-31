"""Testes da statusLine do Claude Code (2-configuracao/claude/statusline.py).

O Claude Code passa um JSON no stdin; a linha mostra o modelo, o contexto e os limites do plano, e os
`rate_limits` ficam em ~/.claude/rate_limits.json para o indicador da barra do Zebar (claude_usage.py).
Aqui o ficheiro vai para uma pasta temporária: os testes nunca tocam no ~/.claude real.
"""

import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from carregar_por_caminho import PASTA_STATUSLINE, carregar_statusline, correr_como_script

statusline = carregar_statusline()
LIMITES = {"five_hour": {"used_percentage": 85.4}, "seven_day": {"used_percentage": 55}}


def correr(entrada, pasta):
    """Corre a statusLine com `entrada` (bytes) e o rate_limits.json em `pasta`; devolve o stdout."""
    with mock.patch.object(Path, "home", return_value=Path(pasta)):
        codigo, saida, _ = correr_como_script(PASTA_STATUSLINE / "statusline.py", entrada)
    assert codigo == 0
    return saida


def pasta_temporaria(caso):
    """Pasta temporária apagada no fim do teste."""
    pasta = tempfile.TemporaryDirectory()
    caso.addCleanup(pasta.cleanup)
    return pasta.name


class Cores(unittest.TestCase):

    def test_verde_amarelo_e_vermelho_pelos_limites(self):
        self.assertEqual(statusline.color_for(49.9), statusline.GREEN)
        self.assertEqual(statusline.color_for(50), statusline.YELLOW)
        self.assertEqual(statusline.color_for(80), statusline.RED)


class Linha(unittest.TestCase):

    def setUp(self):
        self.pasta = pasta_temporaria(self)
        (Path(self.pasta) / ".claude").mkdir()
        self.ficheiro = Path(self.pasta) / ".claude" / "rate_limits.json"

    def test_mostra_modelo_contexto_e_limites_com_as_cores(self):
        pedido = {"model": {"display_name": "Opus"}, "context_window": {"used_percentage": 42.4}, "rate_limits": LIMITES}
        saida = correr(json.dumps(pedido).encode("utf-8"), self.pasta)
        self.assertIn("Opus", saida)
        self.assertIn("ctx 42%", saida)
        self.assertIn(f"{statusline.RED}5h 85%", saida)
        self.assertIn(f"{statusline.YELLOW}7d 55%", saida)

    def test_guarda_os_limites_para_a_barra(self):
        with mock.patch("time.time", return_value=1700000000):
            correr(json.dumps({"rate_limits": LIMITES}).encode("utf-8"), self.pasta)
        self.assertEqual(json.loads(self.ficheiro.read_text(encoding="utf-8")),
                         {"captured_at": 1700000000, "rate_limits": LIMITES})
        self.assertEqual(list(self.ficheiro.parent.glob("*.tmp")), [], "o temporário vira o ficheiro final")

    def test_tolera_o_bom_do_powershell(self):
        saida = correr(b"\xef\xbb\xbf" + json.dumps({"model": {"display_name": "Sonnet"}}).encode("utf-8"), self.pasta)
        self.assertIn("Sonnet", saida)

    def test_entrada_estranha_mostra_so_o_nome_por_omissao(self):
        estranhas = [b"", b"nao e json", b"[1, 2]",
                     json.dumps({"model": "x", "context_window": 3, "rate_limits": [1]}).encode("utf-8"),
                     json.dumps({"rate_limits": {"five_hour": 7, "seven_day": {"used_percentage": "50"}}}).encode("utf-8")]
        for entrada in estranhas:
            with self.subTest(entrada=entrada):
                self.assertEqual(correr(entrada, self.pasta).strip(), f"{statusline.MAUVE}Claude{statusline.RESET}")


class OutraSessaoAEscrever(unittest.TestCase):
    """Duas sessões ao mesmo tempo: se a escrita falhar fica a versão da outra, e a linha aparece na mesma."""

    def setUp(self):
        self.pasta = pasta_temporaria(self)
        (Path(self.pasta) / ".claude").mkdir()
        self.entrada = json.dumps({"rate_limits": LIMITES}).encode("utf-8")

    def test_sem_a_pasta_nao_escreve_nada(self):
        saida = correr(self.entrada, pasta_temporaria(self))  # sem ~/.claude: o temporário nem se cria
        self.assertIn("5h 85%", saida)

    def test_troca_falhada_apaga_o_temporario(self):
        with mock.patch("os.replace", side_effect=OSError("ocupado")):
            correr(self.entrada, self.pasta)
        self.assertEqual(list((Path(self.pasta) / ".claude").iterdir()), [])

    def test_temporario_que_nao_se_apaga_fica_sem_erro(self):
        with mock.patch("os.replace", side_effect=OSError("ocupado")), \
                mock.patch("os.unlink", side_effect=OSError("preso")) as apagar:
            saida = correr(self.entrada, self.pasta)
        apagar.assert_called_once()
        self.assertIn("7d 55%", saida)


if __name__ == "__main__":
    unittest.main()
