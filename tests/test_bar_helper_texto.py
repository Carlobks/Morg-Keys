"""Caracterização das funções puras do bar_helper.py (teclas, apps.txt, config.yaml, árvore do GlazeWM).

Testes de caracterização (fase 1 da experiência 0001): fixam o comportamento de 2026-10-23 antes da
refatoração. Se um falhar depois de refatorar, o comportamento mudou — confirmar se foi de propósito.
"""

import unittest

from sistema_falso import carregar_bar_helper, config_minimo

bh = carregar_bar_helper()


class Teclas(unittest.TestCase):

    def test_parse_key_aceita_alt_e_alt_shift(self):
        self.assertEqual(bh._parse_key("Alt+Shift+B"), "alt+shift+b")
        self.assertEqual(bh._parse_key(" alt + 7 "), "alt+7")
        self.assertEqual(bh._parse_key("Alt+Enter"), "alt+enter")
        self.assertEqual(bh._parse_key("Alt+Espaço"), "alt+space")
        self.assertEqual(bh._parse_key("Alt+espaco"), "alt+space")

    def test_parse_key_recusa_o_resto(self):
        for texto in ["Ctrl+B", "Alt+Ctrl+B", "Shift+B", "Alt+Win+B", "Alt+F1", "Alt+", "", "Alt+Shift+ab", "Alt+-"]:
            with self.subTest(texto=texto):
                self.assertIsNone(bh._parse_key(texto))

    def test_key_text_volta_a_forma_do_apps_txt(self):
        self.assertEqual(bh._key_text("alt+shift+b"), "Alt+Shift+B")
        self.assertEqual(bh._key_text("alt+enter"), "Alt+Enter")
        self.assertEqual(bh._key_text("alt+space"), "Alt+Space")
        self.assertEqual(bh._key_text("alt+7"), "Alt+7")


MENU_INICIAR = {"google chrome": "Chrome", "obsidian": "md.obsidian", "microsoft edge": "MSEdge",
                "edge tools": "EdgeTools", "app clássica": r"C:\Program Files\X\x.exe"}


class ResolverApps(unittest.TestCase):

    def test_palavras_especiais(self):
        self.assertEqual(bh._resolve_app("Terminal", {}), bh.SPECIAL_APPS["terminal"])
        self.assertEqual(bh._resolve_app("claude-code", {}), bh.SPECIAL_APPS["claude-code"])
        self.assertEqual(bh._resolve_app("Explorador", {}), "shell-exec explorer")

    def test_web_so_com_http(self):
        self.assertEqual(bh._resolve_app("web: https://x.pt", {}), "shell-exec chrome --app=https://x.pt")
        self.assertIsNone(bh._resolve_app("web: x.pt", {}))

    def test_nome_do_menu_iniciar_exato_e_parcial_unico(self):
        self.assertEqual(bh._resolve_app("Google Chrome", MENU_INICIAR), 'shell-exec explorer "shell:AppsFolder\\Chrome"')
        self.assertEqual(bh._resolve_app("obsid", MENU_INICIAR), 'shell-exec explorer "shell:AppsFolder\\md.obsidian"')

    def test_nome_parcial_ambiguo_ou_inexistente(self):
        self.assertIsNone(bh._resolve_app("edge", MENU_INICIAR))  # "microsoft edge" e "edge tools"
        self.assertIsNone(bh._resolve_app("Photoshop", MENU_INICIAR))

    def test_appid_com_espacos_vai_entre_aspas(self):
        self.assertEqual(bh._resolve_app("App clássica", MENU_INICIAR),
                         'shell-exec explorer "shell:AppsFolder\\C:\\Program Files\\X\\x.exe"')

    def test_exe_inexistente_cai_para_o_menu(self):
        self.assertIsNone(bh._resolve_app(r"C:\nao\existe.exe", {}))


class AtalhosFixos(unittest.TestCase):

    def test_le_os_atalhos_fora_do_bloco_gerado(self):
        bloco = ["  # X", "  - commands: ['shell-exec x']", "    bindings: ['alt+shift+x']"]
        fixos = bh._fixed_bindings(config_minimo(bh, bloco))
        self.assertEqual(fixos, {"alt+h", "alt+left", "alt+shift+space", "alt+shift+e"})

    def test_sem_marcadores_le_tudo(self):
        texto = "keybindings:\n  - commands: ['a']\n    bindings: ['alt+a']\n"
        self.assertEqual(bh._fixed_bindings(texto), {"alt+a"})


class LinhasDoAppsTxt(unittest.TestCase):

    def test_apps_entries_ignora_comentarios_e_linhas_invalidas(self):
        linhas = ["# comentário", "", "Alt+Shift+B = Google Chrome", "sem igual", "Ctrl+X = nada",
                  "  Alt+O=Obsidian  "]
        self.assertEqual(bh._apps_entries(linhas), [(2, "alt+shift+b", "Google Chrome"), (5, "alt+o", "Obsidian")])


class ArvoreDoGlaze(unittest.TestCase):

    def test_windows_by_workspace_percorre_divisoes(self):
        workspaces = [
            {"name": "1", "children": [
                {"type": "window", "id": "a"},
                {"type": "split", "children": [{"type": "window", "id": "b"}, {"type": "window", "id": "c"}]}]},
            {"name": "2", "children": [{"type": "window", "id": "d"}]},
        ]
        ids = [(ws, w["id"]) for ws, w in bh._windows_by_workspace(workspaces)]
        self.assertEqual(ids, [("1", "a"), ("1", "b"), ("1", "c"), ("2", "d")])

    def test_title_hash_estavel_e_curto(self):
        self.assertEqual(bh._title_hash("Caixa de entrada"), bh._title_hash("Caixa de entrada"))
        self.assertEqual(len(bh._title_hash("x")), 16)
        self.assertEqual(bh._title_hash(None), bh._title_hash(""))
        self.assertNotEqual(bh._title_hash("a"), bh._title_hash("b"))

    def test_entry_label(self):
        self.assertEqual(bh._entry_label({"label": "Gmail", "process": "chrome"}), "Gmail")
        self.assertEqual(bh._entry_label({"process": "chrome"}), "Google Chrome")
        self.assertEqual(bh._entry_label({"process": "outra"}), "outra")
        self.assertEqual(bh._entry_label({}), "?")


if __name__ == "__main__":
    unittest.main()
