"""Atalhos das apps (morg_atalhos): lista do menu Iniciar (Get-StartApps e cache), apps que não existem
neste PC e o Alt+Shift+R (`apps_apply`), em casos que test_bar_helper_apps_txt.py não fixava.
"""

import json
import sys
import unittest
from unittest import mock

from falsos_windows import Gravador, SubprocessFalso
from sistema_falso import SistemaFalso, carregar_bar_helper, config_minimo

carregar_bar_helper()
ATALHOS = sys.modules["morg_atalhos"]
START_ITEMS = ATALHOS._start_items
MENU_JSON = json.dumps([{"Name": " Google Chrome ", "AppID": "Chrome"}, {"Name": "Sem id"}, {"AppID": "sem.nome"}])


class RegistoFalso:
    """Faz de `winreg`: a chave do Chrome existe ou não."""
    HKEY_LOCAL_MACHINE = 2

    def __init__(self, existe):
        self.existe = existe

    def OpenKey(self, raiz, caminho):
        if not self.existe:
            raise OSError("sem chave")
        return mock.MagicMock()


class MenuIniciar(unittest.TestCase):

    def ler(self, saida, cache=None, use_cache=False, cache_estragada=False):
        with SistemaFalso() as s:
            sp = SubprocessFalso(lambda cmd: saida)
            s.trocar("subprocess", sp)
            if cache_estragada:
                s.escrever("START_CACHE", "{lixo")
            elif cache is not None:
                s.escrever("START_CACHE", json.dumps(cache))
            itens = START_ITEMS(use_cache)
            guardado = s.ler("START_CACHE")
            return itens, len(sp.corridos), guardado, s.relogio.time()

    def test_get_start_apps_limpa_e_guarda_em_cache(self):
        itens, corridas, guardado, agora = self.ler(MENU_JSON)
        self.assertEqual((itens, corridas), ([{"Name": "Google Chrome", "AppID": "Chrome"}], 1))
        self.assertEqual(json.loads(guardado), {"saved_at": int(agora), "items": itens})

    def test_um_so_item_vem_como_objeto(self):
        self.assertEqual(self.ler(json.dumps({"Name": "A", "AppID": "a"}))[0], [{"Name": "A", "AppID": "a"}])

    def test_saida_vazia_ou_estragada(self):
        self.assertEqual(self.ler("")[0], [])
        itens, _, guardado, _ = self.ler("isto não é json")
        self.assertEqual((itens, guardado), ([], None))

    def test_cache_recente_evita_o_powershell(self):
        with SistemaFalso() as s:
            sp = SubprocessFalso(lambda cmd: MENU_JSON)
            s.trocar("subprocess", sp)
            s.escrever("START_CACHE", json.dumps({"saved_at": s.relogio.time() - 3600, "items": [{"Name": "X"}]}))
            self.assertEqual((START_ITEMS(use_cache=True), sp.corridos), ([{"Name": "X"}], []))

    def test_cache_velha_vazia_ou_estragada_pede_de_novo(self):
        for caso in ({"cache": {"saved_at": 0, "items": [{"Name": "X"}]}}, {"cache": {"saved_at": 1e10, "items": []}},
                     {"cache_estragada": True}, {}):
            with self.subTest(**caso):
                itens, corridas, _, _ = self.ler(MENU_JSON, use_cache=True, **caso)
                self.assertEqual((len(itens), corridas), (1, 1))

    def test_cache_que_nao_se_consegue_gravar_nao_rebenta(self):
        with SistemaFalso() as s:
            s.trocar("subprocess", SubprocessFalso(lambda cmd: MENU_JSON))
            s.trocar("START_CACHE", s.pasta / "nao-existe" / ".start-apps.json")
            self.assertEqual(len(START_ITEMS()), 1)

    def test_cache_sem_a_app_pede_a_lista_nova(self):
        with SistemaFalso() as s:
            pedidos = []
            s.trocar("_start_items", lambda use_cache=False: pedidos.append(use_cache) or (
                [] if use_cache else [{"Name": "Nova", "AppID": "nova.id"}]))
            menu = ATALHOS._MenuIniciar(use_cache=True)
            self.assertEqual(menu.comando("Nova"), 'shell-exec explorer "shell:AppsFolder\\nova.id"')
            self.assertEqual((pedidos, menu.use_cache), ([True, False], False))


class AppsNesteComputador(unittest.TestCase):

    def test_exe_que_existe_vira_caminho_com_barras(self):
        with SistemaFalso() as s:
            exe = s.pasta / "App.exe"
            exe.write_text("")
            self.assertEqual(s.bh._resolve_app(str(exe), {}), "shell-exec " + str(exe).replace("\\", "/"))

    def test_special_available(self):
        with SistemaFalso() as s, mock.patch.object(ATALHOS.Path, "home", return_value=s.pasta):
            self.assertFalse(s.bh._special_available("claude-code"))
            (s.pasta / ".local" / "bin").mkdir(parents=True)
            (s.pasta / ".local" / "bin" / "claude.exe").write_text("")
            self.assertTrue(s.bh._special_available(" Claude-Code "))
            self.assertTrue(s.bh._special_available("terminal"))
            for existe in (True, False):
                with mock.patch.dict(sys.modules, {"winreg": RegistoFalso(existe)}):
                    self.assertEqual(s.bh._special_available("web: https://x.pt"), existe)

    def test_skip_missing_comenta_o_site_sem_chrome(self):
        with SistemaFalso() as s, mock.patch.dict(sys.modules, {"winreg": RegistoFalso(False)}):
            s.escrever("APPS_FILE", "Alt+Y = web: https://youtube.com\n")
            s.escrever("GLAZE_CONFIG", config_minimo(s.bh))
            self.assertEqual(s.bh._apps_apply_core(skip_missing=True), [])
            self.assertEqual(s.ler("APPS_FILE"), "# (não encontrada neste PC) Alt+Y = web: https://youtube.com\n")


class AltShiftR(unittest.TestCase):

    def test_com_erros_avisa_e_recarrega_sem_mudar(self):
        with SistemaFalso() as s:
            u32 = Gravador("user32", MessageBoxW=1)
            s.trocar("user32", u32)
            s.escrever("APPS_FILE", "isto não tem igual\n")
            s.escrever("GLAZE_CONFIG", config_minimo(s.bh))
            s.bh.apps_apply()
            texto, titulo = u32.de("MessageBoxW")[0][1:3]
            self.assertIn("NÃO foram alterados", texto)
            self.assertIn("linha 1: falta o '='", texto)
            self.assertEqual(titulo, "Atalhos das apps (apps.txt)")
            self.assertEqual(s.glaze.comandos, [("command", "wm-reload-config")])

    def test_sem_erros_aplica_e_da_um_bipe(self):
        with SistemaFalso() as s:
            s.escrever("APPS_FILE", "Alt+Enter = terminal\n")
            s.escrever("GLAZE_CONFIG", config_minimo(s.bh))
            s.bh.apps_apply()
            self.assertEqual(s.bipes, [0])
            self.assertIn("bindings: ['alt+enter']", s.ler("GLAZE_CONFIG"))

    def test_apps_edit_abre_o_apps_txt(self):
        with SistemaFalso() as s:
            s.abridor.app(str(s.bh.APPS_FILE), None)
            s.bh.apps_edit()
            self.assertEqual(s.abridor.abertos, [(str(s.bh.APPS_FILE), None)])


if __name__ == "__main__":
    unittest.main()
