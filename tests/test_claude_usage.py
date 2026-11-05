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


def correr(conteudo, arranque=None):
    """Corre o main() com este rate_limits.json (texto, ou None = ficheiro em falta) e este arranque.txt
    (None = em falta); devolve o JSON."""
    with tempfile.TemporaryDirectory() as pasta:
        ficheiro = Path(pasta) / "rate_limits.json"
        if conteudo is not None:
            ficheiro.write_text(conteudo, encoding="utf-8")
        arranque_txt = Path(pasta) / "arranque.txt"
        if arranque is not None:
            arranque_txt.write_text(arranque, encoding="utf-8")
        saida = io.StringIO()
        with mock.patch.object(uso, "RATE_FILE", ficheiro), mock.patch.object(uso, "ARRANQUE_FILE", arranque_txt), \
                mock.patch.object(uso.time, "time", return_value=AGORA), contextlib.redirect_stdout(saida):
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
            "now": AGORA, "mostrar": True, "captured_at": AGORA - 60, "origem": None,
            "five_hour": {"pct": 23.5, "resets_at": AGORA + 3600},
            "seven_day": {"pct": 24.0, "resets_at": AGORA + 86400}})

    def test_janela_ja_reposta_fica_como_ultimo_valor_expirado(self):
        # O último valor não some: a barra mostra-o esbatido até alguém o atualizar (clique no ✻).
        dados = {"rate_limits": {"five_hour": {"used_percentage": 90, "resets_at": AGORA - 1}}}
        self.assertEqual(correr(json.dumps(dados))["five_hour"],
                         {"pct": 90.0, "resets_at": AGORA - 1, "expirado": True})

    def test_semanal_expirada_avanca_de_7_em_7_dias_ate_ao_futuro(self):
        semana = 7 * 86400
        for atraso, ciclos in [(0, 1), (1, 1), (semana, 2), (semana + 5, 2), (3 * semana + 1, 4)]:
            with self.subTest(atraso=atraso):
                dados = {"rate_limits": {"seven_day": {"used_percentage": 70, "resets_at": AGORA - atraso}}}
                self.assertEqual(correr(json.dumps(dados))["seven_day"], {
                    "pct": 70.0, "resets_at": AGORA - atraso + ciclos * semana, "expirado": True})

    def test_janela_sem_reset_ou_com_percentagem_estranha_nao_conta(self):
        for janela in [{"used_percentage": 50}, {"used_percentage": 50, "resets_at": 0},
                       {"used_percentage": True, "resets_at": AGORA + 5}, {"used_percentage": "5", "resets_at": AGORA}]:
            with self.subTest(janela=janela):
                self.assertIsNone(correr(json.dumps({"rate_limits": {"five_hour": janela}}))["five_hour"])

    def test_ficheiro_em_falta_estragado_ou_estranho(self):
        vazio = {"now": AGORA, "mostrar": True, "captured_at": None, "origem": None, "five_hour": None,
                 "seven_day": None}
        for conteudo in [None, "{nao e json", "[1, 2]", '{"rate_limits": "x"}',
                         '{"rate_limits": {"five_hour": "x", "seven_day": {"used_percentage": "50"}}}']:
            with self.subTest(conteudo=conteudo):
                self.assertEqual(correr(conteudo), vazio)

    def test_origem_dos_valores(self):
        # O modal dos limites (morg_limites.py) grava "origem": "manual"; a statusLine não grava o campo.
        for origem, esperado in [("manual", "manual"), (None, None), (3, None)]:
            with self.subTest(origem=origem):
                self.assertEqual(correr(json.dumps({"origem": origem}))["origem"], esperado)


class MostrarOuEsconder(unittest.TestCase):

    def test_claude_esconder_no_arranque_txt(self):
        for texto, mostrar in [
            (None, True),                                            # sem arranque.txt
            ("animacao = cafe\n", True),                             # sem a linha
            ("claude = mostrar\n", True),
            ("﻿Claude = Esconder\n", False),                    # BOM e maiúsculas
            ("# claude = esconder\nclaude = ocultar\n", False),      # comentário não conta
            ("claude = não\n", False), ("claude=off\n", False),
            ("claude = esconder\nclaude = mostrar\n", False),        # vale a primeira
        ]:
            with self.subTest(texto=texto):
                self.assertIs(correr(None, texto)["mostrar"], mostrar)


if __name__ == "__main__":
    unittest.main()
