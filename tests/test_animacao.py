"""Caracterização do Alt+Esc, E (`animacao_tap`): tocar passa à animação seguinte; segurar mostra-a ao largar.

Fase 2b da experiência 0001: fixa o comportamento antes de partir a função. O relógio do Windows
(`GetTickCount64`) deriva do relógio falso, para simular a repetição automática da tecla segurada.
"""

import unittest

from sistema_falso import Bomba, SistemaFalso

TRES_ANIMACOES = {"cafe": ("Café", "cafe.bmp", 1, 1), "lua": ("Lua", "lua.bmp", 1, 1), "sol": ("Sol", "sol.bmp", 1, 1)}


class MutexFalso:
    livre = True

    def __init__(self, nome, timeout_ms=2000):
        pass

    def __enter__(self):
        return MutexFalso.livre

    def __exit__(self, *erro):
        return False


class AnimacaoFalsa(SistemaFalso):
    """SistemaFalso com arranque.txt, .anim-tap, três animações e camada/pré-visualização gravadas."""

    def __enter__(self):
        super().__enter__()
        self.arranque_txt = self.pasta / "arranque.txt"
        self.arranque_txt.write_text("animacao = cafe\n", encoding="utf-8")
        self.toque = self.pasta / ".anim-tap"
        self.previsualizadas, self.camadas_escondidas = [], []
        self.trocar("ARRANQUE_FILE", self.arranque_txt)
        self.trocar("ANIM_TAP_FILE", self.toque)
        self.trocar("ANIMACOES", TRES_ANIMACOES)
        self.trocar("_NamedMutex", MutexFalso)
        self.trocar("kernel32", Bomba("kernel32", {"GetTickCount64": lambda: int(self.relogio.agora * 1000)}))
        self.trocar("animacao_preview", lambda name=None: self.previsualizadas.append(name))
        self.trocar("layer_hide", lambda: self.camadas_escondidas.append(True))
        MutexFalso.livre = True
        return self

    def animacao(self):
        return self.bh._arranque_cfg()["animacao"]

    def carregar(self, aos_segundos):
        """Uma chamada do atalho (pressão ou repetição) neste instante."""
        self.relogio.agora = aos_segundos
        self.bh.animacao_tap()


class TocarESegurar(unittest.TestCase):

    def test_tocar_passa_a_seguinte_sem_mostrar(self):
        with AnimacaoFalsa() as s:
            s.carregar(10.0)
            self.assertEqual(s.animacao(), "lua")
            self.assertEqual(s.toque.read_text(encoding="utf-8"), "10000 cafe tap -")
            s.carregar(11.0)
            self.assertEqual(s.animacao(), "sol")
            self.assertEqual(s.toque.read_text(encoding="utf-8"), "11000 lua tap cafe")
            s.carregar(12.0)
            self.assertEqual(s.animacao(), "cafe")  # dá a volta
            self.assertEqual((s.previsualizadas, s.camadas_escondidas, s.glaze.comandos), ([], [], []))

    def test_segurar_repoe_a_de_antes_da_pressao_e_mostra_ao_largar(self):
        with AnimacaoFalsa() as s:
            s.carregar(10.0)    # pressão: cafe -> lua
            s.carregar(10.5)    # 1.ª repetição (parece um 2.º toque): lua -> sol
            s.carregar(10.533)  # 2.ª repetição, a 33 ms: é segurar
            self.assertEqual(s.animacao(), "cafe")  # volta à de antes da pressão
            self.assertEqual(s.previsualizadas, ["cafe"])
            self.assertEqual(s.camadas_escondidas, [True])
            self.assertEqual(s.glaze.comandos, [("command", "wm-disable-binding-mode", "--name", "sistema")])
            self.assertGreater(s.relogio.agora - 10.533, 0.25)  # esperou que a tecla fosse largada

    def test_repeticoes_depois_de_detetado_o_segurar_nao_fazem_nada(self):
        with AnimacaoFalsa() as s:
            s.toque.write_text("9980 lua hold cafe", encoding="utf-8")
            s.carregar(10.0)
            self.assertEqual(s.toque.read_text(encoding="utf-8"), "10000 lua hold cafe")
            self.assertEqual((s.animacao(), s.previsualizadas), ("cafe", []))

    def test_mutex_ocupado_nao_faz_nada(self):
        with AnimacaoFalsa() as s:
            MutexFalso.livre = False
            s.carregar(10.0)
            self.assertEqual((s.animacao(), s.toque.exists()), ("cafe", False))

    def test_ficheiro_estragado_conta_como_toque_novo(self):
        with AnimacaoFalsa() as s:
            s.toque.write_text("lixo", encoding="utf-8")
            s.carregar(10.0)
            self.assertEqual(s.animacao(), "lua")
            self.assertEqual(s.toque.read_text(encoding="utf-8"), "10000 cafe tap -")


class EscolherEMostrar(unittest.TestCase):

    def test_animacao_set_seguinte_ou_indicada(self):
        with AnimacaoFalsa() as s:
            s.bh.animacao_set()
            self.assertEqual((s.animacao(), s.previsualizadas), ("lua", ["lua"]))
            s.bh.animacao_set("cafe")
            self.assertEqual((s.animacao(), s.previsualizadas), ("cafe", ["lua", "cafe"]))
            s.bh.animacao_set("nao-existe")
            self.assertEqual(s.animacao(), "lua")


if __name__ == "__main__":
    unittest.main()
