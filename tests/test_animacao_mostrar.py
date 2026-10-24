"""Pré-visualização da animação do arranque (`animacao_preview`) e os casos-limite do segurar (Alt+Esc, E).

Completa test_animacao.py: o ecrã de arranque, o Zebar e o mutex do arranque são falsos.
"""

import json
import unittest

from falsos_windows import Gravador
from sistema_falso import SistemaFalso
from test_animacao import TRES_ANIMACOES, AnimacaoFalsa


class PreVisualizar(SistemaFalso):

    def __init__(self, arranque_a_correr=False, splash_aberto=False, zebar_existe=True):
        super().__init__()
        self.arranque_a_correr, self.splash_aberto, self.zebar_existe = arranque_a_correr, splash_aberto, zebar_existe

    def __enter__(self):
        super().__enter__()
        zebar = self.pasta / "zebar.exe"
        if self.zebar_existe:
            zebar.write_text("")
        self.lancados = []
        (self.pasta / "arranque.txt").write_text("animacao = sol\n", encoding="utf-8")
        self.trocar("ARRANQUE_FILE", self.pasta / "arranque.txt")
        self.trocar("ANIMACOES", TRES_ANIMACOES)
        self.trocar("ZEBAR", zebar)
        self.trocar("PROGRESS_FILE", self.pasta / "progress.json")
        self.trocar("_popen_detached", lambda cmd, **kw: self.lancados.append([str(c) for c in cmd]))
        self.k32 = Gravador("kernel32", OpenMutexW=lambda *a: 3 if self.arranque_a_correr else 0, CloseHandle=1)
        self.trocar("kernel32", self.k32)
        self.trocar("user32", Gravador("user32", FindWindowW=lambda c, t: 14 if self.splash_aberto else 0))
        return self

    def progresso(self):
        caminho = self.pasta / "progress.json"
        return json.loads(caminho.read_text(encoding="utf-8")) if caminho.exists() else None


class MostrarAnimacao(unittest.TestCase):

    def test_mostra_as_etapas_de_exemplo_e_acaba(self):
        with PreVisualizar() as s:
            inicio = s.relogio.agora
            s.bh.animacao_preview("lua")
            progresso = s.progresso()
            self.assertEqual((progresso["animacao"], progresso["preview"], progresso["fim"]), ("lua", True, True))
            self.assertEqual([(p["id"], p["label"], p["state"]) for p in progresso["steps"]], [
                ("anim", "Animação: Lua", "feito"), ("barra", "Barra", "feito"),
                ("glazewm", "Gestor de janelas", "feito"), ("apps", "Apps", "feito")])
            self.assertEqual(s.lancados, [[str(s.bh.ZEBAR), "start-widget-preset", "--pack", "omarchy-catppuccin",
                                           "--widget-name", "splash", "--preset", "default"]])
            self.assertAlmostEqual(s.relogio.agora - inicio, 0.8 + 4 * 0.9 + 1.2, places=5)

    def test_sem_nome_valido_usa_a_do_arranque_txt(self):
        with PreVisualizar() as s:
            s.bh.animacao_preview("nao-existe")
            self.assertEqual(s.progresso()["animacao"], "sol")

    def test_nao_mexe_durante_o_arranque_com_o_splash_aberto_ou_sem_zebar(self):
        for caso in ({"arranque_a_correr": True}, {"splash_aberto": True}, {"zebar_existe": False}):
            with self.subTest(**caso), PreVisualizar(**caso) as s:
                s.bh.animacao_preview()
                self.assertEqual((s.lancados, s.progresso()), ([], None))
                if caso.get("arranque_a_correr"):
                    self.assertEqual(s.k32.nomes(), ["OpenMutexW", "CloseHandle"])


class SegurarCasosLimite(unittest.TestCase):

    def segurar(self, conteudo, antes="-", prev="-"):
        with AnimacaoFalsa() as s:
            inicio = s.relogio.agora
            if conteudo is not None:
                s.toque.write_text(conteudo, encoding="utf-8")
            if conteudo == "atualizado":  # tecla nunca largada: o ficheiro é sempre de agora
                s.relogio.ao_avancar.append(
                    lambda agora: s.toque.write_text(f"{int(agora * 1000)} x hold y", encoding="utf-8"))
            s.bh._anim_segurar(prev, antes)
            return s.animacao(), s.previsualizadas, s.relogio.agora - inicio

    def test_sem_animacao_conhecida_nao_grava_e_mostra_a_atual(self):
        self.assertEqual(self.segurar(None)[:2], ("cafe", [None]))

    def test_ficheiro_apagado_ou_estragado_deixa_de_esperar(self):
        for conteudo in (None, "lixo", ""):
            with self.subTest(conteudo=conteudo):
                animacao, mostradas, duracao = self.segurar(conteudo, prev="lua")
                self.assertEqual((animacao, mostradas), ("lua", ["lua"]))
                self.assertAlmostEqual(duracao, 0.05, places=5)

    def test_tecla_que_nunca_e_largada_desiste_aos_15_s(self):
        animacao, mostradas, duracao = self.segurar("atualizado", antes="sol", prev="lua")
        self.assertEqual((animacao, mostradas), ("sol", ["sol"]))
        self.assertGreaterEqual(duracao, 15)


if __name__ == "__main__":
    unittest.main()
