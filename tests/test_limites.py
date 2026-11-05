"""Modal dos limites do Claude (morg_limites, P7): ler o que o dono escreve, gravar no rate_limits.json e
mostrar/esconder o widget com o foco certo. Ficheiros e janelas falsos (sistema_falso, test_janelas_zebar).
"""

import base64
import contextlib
import io
import json
import sys
import unittest
from datetime import datetime, timedelta
from unittest import mock

from sistema_falso import SistemaFalso
from test_janelas_zebar import Ecra, JanelasFalsas

MODAL, BARRA = "Zebar - omarchy-catppuccin / limites", "Zebar - omarchy-catppuccin / bar"
CINCO_H, SETE_D = 5 * 3600, 7 * 86400
TERCA_18H = datetime(2026, 11, 3, 18, 0)  # uma terça-feira, hora local do PC
AGORA = int(TERCA_18H.timestamp())


def em(data):
    return int(data.timestamp())


def limites():
    return sys.modules["morg_limites"]


class LerPercentagem(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        SistemaFalso()  # carrega o bar_helper e os morg_*.py

    def test_aceita_inteiros_de_0_a_100(self):
        for texto, valor in [("40", 40), (" 7 % ", 7), ("0", 0), ("100", 100), ("55%", 55)]:
            with self.subTest(texto=texto):
                self.assertEqual(limites().ler_percentagem(texto), valor)

    def test_recusa_o_resto_com_uma_mensagem(self):
        for texto in ["101", "-1", "4,5", "4.5", "abc", "1000"]:
            with self.subTest(texto=texto), self.assertRaises(ValueError) as erro:
                limites().ler_percentagem(texto)
            self.assertEqual(str(erro.exception), "Use um número inteiro de 0 a 100.")


class LerReset(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        SistemaFalso()

    def ler(self, texto, maximo=SETE_D):
        return limites().ler_reset(texto, AGORA, maximo)

    def test_tempo_que_falta(self):
        casos = {"2h15": 2 * 3600 + 15 * 60, "45m": 45 * 60, "2h": 7200, "1d5h": 29 * 3600, " 1d 2h 3m ": 93780,
                 "3H05": 3 * 3600 + 300}
        for texto, segundos in casos.items():
            with self.subTest(texto=texto):
                self.assertEqual(self.ler(texto), AGORA + segundos)

    def test_hora_de_hoje_ou_de_amanha(self):
        self.assertEqual(self.ler("19:05"), em(TERCA_18H.replace(hour=19, minute=5)))
        self.assertEqual(self.ler("14:30"), em(TERCA_18H.replace(hour=14, minute=30) + timedelta(days=1)))
        self.assertEqual(self.ler("18:00"), em(TERCA_18H + timedelta(days=1)))  # agora mesmo já passou
        self.assertEqual(self.ler("9:00"), em(TERCA_18H.replace(hour=9) + timedelta(days=1)))

    def test_dia_da_semana_e_hora(self):
        quinta = TERCA_18H.replace(day=5, hour=16)
        casos = {"qui 16:00": quinta, "Quinta 16:00": quinta, "qui. 16:00": quinta,
                 "ter 19:00": TERCA_18H.replace(hour=19), "ter 17:00": TERCA_18H.replace(day=10, hour=17),
                 "sáb 9:30": TERCA_18H.replace(day=7, hour=9, minute=30), "sab 9:30": TERCA_18H.replace(day=7, hour=9, minute=30),
                 "seg 8:00": TERCA_18H.replace(day=9, hour=8), "dom 23:59": TERCA_18H.replace(day=8, hour=23, minute=59),
                 "qua 0:00": TERCA_18H.replace(day=4, hour=0), "sex 12:00": TERCA_18H.replace(day=6, hour=12)}
        for texto, data in casos.items():
            with self.subTest(texto=texto):
                self.assertEqual(self.ler(texto), em(data))

    def test_vazio_e_none(self):
        self.assertIsNone(self.ler(""))
        self.assertIsNone(self.ler("   "))

    def test_recusa_o_que_nao_entende(self):
        for texto in ["abc", "45", "25:00", "14:60", "0m", "0h0", "xyz 16:00", "qui", "2h15x", "1d15"]:
            with self.subTest(texto=texto), self.assertRaises(ValueError) as erro:
                self.ler(texto)
            self.assertEqual(str(erro.exception), "Use 14:30, 2h15, 45m ou qui 16:00.")

    def test_recusa_mais_do_que_a_janela(self):
        with self.assertRaises(ValueError) as erro:
            self.ler("5h02", maximo=CINCO_H)
        self.assertEqual(str(erro.exception), "Passa das 5 h: confira o valor.")
        self.assertEqual(self.ler("5h", maximo=CINCO_H), AGORA + CINCO_H)
        with self.assertRaises(ValueError) as erro:
            self.ler("8d")
        self.assertEqual(str(erro.exception), "Passa dos 7 dias: confira o valor.")


class Modal(unittest.TestCase):
    """limites state | limites set <b64>, com o rate_limits.json numa pasta temporária."""

    def setUp(self):
        self.s = SistemaFalso().__enter__()
        self.addCleanup(self.s.__exit__, None, None, None)
        self.ficheiro = self.s.pasta / "rate_limits.json"
        self.s.trocar("RATE_FILE", self.ficheiro)
        self.agora = int(self.s.relogio.time())

    def gravar_ficheiro(self, dados):
        self.ficheiro.write_text(json.dumps(dados), encoding="utf-8")

    def pedir(self, *args):
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            limites().limites_cli(list(args))
        texto = saida.getvalue()
        self.assertTrue(texto.isascii())
        return json.loads(texto)

    def gravar(self, **campos):
        b64 = base64.urlsafe_b64encode(json.dumps(campos).encode("utf-8")).decode("ascii").rstrip("=")
        return self.pedir("set", b64)

    def ficheiro_json(self):
        return json.loads(self.ficheiro.read_text(encoding="utf-8"))

    def test_estado_sem_ficheiro(self):
        self.assertEqual(self.pedir("state"), {"ok": True, "state": {
            "now": self.agora, "captured_at": None, "origem": None, "five_hour": None, "seven_day": None}})

    def test_estado_com_valores_e_janela_ja_reposta(self):
        # A 5 h expirada continua no estado (o modal abre com o último %); a semanal tem o ciclo avançado.
        self.gravar_ficheiro({"captured_at": self.agora - 60, "origem": "manual", "rate_limits": {
            "five_hour": {"used_percentage": 23.5, "resets_at": self.agora - 1},
            "seven_day": {"used_percentage": 40, "resets_at": (self.agora + 99) * 1000}}})
        self.assertEqual(self.pedir("state")["state"], {
            "now": self.agora, "captured_at": self.agora - 60, "origem": "manual",
            "five_hour": {"pct": 23.5, "resets_at": self.agora - 1, "expirado": True},
            "seven_day": {"pct": 40, "resets_at": self.agora + 99}})

    def test_estado_com_semanal_expirada_avanca_o_ciclo(self):
        passado = self.agora - 86400
        self.gravar_ficheiro({"rate_limits": {"seven_day": {"used_percentage": 40, "resets_at": passado}}})
        self.assertEqual(self.pedir("state")["state"]["seven_day"],
                         {"pct": 40, "resets_at": passado + 7 * 86400, "expirado": True})

    def test_estado_com_ficheiro_estragado(self):
        for conteudo in ["{", "[]", json.dumps({"rate_limits": []}), json.dumps({"rate_limits": {"five_hour": 3}})]:
            with self.subTest(conteudo=conteudo):
                self.ficheiro.write_text(conteudo, encoding="utf-8")
                estado = self.pedir("state")["state"]
                self.assertEqual((estado["five_hour"], estado["seven_day"]), (None, None))

    def test_grava_as_duas_janelas_com_origem_manual(self):
        resposta = self.gravar(five_pct="40", five_reset="2h15", week_pct="70", week_reset="qui 16:00")
        self.assertTrue(resposta["ok"], resposta)
        dados = self.ficheiro_json()
        self.assertEqual((dados["origem"], dados["captured_at"]), ("manual", self.agora))
        self.assertEqual(dados["rate_limits"]["five_hour"],
                         {"used_percentage": 40, "resets_at": self.agora + 2 * 3600 + 15 * 60})
        self.assertEqual(dados["rate_limits"]["seven_day"]["used_percentage"], 70)
        self.assertEqual(resposta["state"]["five_hour"], {"pct": 40, "resets_at": self.agora + 8100})
        self.assertEqual(list(self.s.pasta.glob("*.tmp")), [])  # o temporário já foi trocado

    def test_reset_vazio_mantem_o_anterior_e_o_resto_do_ficheiro(self):
        self.gravar_ficheiro({"captured_at": 1, "outro": "fica", "rate_limits": {
            "five_hour": {"used_percentage": 10, "resets_at": self.agora + 600},
            "seven_day": {"used_percentage": 20, "resets_at": self.agora + 9000, "extra": 1}}})
        self.assertTrue(self.gravar(five_pct="35", five_reset="", week_pct="", week_reset="")["ok"])
        dados = self.ficheiro_json()
        self.assertEqual(dados["outro"], "fica")
        self.assertEqual(dados["rate_limits"]["five_hour"], {"used_percentage": 35, "resets_at": self.agora + 600})
        self.assertEqual(dados["rate_limits"]["seven_day"],
                         {"used_percentage": 20, "resets_at": self.agora + 9000, "extra": 1})

    def test_sem_anterior_pede_o_que_falta_e_nao_grava(self):
        resposta = self.gravar(five_pct="40", five_reset="", week_pct="", week_reset="qui 16:00")
        self.assertEqual(resposta, {"ok": False, "errors": {
            "five_reset": "Falta a hora do reset.", "week_pct": "Falta o %."}, "state": mock.ANY})
        self.assertFalse(self.ficheiro.exists())

    def test_janela_toda_vazia_sem_anterior_fica_de_fora(self):
        self.assertTrue(self.gravar(five_pct="40", five_reset="45m", week_pct="", week_reset="")["ok"])
        self.assertNotIn("seven_day", self.ficheiro_json()["rate_limits"])

    def test_anterior_ja_reposto_nao_conta(self):
        self.gravar_ficheiro({"rate_limits": {"five_hour": {"used_percentage": 10, "resets_at": self.agora - 5}}})
        resposta = self.gravar(five_pct="40", five_reset="")
        self.assertEqual(resposta["errors"], {"five_reset": "Falta a hora do reset."})

    def test_5h_expirada_aproveita_o_pct_mas_pede_reset_novo(self):
        # Nunca se grava uma hora no passado: o reset da 5 h expirada tem de ser dito de novo.
        self.gravar_ficheiro({"rate_limits": {"five_hour": {"used_percentage": 10, "resets_at": self.agora - 5}}})
        resposta = self.gravar(five_pct="", five_reset="")
        self.assertEqual(resposta["errors"], {"five_reset": "Falta a hora do reset."})
        self.assertTrue(self.gravar(five_pct="", five_reset="45m")["ok"])
        self.assertEqual(self.ficheiro_json()["rate_limits"]["five_hour"],
                         {"used_percentage": 10, "resets_at": self.agora + 45 * 60})

    def test_semanal_expirada_grava_com_o_reset_avancado(self):
        passado = self.agora - 86400
        self.gravar_ficheiro({"rate_limits": {"seven_day": {"used_percentage": 40, "resets_at": passado}}})
        self.assertTrue(self.gravar(week_pct="55", week_reset="")["ok"])
        self.assertEqual(self.ficheiro_json()["rate_limits"]["seven_day"],
                         {"used_percentage": 55, "resets_at": passado + 7 * 86400})

    def test_erros_de_formato_por_campo(self):
        resposta = self.gravar(five_pct="140", five_reset="6h", week_pct="x", week_reset="zz")
        self.assertEqual(resposta["errors"], {
            "five_pct": "Use um número inteiro de 0 a 100.", "five_reset": "Passa das 5 h: confira o valor.",
            "week_pct": "Use um número inteiro de 0 a 100.", "week_reset": "Use 14:30, 2h15, 45m ou qui 16:00."})

    def test_pedidos_estragados_ou_desconhecidos(self):
        self.assertEqual(self.pedir("set", "!!!")["ok"], False)
        self.assertIn("error", self.pedir("set", "!!!"))
        nao_objeto = base64.urlsafe_b64encode(b"[1]").decode("ascii")
        self.assertEqual(self.pedir("set", nao_objeto), {"ok": False, "error": "Pedido estragado."})
        self.assertEqual(self.pedir("xyz"), {"ok": False, "error": "Pedido desconhecido."})
        with mock.patch.object(limites(), "_gravar", side_effect=PermissionError("negado")):
            self.assertEqual(self.gravar(five_pct="40", five_reset="45m"),
                             {"ok": False, "error": "PermissionError: negado"})
        self.assertEqual(self.gravar(five_pct=40, five_reset="45m")["ok"], True)  # número em vez de texto
        self.assertEqual(self.pedir(), {"ok": False, "error": "Pedido desconhecido."})


class MostrarEEsconder(unittest.TestCase):

    def mostrar(self, ecra):
        with JanelasFalsas(ecra) as s:
            s.trocar("LIMITES_PREV", s.pasta / ".limites-prev")
            limites().limites_show()
            antes = s.pasta / ".limites-prev"
            return s.feitos, antes.read_text() if antes.exists() else None

    def test_mostra_com_foco_e_lembra_a_janela_de_antes(self):
        self.assertEqual(self.mostrar(Ecra({MODAL: 9}, primeiro_plano=40)),
                         ([("frente", 9), ("foco", 9), ("vigiar", 9)], "40"))

    def test_sem_widget_abre_o_limites(self):
        self.assertEqual(self.mostrar(Ecra())[0], [("widget", "limites")])

    def test_visivel_esconde_e_activa_a_barra(self):
        ecra = Ecra({MODAL: 9, BARRA: 5}, visiveis={9}, primeiro_plano=9)
        self.assertEqual(self.mostrar(ecra)[0], [("frente", 5)])

    def test_limites_hide(self):
        for janelas in ({MODAL: 9}, {}):
            with self.subTest(janelas=janelas):
                ecra = Ecra(janelas, visiveis={9}, primeiro_plano=40)
                with JanelasFalsas(ecra) as s:
                    s.trocar("LIMITES_PREV", s.pasta / ".limites-prev")
                    limites().limites_hide()
                self.assertEqual(ecra.visiveis, set() if janelas else {9})


class PontoDeEntrada(unittest.TestCase):

    def test_bar_helper_encaminha_os_pedidos(self):
        bh = SistemaFalso().bh
        modulo = sys.modules["bar_helper"]
        self.assertIs(modulo.COMANDOS[("limites",)], limites().limites_show)
        self.assertIs(modulo.COMANDOS[("limites-hide",)], limites().limites_hide)
        with mock.patch.object(modulo, "limites_cli") as cli:
            self.assertEqual(bh.main(["bar_helper.py", "limites", "state"]), 0)
        cli.assert_called_once_with(["state"])


if __name__ == "__main__":
    unittest.main()
