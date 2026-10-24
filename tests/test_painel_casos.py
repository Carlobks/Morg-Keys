"""Painel "Apps e arranque" (morg_painel): mostrar/esconder com o foco certo e casos do estado e do desfazer
que test_bar_helper_painel.py não fixava.
"""

import json
import os
import unittest
from pathlib import Path

from test_bar_helper_painel import painel
from test_janelas_zebar import Ecra, JanelasFalsas

PAINEL, BARRA = "Zebar - omarchy-catppuccin / apps", "Zebar - omarchy-catppuccin / bar"


class MostrarEEsconder(unittest.TestCase):

    def mostrar(self, ecra, widget_arranca=True, janela_aparece_aos=None, antes=None):
        with JanelasFalsas(ecra) as s:
            s.widget_arranca = widget_arranca
            if antes is not None:
                s.escrever("PANEL_PREV", antes)
            if janela_aparece_aos is not None:
                inicio = s.relogio.agora
                s.relogio.ao_avancar.append(
                    lambda agora: ecra.janelas.setdefault(PAINEL, 9) if agora - inicio >= janela_aparece_aos else 0)
            s.bh.panel_show()
            return s.feitos, s.ler("PANEL_PREV")

    def test_mostra_com_foco_e_lembra_a_janela_de_antes(self):
        self.assertEqual(self.mostrar(Ecra({PAINEL: 9}, primeiro_plano=40)),
                         ([("frente", 9), ("foco", 9), ("vigiar", 9)], "40"))
        for frente in (0, 9):
            with self.subTest(frente=frente):
                self.assertEqual(self.mostrar(Ecra({PAINEL: 9}, primeiro_plano=frente))[1], None)

    def test_sem_painel_abre_o_widget(self):
        feitos, _ = self.mostrar(Ecra(), janela_aparece_aos=0.4)
        self.assertEqual(feitos, [("widget", "apps"), ("frente", 9), ("foco", 9), ("vigiar", 9)])
        self.assertEqual(self.mostrar(Ecra(), widget_arranca=False)[0], [("widget", "apps")])
        self.assertEqual(self.mostrar(Ecra())[0], [("widget", "apps")])
        feitos, _ = self.mostrar(Ecra({}, visiveis={9}), janela_aparece_aos=0.2)
        self.assertEqual(feitos[1], ("frente", 9))

    def test_visivel_esconde_e_devolve_o_foco(self):
        ecra = Ecra({PAINEL: 9}, visiveis={9, 40}, primeiro_plano=9, outras={40})
        feitos, _ = self.mostrar(ecra, antes="40")
        self.assertEqual((feitos, ecra.visiveis), ([("frente", 40)], {40}))

    def test_esconder_sem_janela_de_antes_ativa_a_barra(self):
        casos = {"sem ficheiro": None, "lixo": "x", "fechada": "41", "invisível": "40", "noutro workspace": "666"}
        for nome, antes in casos.items():
            with self.subTest(caso=nome):
                ecra = Ecra({PAINEL: 9, BARRA: 5}, visiveis={9, 666}, primeiro_plano=9, outras={40, 666})
                self.assertEqual(self.mostrar(ecra, antes=antes)[0], [("frente", 5)])
        ecra = Ecra({PAINEL: 9}, visiveis={9}, primeiro_plano=9)
        self.assertEqual(self.mostrar(ecra)[0], [])  # nem barra: fica só escondido

    def test_esconder_quando_o_foco_ja_esta_noutra_janela_nao_mexe_no_foco(self):
        ecra = Ecra({PAINEL: 9}, visiveis={9}, primeiro_plano=40)
        self.assertEqual(self.mostrar(ecra, antes="40")[0], [])
        self.assertEqual(ecra.visiveis, set())

    def test_panel_hide(self):
        for janelas in ({PAINEL: 9}, {}):
            with self.subTest(janelas=janelas):
                ecra = Ecra(janelas, visiveis={9}, primeiro_plano=40)
                with JanelasFalsas(ecra) as s:
                    s.bh.panel_hide()
                self.assertEqual(ecra.visiveis, set() if janelas else {9})


class EstadoEComoAbrir(unittest.TestCase):

    def setUp(self):
        self.s = painel("Alt+O = Obsidian\n")
        self.addCleanup(self.s.__exit__, None, None, None)

    def test_estado_sem_apps_txt_nem_config(self):
        self.s.bh.APPS_FILE.unlink()
        self.s.bh.GLAZE_CONFIG.unlink()
        self.assertEqual(self.s.bh._panel_state(), {"keys": [], "fixed": [], "workspaces": [], "undo": 0})

    def test_launch_for_palavras_especiais_e_exe(self):
        bh = self.s.bh
        wt = str(Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WindowsApps" / "wt.exe")
        casa = str(Path.home())
        self.assertEqual(bh._launch_for("claude-code"), ("WindowsTerminal", {
            "file": wt, "args": f'-w new -d "{casa}" "{casa}\\.local\\bin\\claude.exe"'}))
        self.assertEqual(bh._launch_for("Explorador"), ("explorer", {"file": "explorer"}))
        self.assertEqual(bh._launch_for(r"C:\Apps\Notas.exe"), ("Notas", {"file": r"C:\Apps\Notas.exe"}))


class CasosDoDesfazer(unittest.TestCase):

    def setUp(self):
        self.s = painel("Alt+O = Obsidian\n", {"windows": []})
        self.addCleanup(self.s.__exit__, None, None, None)

    def test_marcar_o_depois_sem_pilha_ou_estragada(self):
        bh = self.s.bh
        bh._panel_mark_after()
        self.assertIsNone(self.s.ler("PANEL_UNDO"))
        for texto in ("[]", "{lixo"):
            self.s.escrever("PANEL_UNDO", texto)
            bh._panel_mark_after()
            self.assertEqual(self.s.ler("PANEL_UNDO"), texto)

    def test_pilha_vazia_nada_para_desfazer(self):
        self.s.escrever("PANEL_UNDO", "[]")
        self.assertEqual(self.s.bh._panel_undo(), "Nada para desfazer.")

    def test_desfaz_um_workspace_repondo_o_layout(self):
        bh = self.s.bh
        bh._panel_do({"op": "ws-add", "ws": "3", "value": "Obsidian"})
        self.assertIsNone(bh._panel_undo())
        self.assertEqual(json.loads(self.s.ler("LAYOUT_FILE")), {"windows": []})

    def test_desfeito_mas_o_apps_txt_antigo_tem_erros(self):
        self.s.escrever("PANEL_UNDO", json.dumps([{"apps": "lixo sem igual\n", "layout": '{"windows": []}'}]))
        erro = self.s.bh._panel_undo()
        self.assertTrue(erro.startswith("Desfeito, mas: linha 1: falta o '='"), erro)
        self.assertEqual(self.s.ler("APPS_FILE"), "lixo sem igual\n")


if __name__ == "__main__":
    unittest.main()
