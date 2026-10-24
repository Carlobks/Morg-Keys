"""Janelas do Zebar (morg_janelas_zebar): guia Alt+K, barra, camada Alt+Esc e o filtro de repetição.

As janelas são uma tabela falsa (título -> hwnd, visíveis, primeiro plano) e o tempo é o relógio falso:
fixa-se quem mostra, quem esconde e para onde volta o foco, sem tocar no Windows.
"""

import sys
import unittest
from unittest import mock

from falsos_windows import Gravador
from sistema_falso import SistemaFalso

GUIA, BARRA = "Zebar - omarchy-catppuccin / guia", "Zebar - omarchy-catppuccin / bar"
CAMADA, PAINEL = "Zebar - omarchy-catppuccin / sistema", "Zebar - omarchy-catppuccin / apps"


class MutexFalso:
    livre = True

    def __init__(self, nome, timeout_ms=2000):
        self.nome = nome

    def __enter__(self):
        return MutexFalso.livre

    def __exit__(self, *erro):
        return False


class Ecra:
    """Janelas falsas: título -> hwnd, as visíveis, a do primeiro plano e o texto da janela da frente."""

    def __init__(self, janelas=None, visiveis=(), primeiro_plano=0, outras=()):
        self.janelas, self.visiveis = dict(janelas or {}), set(visiveis)
        self.primeiro_plano, self.outras, self.texto_da_frente = primeiro_plano, set(outras), ""

    def user32(self):
        return Gravador(
            "user32",
            FindWindowW=lambda classe, titulo: self.janelas.get(titulo, 0),
            IsWindowVisible=lambda h: h in self.visiveis,
            IsWindow=lambda h: h in self.outras or h in self.janelas.values(),
            GetForegroundWindow=lambda: self.primeiro_plano,
            ShowWindow=self._mostrar,
            GetWindowTextW=lambda h, buf, n: setattr(buf, "value", self.texto_da_frente),
        )

    def _mostrar(self, hwnd, comando):
        (self.visiveis.discard if comando == 0 else self.visiveis.add)(hwnd)
        return 1


class JanelasFalsas(SistemaFalso):

    def __init__(self, ecra, **kw):
        super().__init__(**kw)
        self.ecra = ecra
        self.feitos = []  # o que se pediu: ("frente", hwnd), ("widget", nome), …

    def __enter__(self):
        super().__enter__()
        self.u32 = self.ecra.user32()
        self.trocar("user32", self.u32)
        self.trocar("LAST_KEY_FILE", self.pasta / ".guide-last")
        self.trocar("PREV_FILE", self.pasta / ".guide-prev")
        self.trocar("_NamedMutex", MutexFalso)
        self.trocar("_is_cloaked", lambda h: h == 666)
        self.trocar("_bring_to_front", lambda h: self.feitos.append(("frente", h)))
        self.trocar("_focus_webview", lambda h: self.feitos.append(("foco", h)))
        self.trocar("_hide_when_unfocused", lambda h: self.feitos.append(("vigiar", h)))
        self.widget_arranca = True
        self.trocar("_start_widget", lambda pack, nome: self.feitos.append(("widget", nome)) or self.widget_arranca)
        self.tique = 10_000
        self.trocar("kernel32", Gravador("kernel32", GetTickCount64=lambda: self.tique))
        MutexFalso.livre = True
        return self


class RegistoFalso:
    """Faz de `winreg` (só o que _is_key_repeat lê)."""
    HKEY_CURRENT_USER = 1

    def __init__(self, atraso):
        self.atraso = atraso

    def OpenKey(self, raiz, caminho):
        if isinstance(self.atraso, Exception):
            raise self.atraso
        return mock.MagicMock()

    def QueryValueEx(self, chave, nome):
        return (self.atraso, 1)


class RepeticaoDoAltK(unittest.TestCase):

    def repete(self, atraso, intervalo_ms, antes=None):
        with JanelasFalsas(Ecra()) as s, mock.patch.dict(sys.modules, {"winreg": RegistoFalso(atraso)}):
            if antes is not None:
                (s.pasta / ".guide-last").write_text(antes)
            primeira = s.bh._is_key_repeat()
            s.tique += intervalo_ms
            segunda = s.bh._is_key_repeat()
            return primeira, segunda, (s.pasta / ".guide-last").read_text()

    def test_atraso_do_teclado_mais_200_ms(self):
        # KeyboardDelay 1 -> (1+1)*250 = 500 ms; mais 200 ms de folga.
        self.assertEqual(self.repete("1", 699), (False, True, "10699"))
        self.assertEqual(self.repete("1", 700), (False, False, "10700"))

    def test_registo_ilegivel_usa_500_ms(self):
        for atraso in (OSError("sem chave"), "x"):
            with self.subTest(atraso=atraso):
                self.assertEqual(self.repete(atraso, 699)[:2], (False, True))
                self.assertEqual(self.repete(atraso, 700)[:2], (False, False))

    def test_ficheiro_estragado_conta_como_sem_toque_anterior(self):
        self.assertEqual(self.repete("0", 10, antes="lixo")[:2], (False, True))

    def test_relogio_para_tras_nao_e_repeticao(self):
        self.assertEqual(self.repete("0", 0, antes="99999")[0], False)

    def test_mutex_ocupado_e_repeticao(self):
        with JanelasFalsas(Ecra()) as s, mock.patch.dict(sys.modules, {"winreg": RegistoFalso("0")}):
            MutexFalso.livre = False
            self.assertTrue(s.bh._is_key_repeat())
            self.assertFalse((s.pasta / ".guide-last").exists())


class GuiaAltK(unittest.TestCase):

    def abrir(self, ecra, repeticao=False, antes=None, widget_arranca=True, janela_aparece_aos=None):
        with JanelasFalsas(ecra) as s:
            s.trocar("_is_key_repeat", lambda: repeticao)
            s.widget_arranca = widget_arranca
            if antes is not None:
                (s.pasta / ".guide-prev").write_text(antes)
            if janela_aparece_aos is not None:
                inicio = s.relogio.agora
                s.relogio.ao_avancar.append(
                    lambda agora: ecra.janelas.setdefault(GUIA, 7) if agora - inicio >= janela_aparece_aos else None)
            s.bh.guide()
            prev = s.pasta / ".guide-prev"
            return s.feitos, (prev.read_text() if prev.exists() else None)

    def test_repeticao_nao_faz_nada(self):
        self.assertEqual(self.abrir(Ecra({GUIA: 7}), repeticao=True), ([], None))

    def test_mostra_lembra_a_janela_de_antes_e_da_o_foco(self):
        feitos, prev = self.abrir(Ecra({GUIA: 7}, primeiro_plano=40))
        self.assertEqual(feitos, [("frente", 7), ("foco", 7), ("vigiar", 7)])
        self.assertEqual(prev, "40")

    def test_sem_primeiro_plano_ou_ja_e_o_guia_nao_lembra(self):
        for frente in (0, 7):
            with self.subTest(frente=frente):
                feitos, prev = self.abrir(Ecra({GUIA: 7}, primeiro_plano=frente))
                self.assertEqual((feitos[0], prev), (("frente", 7), None))

    def test_visivel_fecha_devolvendo_o_foco_a_janela_de_antes(self):
        feitos, _ = self.abrir(Ecra({GUIA: 7}, visiveis={7, 40}, outras={40}), antes="40")
        self.assertEqual(feitos, [("frente", 40)])

    def test_visivel_sem_janela_de_antes_valida_so_esconde(self):
        casos = {"sem ficheiro": (None, set()), "lixo": ("x", set()), "a própria": ("7", set()),
                 "fechada": ("41", set()), "invisível": ("40", set()), "noutro workspace": ("666", {666})}
        for nome, (antes, mais_visiveis) in casos.items():
            with self.subTest(caso=nome):
                ecra = Ecra({GUIA: 7}, visiveis={7, *mais_visiveis}, outras={40, 666})
                feitos, _ = self.abrir(ecra, antes=antes)
                self.assertEqual((feitos, ecra.visiveis - {666}), ([], set()))

    def test_sem_guia_abre_o_widget_e_espera_que_se_esconda(self):
        ecra = Ecra()
        feitos, _ = self.abrir(ecra, janela_aparece_aos=0.5)
        self.assertEqual(feitos, [("widget", "guia"), ("frente", 7), ("foco", 7), ("vigiar", 7)])

    def test_widget_visivel_ate_ao_fim_da_espera_mostra_na_mesma(self):
        ecra = Ecra({}, visiveis={7})
        feitos, _ = self.abrir(ecra, janela_aparece_aos=0.3)
        self.assertEqual(feitos[0], ("widget", "guia"))
        self.assertEqual(feitos[1], ("frente", 7))

    def test_widget_que_nao_arranca_ou_nao_aparece_desiste(self):
        self.assertEqual(self.abrir(Ecra(), widget_arranca=False)[0], [("widget", "guia")])
        self.assertEqual(self.abrir(Ecra())[0], [("widget", "guia")])

    def test_guide_hide(self):
        for janelas, visiveis in (({GUIA: 7}, set()), ({}, {7})):
            with self.subTest(janelas=janelas):
                ecra = Ecra(janelas, visiveis={7})
                with JanelasFalsas(ecra) as s:
                    s.bh.guide_hide()
                self.assertEqual(ecra.visiveis, visiveis)


class GuiaEscondidoNoArranque(unittest.TestCase):

    def test_esconde_o_que_ficou_visivel_menos_o_que_tem_o_foco(self):
        ecra = Ecra({GUIA: 7, CAMADA: 8}, visiveis={7, 8}, primeiro_plano=8)
        with JanelasFalsas(ecra) as s:
            inicio = s.relogio.agora
            s.relogio.ao_avancar.append(lambda agora: ecra.janelas.setdefault(PAINEL, 9) if agora - inicio > 5 else 0)
            s.trocar("_refocus_if_zebar_stole", lambda: s.feitos.append("refocar"))
            s.bh.guide_ensure_hidden()
            self.assertEqual(ecra.visiveis, {8})
            self.assertEqual(s.feitos, ["refocar"])
            self.assertEqual(s.relogio.agora - inicio, 15)

    def test_espera_que_o_guia_apareca_ate_60_s(self):
        ecra = Ecra()
        with JanelasFalsas(ecra) as s:
            inicio = s.relogio.agora
            s.relogio.ao_avancar.append(lambda agora: ecra.janelas.setdefault(GUIA, 7) if agora - inicio >= 3 else 0)
            s.trocar("_refocus_if_zebar_stole", lambda: s.feitos.append("refocar"))
            s.bh.guide_ensure_hidden()
            self.assertEqual((s.relogio.agora - inicio, s.feitos), (18, ["refocar"]))
        with JanelasFalsas(Ecra()) as s:
            inicio = s.relogio.agora
            s.bh.guide_ensure_hidden()
            self.assertEqual((s.relogio.agora - inicio, s.feitos), (60, []))

    def test_refocar_so_se_a_frente_for_o_tauri_app_e_o_glaze_tiver_uma_janela(self):
        respostas = {"window": {"data": {"focused": {"type": "window", "id": "j9"}}},
                     "workspace": {"data": {"focused": {"type": "workspace", "id": "w1"}}}}
        for texto, focado, esperado in (("Tauri App", "window", [("command", "focus", "--container-id", "j9")]),
                                        ("Tauri App", "workspace", []), ("Outra", "window", [])):
            with self.subTest(texto=texto, focado=focado):
                ecra = Ecra()
                ecra.texto_da_frente = texto
                with JanelasFalsas(ecra) as s:
                    comandos = []
                    s.trocar("_glaze", lambda *a, f=focado, c=comandos: c.append(a) or respostas[f])
                    s.bh._refocus_if_zebar_stole()
                self.assertEqual([c for c in comandos if c[0] == "command"], esperado)


class BarraECamada(unittest.TestCase):

    def test_bar_toggle(self):
        for janelas, visiveis, depois, widget in (({}, set(), set(), True), ({BARRA: 5}, {5}, set(), False),
                                                  ({BARRA: 5}, set(), {5}, False)):
            with self.subTest(janelas=janelas, visiveis=visiveis):
                ecra = Ecra(janelas, visiveis)
                with JanelasFalsas(ecra) as s:
                    s.bh.bar_toggle()
                self.assertEqual(ecra.visiveis, depois)
                self.assertEqual(s.feitos == [("widget", "bar")], widget)
                if visiveis == set() and janelas:
                    self.assertEqual(s.u32.de("ShowWindow"), [(5, 8)])  # SW_SHOWNA: sem roubar o foco

    def test_layer_show_e_hide(self):
        ecra = Ecra({CAMADA: 6})
        with JanelasFalsas(ecra) as s:
            s.bh.layer_show()
            self.assertEqual(ecra.visiveis, {6})
            s.bh.layer_hide()
            self.assertEqual(ecra.visiveis, set())
        with JanelasFalsas(Ecra()) as s:
            s.bh.layer_show()
            s.bh.layer_hide()
            self.assertEqual(s.feitos, [("widget", "sistema")])
            self.assertEqual(s.u32.de("ShowWindow"), [])


if __name__ == "__main__":
    unittest.main()
