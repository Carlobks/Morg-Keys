"""Caracterização do claude_usage.py (limites do plano Claude para a barra).

Fase 1 da experiência 0001: fixa o comportamento de 2026-10-23, antes do pendente "quota na barra".
"""

import contextlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from sistema_falso import PASTA_PACK

_especificacao = importlib.util.spec_from_file_location("claude_usage", PASTA_PACK / "claude_usage.py")
uso = importlib.util.module_from_spec(_especificacao)
_especificacao.loader.exec_module(uso)

AGORA = 1_800_000_000


def correr(conteudo):
    """Corre o main() com este rate_limits.json (texto, ou None = ficheiro em falta); devolve o JSON."""
    with tempfile.TemporaryDirectory() as pasta:
        ficheiro = Path(pasta) / "rate_limits.json"
        if conteudo is not None:
            ficheiro.write_text(conteudo, encoding="utf-8")
        saida = io.StringIO()
        with mock.patch.object(uso, "RATE_FILE", ficheiro), mock.patch.object(uso.time, "time", return_value=AGORA), \
                contextlib.redirect_stdout(saida):
            uso.main()
    return json.loads(saida.getvalue())


class Epoch(unittest.TestCase):

    def test_segundos_e_milissegundos(self):
        self.assertEqual(uso._epoch(AGORA), AGORA)
        self.assertEqual(uso._epoch(AGORA * 1000 + 999), AGORA)
        self.assertEqual(uso._epoch(12.7), 12)

    def test_outros_formatos(self):
        for valor in [None, "123", True, [], {}]:
            with self.subTest(valor=valor):
                self.assertIsNone(uso._epoch(valor))


class LimitesParaABarra(unittest.TestCase):

    def test_le_as_duas_janelas(self):
        dados = {"captured_at": AGORA - 60, "rate_limits": {
            "five_hour": {"used_percentage": 23.456, "resets_at": AGORA + 3600},
            "seven_day": {"used_percentage": 24, "resets_at": (AGORA + 86400) * 1000}}}
        self.assertEqual(correr(json.dumps(dados)), {
            "now": AGORA, "captured_at": AGORA - 60,
            "five_hour": {"pct": 23.5, "resets_at": AGORA + 3600},
            "seven_day": {"pct": 24.0, "resets_at": AGORA + 86400}})

    def test_janela_ja_reposta_deixa_de_valer(self):
        dados = {"rate_limits": {"five_hour": {"used_percentage": 90, "resets_at": AGORA - 1}}}
        self.assertIsNone(correr(json.dumps(dados))["five_hour"])

    def test_ficheiro_em_falta_estragado_ou_estranho(self):
        vazio = {"now": AGORA, "captured_at": None, "five_hour": None, "seven_day": None}
        for conteudo in [None, "{nao e json", "[1, 2]", '{"rate_limits": "x"}',
                         '{"rate_limits": {"five_hour": "x", "seven_day": {"used_percentage": "50"}}}']:
            with self.subTest(conteudo=conteudo):
                self.assertEqual(correr(conteudo), vazio)


if __name__ == "__main__":
    unittest.main()
