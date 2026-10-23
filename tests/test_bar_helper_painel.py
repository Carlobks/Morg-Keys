"""Caracterização do painel "Apps e arranque" (Alt+Esc, C): `_panel_do`, `_panel_undo`, `panel_cli`.

Fase 1 da experiência 0001: fixa o comportamento de 2026-10-23. Ficheiros e GlazeWM falsos (sistema_falso).
"""

import base64
import contextlib
import io
import json
import unittest

from sistema_falso import SistemaFalso, config_minimo

MENU = [{"Name": "Google Chrome", "AppID": "Chrome"}, {"Name": "Obsidian", "AppID": "md.obsidian"},
        {"Name": "Notas", "AppID": r"C:\Apps\notas.exe"}]


class MutexFalso:
    """Faz de `_NamedMutex` (o real usa o kernel32): entra sempre, ou nunca (ocupado)."""

    livre = True

    def __init__(self, nome, timeout_ms=2000):
        self.nome = nome

    def __enter__(self):
        return MutexFalso.livre

    def __exit__(self, *erro):
        return False


def painel(apps_txt="", layout=None):
    """SistemaFalso com apps.txt, config.yaml e (opcional) layout.json escritos."""
    s = SistemaFalso(apps_do_menu=MENU).__enter__()
    s.escrever("APPS_FILE", apps_txt)
    s.escrever("GLAZE_CONFIG", config_minimo(s.bh))
    if layout is not None:
        s.escrever("LAYOUT_FILE", json.dumps(layout))
    return s


def layout_de(s):
    return json.loads(s.ler("LAYOUT_FILE"))


class MudarTeclas(unittest.TestCase):

    def setUp(self):
        self.s = painel("Alt+O = Obsidian\n")
        self.addCleanup(self.s.__exit__, None, None, None)

    def test_key_acrescenta_e_aplica(self):
        self.assertIsNone(self.s.bh._panel_do({"op": "key", "key": "Alt+Shift+B", "value": "Google Chrome"}))
        self.assertEqual(self.s.ler("APPS_FILE"), "Alt+O = Obsidian\nAlt+Shift+B      = Google Chrome\n")
        self.assertIn("bindings: ['alt+shift+b']", self.s.ler("GLAZE_CONFIG"))
        self.assertEqual(json.loads(self.s.ler("PANEL_UNDO")), [{"apps": "Alt+O = Obsidian\n", "layout": None}])

    def test_key_numa_tecla_ocupada_substitui(self):
        self.s.bh._panel_do({"op": "key", "key": "Alt+O", "value": "Google Chrome"})
        self.assertEqual(self.s.ler("APPS_FILE"), "Alt+O            = Google Chrome\n")

    def test_key_com_from_move_de_tecla(self):
        self.s.bh._panel_do({"op": "key", "key": "Alt+P", "value": "Obsidian", "from": "Alt+O"})
        self.assertEqual(self.s.ler("APPS_FILE"), "Alt+P            = Obsidian\n")

    def test_unkey_tira(self):
        self.assertIsNone(self.s.bh._panel_do({"op": "unkey", "key": "Alt+O"}))
        self.assertEqual(self.s.ler("APPS_FILE"), "\n")

    def test_pedidos_invalidos(self):
        bh = self.s.bh
        self.assertEqual(bh._panel_do({"op": "key", "key": "Ctrl+B", "value": "x"}), "Tecla inválida.")
        self.assertEqual(bh._panel_do({"op": "key", "key": "Alt+B", "value": " "}), "App inválida.")
        self.assertEqual(bh._panel_do({"op": "key", "key": "Alt+B", "value": "a\nb"}), "App inválida.")
        self.assertEqual(bh._panel_do({"op": "nada"}), "Pedido desconhecido.")
        self.assertIsNone(self.s.ler("PANEL_UNDO"))

    def test_erro_ao_aplicar_repoe_o_apps_txt_e_o_desfazer(self):
        erro = self.s.bh._panel_do({"op": "key", "key": "Alt+H", "value": "Obsidian"})
        self.assertEqual(erro, "Não mudei nada: Alt+H já é usado por outro atalho do sistema")
        self.assertEqual(self.s.ler("APPS_FILE"), "Alt+O = Obsidian\n")
        self.assertEqual(json.loads(self.s.ler("PANEL_UNDO")), [])


LAYOUT_DOIS_WORKSPACES = {"saved_at": 1, "windows": [
    {"workspace": "1", "process": "chrome", "title_hash": "aa"},
    {"workspace": "2", "process": "Obsidian", "title_hash": "", "label": "Obsidian", "value": "Obsidian",
     "launch": {"file": "shell:AppsFolder\\md.obsidian"}},
]}


class MudarWorkspaces(unittest.TestCase):

    def setUp(self):
        self.s = painel("", json.loads(json.dumps(LAYOUT_DOIS_WORKSPACES)))
        self.addCleanup(self.s.__exit__, None, None, None)

    def test_ws_add_de_uma_app_do_menu(self):
        self.assertIsNone(self.s.bh._panel_do({"op": "ws-add", "ws": "3", "value": "Google Chrome"}))
        nova = layout_de(self.s)["windows"][-1]
        self.assertEqual(nova, {"workspace": "3", "title_hash": "", "label": "Google Chrome", "value": "Google Chrome",
                                "launch": {"file": "shell:AppsFolder\\Chrome"}})

    def test_ws_add_de_uma_app_classica_ja_sabe_o_processo(self):
        self.s.bh._panel_do({"op": "ws-add", "ws": "4", "value": "Notas"})
        self.assertEqual(layout_de(self.s)["windows"][-1]["process"], "notas")

    def test_ws_add_web_e_terminal(self):
        self.s.bh._panel_do({"op": "ws-add", "ws": "5", "value": "web: https://mail.google.com", "label": "Gmail"})
        nova = layout_de(self.s)["windows"][-1]
        self.assertEqual((nova["process"], nova["label"], nova["launch"]),
                         ("chrome", "Gmail", {"file": "chrome", "args": "--app=https://mail.google.com"}))
        self.s.bh._panel_do({"op": "ws-add", "ws": "6", "value": "Terminal"})
        self.assertEqual(layout_de(self.s)["windows"][-1]["process"], "WindowsTerminal")

    def test_ws_add_invalido(self):
        bh = self.s.bh
        self.assertEqual(bh._panel_do({"op": "ws-add", "ws": "11", "value": "Obsidian"}), "Workspace ou app inválidos.")
        self.assertEqual(bh._panel_do({"op": "ws-add", "ws": "1", "value": ""}), "Workspace ou app inválidos.")
        self.assertEqual(bh._panel_do({"op": "ws-add", "ws": "1", "value": "Photoshop"}),
                         "Não encontrei a app 'Photoshop' neste PC.")
        self.assertEqual(bh._panel_do({"op": "ws-add", "ws": "1", "value": "web: x.pt"}),
                         "Não encontrei a app 'web: x.pt' neste PC.")

    def test_ws_move_e_ws_del(self):
        bh = self.s.bh
        self.assertIsNone(bh._panel_do({"op": "ws-move", "index": 0, "ws": "7"}))
        self.assertEqual(layout_de(self.s)["windows"][0]["workspace"], "7")
        self.assertIsNone(bh._panel_do({"op": "ws-del", "index": 1}))
        self.assertEqual(len(layout_de(self.s)["windows"]), 1)
        self.assertEqual(len(json.loads(self.s.ler("PANEL_UNDO"))), 2)

    def test_ws_move_para_o_mesmo_nao_guarda_desfazer(self):
        self.assertIsNone(self.s.bh._panel_do({"op": "ws-move", "index": 0, "ws": "1"}))
        self.assertIsNone(self.s.ler("PANEL_UNDO"))

    def test_indice_invalido_ou_painel_desatualizado(self):
        bh = self.s.bh
        self.assertEqual(bh._panel_do({"op": "ws-del", "index": 5}), "Essa app já não está nesse workspace.")
        self.assertEqual(bh._panel_do({"op": "ws-del", "index": "0"}), "Essa app já não está nesse workspace.")
        self.assertEqual(bh._panel_do({"op": "ws-del", "index": 1, "expect_ws": "1", "expect_label": "Obsidian"}),
                         "O painel estava desatualizado: veja de novo e repita.")
        self.assertEqual(bh._panel_do({"op": "ws-del", "index": 1, "expect_ws": "2", "expect_label": "Outra"}),
                         "O painel estava desatualizado: veja de novo e repita.")
        self.assertEqual(bh._panel_do({"op": "ws-move", "index": 0, "ws": "0"}), "Workspace inválido.")
        self.assertEqual(len(layout_de(self.s)["windows"]), 2)

    def test_expect_certo_deixa_mexer(self):
        self.assertIsNone(self.s.bh._panel_do({"op": "ws-del", "index": 1, "expect_ws": "2",
                                               "expect_label": "Obsidian"}))
        self.assertEqual([w["process"] for w in layout_de(self.s)["windows"]], ["chrome"])


class Desfazer(unittest.TestCase):

    def setUp(self):
        self.s = painel("Alt+O = Obsidian\n")
        self.addCleanup(self.s.__exit__, None, None, None)

    def test_nada_para_desfazer(self):
        self.assertEqual(self.s.bh._panel_undo(), "Nada para desfazer.")

    def test_desfaz_tecla_e_reaplica(self):
        bh = self.s.bh
        bh._panel_do({"op": "key", "key": "Alt+B", "value": "Google Chrome"})
        bh._panel_mark_after()
        self.s.glaze.comandos.clear()
        self.assertIsNone(bh._panel_undo())
        self.assertEqual(self.s.ler("APPS_FILE"), "Alt+O = Obsidian\n")
        self.assertNotIn("alt+b", self.s.ler("GLAZE_CONFIG"))
        self.assertEqual(self.s.glaze.comandos, [("command", "wm-reload-config")])

    def test_desfaz_o_primeiro_workspace_apaga_o_layout(self):
        bh = self.s.bh
        bh._panel_do({"op": "ws-add", "ws": "3", "value": "Obsidian"})
        bh._panel_mark_after()
        self.assertIsNone(bh._panel_undo())
        self.assertIsNone(self.s.ler("LAYOUT_FILE"))

    def test_recusa_se_os_ficheiros_mudaram_fora_do_painel(self):
        bh = self.s.bh
        bh._panel_do({"op": "key", "key": "Alt+B", "value": "Google Chrome"})
        bh._panel_mark_after()
        self.s.escrever("APPS_FILE", "Alt+B = Obsidian\n")  # ex.: o utilizador editou o apps.txt
        self.assertEqual(bh._panel_undo(), "Não desfiz: os atalhos ou o arranque mudaram fora do painel depois disso.")
        self.assertEqual(self.s.ler("PANEL_UNDO"), "[]")
        self.assertEqual(self.s.ler("APPS_FILE"), "Alt+B = Obsidian\n")

    def test_pilha_limitada(self):
        bh = self.s.bh
        for n in range(bh.PANEL_UNDO_MAX + 5):
            bh._panel_do({"op": "ws-add", "ws": "1", "value": "Obsidian", "label": f"O{n}"})
        self.assertEqual(len(json.loads(self.s.ler("PANEL_UNDO"))), bh.PANEL_UNDO_MAX)


class RespostasAPagina(unittest.TestCase):

    def setUp(self):
        self.s = painel("Alt+O = Obsidian\n", {"windows": [{"workspace": "2", "process": "chrome", "title_hash": ""}]})
        self.addCleanup(self.s.__exit__, None, None, None)
        self.addCleanup(setattr, MutexFalso, "livre", True)
        self.s.trocar("_NamedMutex", MutexFalso)

    def pedir(self, *args):
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            self.s.bh.panel_cli(list(args))
        texto = saida.getvalue()
        self.assertTrue(texto.isascii())
        return json.loads(texto)

    def do(self, op):
        return self.pedir("do", base64.urlsafe_b64encode(json.dumps(op).encode()).decode().rstrip("="))

    def test_state(self):
        resposta = self.pedir("state")
        self.assertEqual(resposta["state"]["keys"], [{"key": "alt+o", "value": "Obsidian"}])
        self.assertEqual(resposta["state"]["workspaces"], [{"index": 0, "workspace": "2", "label": "Google Chrome",
                                                            "process": "chrome", "value": None}])
        self.assertIn("alt+shift+e", resposta["state"]["fixed"])
        self.assertEqual(resposta["state"]["undo"], 0)

    def test_apps_filtra_o_menu(self):
        self.s.apps_do_menu += [{"Name": "Uninstall X", "AppID": "u"}, {"Name": "Ajuda", "AppID": "a.chm"},
                                {"Name": "obsidian", "AppID": "dup"}]
        nomes = [a["name"] for a in self.pedir("apps")["apps"]]
        self.assertEqual(nomes, ["Google Chrome", "Notas", "Obsidian"])

    def test_do_e_undo_marcam_o_depois(self):
        resposta = self.do({"op": "key", "key": "Alt+B", "value": "Google Chrome"})
        self.assertEqual((resposta["ok"], resposta["error"], resposta["state"]["undo"]), (True, None, 1))
        self.assertIn("after", json.loads(self.s.ler("PANEL_UNDO"))[-1])
        resposta = self.pedir("undo")
        self.assertEqual((resposta["ok"], resposta["state"]["undo"]), (True, 0))

    def test_ocupado(self):
        MutexFalso.livre = False
        resposta = self.do({"op": "unkey", "key": "Alt+O"})
        self.assertEqual((resposta["ok"], resposta["error"]), (False, "Ocupado, tente outra vez."))
        self.assertEqual(self.s.ler("APPS_FILE"), "Alt+O = Obsidian\n")

    def test_pedido_desconhecido_e_excecoes_respondem_sempre(self):
        self.assertEqual(self.pedir("xyz"), {"ok": False, "error": "Pedido desconhecido."})
        resposta = self.pedir("do", "!!!nao-e-base64")
        self.assertFalse(resposta["ok"])
        self.assertIn("Error", resposta["error"])


if __name__ == "__main__":
    unittest.main()
