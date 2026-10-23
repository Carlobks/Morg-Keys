"""Caracterização do `_apps_apply_core` (apps.txt -> bloco de atalhos no config.yaml + recarregar).

Fase 1 da experiência 0001: fixa o comportamento de 2026-10-23. Ficheiros e GlazeWM falsos (sistema_falso).
"""

import unittest

from sistema_falso import SistemaFalso, config_minimo

MENU = [{"Name": "Google Chrome", "AppID": "Chrome"}, {"Name": "Obsidian", "AppID": "md.obsidian"}]


class AplicarAppsTxt(unittest.TestCase):

    def preparar(self, s, apps_txt, config=None):
        s.escrever("APPS_FILE", apps_txt)
        s.escrever("GLAZE_CONFIG", config if config is not None else config_minimo(s.bh))

    def test_escreve_o_bloco_e_recarrega(self):
        with SistemaFalso(apps_do_menu=MENU) as s:
            self.preparar(s, "# as minhas apps\nAlt+Shift+B = Google Chrome\nAlt+O = Obsidian\n")
            self.assertEqual(s.bh._apps_apply_core(), [])
            config = s.ler("GLAZE_CONFIG")
            self.assertIn("  # Google Chrome\n  - commands: ['shell-exec explorer \"shell:AppsFolder\\Chrome\"']\n"
                          "    bindings: ['alt+shift+b']\n", config)
            self.assertIn("    bindings: ['alt+o']\n", config)
            self.assertTrue(config.endswith("  - commands: ['wm-exit']\n    bindings: ['alt+shift+e']\n"))
            self.assertEqual(s.glaze.comandos, [("command", "wm-reload-config")])

    def test_volta_a_aplicar_sem_duplicar_o_bloco(self):
        with SistemaFalso(apps_do_menu=MENU) as s:
            self.preparar(s, "Alt+O = Obsidian\n")
            s.bh._apps_apply_core()
            primeira = s.ler("GLAZE_CONFIG")
            s.bh._apps_apply_core()
            self.assertEqual(s.ler("GLAZE_CONFIG"), primeira)
            self.assertEqual(primeira.count(s.bh.APPS_BEGIN), 1)

    def test_sem_marcadores_insere_logo_depois_de_keybindings(self):
        with SistemaFalso(apps_do_menu=MENU) as s:
            self.preparar(s, "Alt+O = Obsidian\n", "general: {}\n\nkeybindings:\n  - commands: ['a']\n    bindings: ['alt+a']\n")
            self.assertEqual(s.bh._apps_apply_core(), [])
            self.assertTrue(s.ler("GLAZE_CONFIG").startswith(f"general: {{}}\n\nkeybindings:\n{s.bh.APPS_BEGIN}\n"))

    def test_erros_nao_mudam_nada(self):
        with SistemaFalso(apps_do_menu=MENU) as s:
            self.preparar(s, "Alt+Shift+B = Google Chrome\nsem igual\nCtrl+X = Obsidian\nAlt+H = Obsidian\n"
                             "Alt+Shift+B = Obsidian\nAlt+P = Photoshop\n")
            antes = s.ler("GLAZE_CONFIG")
            erros = s.bh._apps_apply_core()
            self.assertEqual(erros, [
                "linha 2: falta o '=' (sem igual)",
                "linha 3: tecla inválida 'Ctrl+X' (use Alt+Shift+letra, sem Ctrl)",
                "linha 4: Alt+H já é usado por outro atalho do sistema",
                "linha 5: Alt+Shift+B repetido (linha 1)",
                "linha 6: não encontrei a app 'Photoshop' no menu Iniciar",
            ])
            self.assertEqual(s.ler("GLAZE_CONFIG"), antes)
            self.assertEqual(s.glaze.comandos, [])

    def test_skip_missing_comenta_as_apps_que_faltam(self):
        with SistemaFalso(apps_do_menu=MENU) as s:
            self.preparar(s, "Alt+O = Obsidian\nAlt+P = Photoshop\n")
            self.assertEqual(s.bh._apps_apply_core(skip_missing=True), [])
            self.assertEqual(s.ler("APPS_FILE"), "Alt+O = Obsidian\n# (não encontrada neste PC) Alt+P = Photoshop\n")
            self.assertIn("bindings: ['alt+o']", s.ler("GLAZE_CONFIG"))
            self.assertNotIn("alt+p", s.ler("GLAZE_CONFIG"))

    def test_palavras_especiais_nao_consultam_o_menu(self):
        with SistemaFalso(apps_do_menu=[]) as s:
            self.preparar(s, "Alt+Enter = Terminal\nAlt+E = Explorador\n")
            self.assertEqual(s.bh._apps_apply_core(), [])
            self.assertIn("shell-exec explorer']", s.ler("GLAZE_CONFIG"))

    def test_aspas_simples_ficam_dobradas_no_yaml(self):
        with SistemaFalso(apps_do_menu=[{"Name": "App d'Ouro", "AppID": "Ouro.d'Ouro"}]) as s:
            self.preparar(s, "Alt+U = App d'Ouro\n")
            self.assertEqual(s.bh._apps_apply_core(), [])
            self.assertIn("  # App d'Ouro\n  - commands: ['shell-exec explorer \"shell:AppsFolder\\Ouro.d''Ouro\"']\n",
                          s.ler("GLAZE_CONFIG"))

    def test_ficheiro_em_falta(self):
        with SistemaFalso() as s:
            erros = s.bh._apps_apply_core()
            self.assertEqual(len(erros), 1)
            self.assertTrue(erros[0].startswith("Não consegui ler os ficheiros:"))


if __name__ == "__main__":
    unittest.main()
