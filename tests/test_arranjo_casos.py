"""Arranjo dos workspaces (morg_arranjo): casos que test_bar_helper_restauro.py não fixava.

`layout-restore` (reinício manual do GlazeWM), apps que não abrem, o registo e a lista de processos.
"""

import json
import sys
import unittest

from falsos_windows import Gravador, SubprocessFalso
from sistema_falso import SistemaFalso, carregar_bar_helper, espaco
from test_bar_helper_restauro import entrada_do_painel, workspaces_com_foco_no_1

carregar_bar_helper()
RUNNING_IMAGES = sys.modules["morg_arranjo"]._running_images


class CasosDoRestauro(unittest.TestCase):

    def test_running_images_le_o_csv_do_tasklist(self):
        saida = '"Obsidian.exe","123","Console"\r\n"System","4"\r\nINFO: sem tarefas\r\n"pythonw.EXE","9"\r\n'
        with SistemaFalso() as s:
            sp = SubprocessFalso(lambda cmd: saida)
            s.trocar("subprocess", sp)
            self.assertEqual(RUNNING_IMAGES(), {"obsidian", "system", "pythonw"})
            self.assertEqual(sp.corridos[0][0], ["tasklist", "/FO", "CSV", "/NH"])

    def test_formato_antigo_com_titulo_em_claro(self):
        with SistemaFalso() as s:
            s.escrever("LAYOUT_FILE", json.dumps({"windows": [{"workspace": "2", "process": "x", "title": "Notas"},
                                                              {"workspace": "3", "process": "y"}]}))
            janelas = s.bh._load_layout()["windows"]
            self.assertEqual([j["title_hash"] for j in janelas], [s.bh._title_hash("Notas"), s.bh._title_hash("")])

    def test_app_do_painel_que_nao_abre_fica_por_colocar(self):
        with SistemaFalso(workspaces_com_foco_no_1()) as s:
            layout = {"windows": [entrada_do_painel("3", "shell:AppsFolder\\Nada", label="Nada"),
                                  entrada_do_painel("4", "nada.exe", "nada")]}
            lancados = []
            faltam = s.bh._restore(layout, s.log, on_launched=lancados.append, wait_s=1)
            self.assertEqual([e["label"] for e in faltam], ["nada.exe", "Nada"])
            self.assertEqual(lancados, [])
            self.assertIn("não consegui abrir shell:AppsFolder\\Nada (falso)", s.registo)

    def test_aprende_no_workspace_certo_sem_mover_e_avisa(self):
        with SistemaFalso(workspaces_com_foco_no_1()) as s:
            s.abridor.app("shell:AppsFolder\\Notas", "Notas", "Notas", atraso=1)
            layout = {"windows": [entrada_do_painel("1", "shell:AppsFolder\\Notas", label="Notas")]}
            colocadas = []
            self.assertEqual(s.bh._restore(layout, s.log, on_placed=colocadas.append), [])
            self.assertEqual(s.glaze.comandos, [])
            self.assertEqual([e["process"] for e in colocadas], ["Notas"])

    def test_app_antiga_que_nao_abre_fica_no_registo(self):
        with SistemaFalso(workspaces_com_foco_no_1()) as s:
            layout = {"windows": [{"workspace": "3", "process": "chrome", "title_hash": "x"}]}
            self.assertEqual(len(s.bh._restore(layout, s.log, wait_s=1)), 1)
            self.assertIn("não consegui abrir chrome: falso: não sei abrir chrome", s.registo)

    def test_app_do_painel_aberta_avisa_on_launched(self):
        with SistemaFalso(workspaces_com_foco_no_1()) as s:
            s.abridor.app("notas.exe", "notas", "Notas")
            lancados = []
            layout = {"windows": [entrada_do_painel("1", "notas.exe", "notas")]}
            self.assertEqual(s.bh._restore(layout, s.log, on_launched=lancados.append), [])
            self.assertEqual(lancados, ["notas"])

    def test_registo_que_nao_se_consegue_escrever_nao_rebenta(self):
        with SistemaFalso() as s:
            s.trocar("RESTORE_LOG", s.pasta)  # é uma pasta: escrever dá erro
            log = s.bh._new_log()
            log("olá")
            log("de novo")

    def test_layout_save_ignora_entradas_antigas_sem_como_abrir(self):
        with SistemaFalso(workspaces_com_foco_no_1()) as s:
            s.escrever("LAYOUT_FILE", json.dumps({"windows": [
                {"workspace": "3", "process": "chrome", "title_hash": "a"},
                {"workspace": "4", "title_hash": "b", "launch": {"file": "y"}}]}))
            s.glaze.janela("chrome", "Gmail", "2")
            s.bh.layout_save()
            self.assertEqual(json.loads(s.ler("LAYOUT_FILE"))["windows"],
                             [{"workspace": "2", "process": "chrome", "title_hash": s.bh._title_hash("Gmail")}])


class ReporNoReinicioDoGlaze(unittest.TestCase):
    """layout_restore: o startup_command do GlazeWM (sem o boot)."""

    def repor(self, layout, arranque_a_correr=False, glaze_ligado=True, workspaces=None):
        with SistemaFalso(workspaces or workspaces_com_foco_no_1()) as s:
            k32 = Gravador("kernel32", OpenMutexW=3 if arranque_a_correr else 0, CloseHandle=1)
            s.trocar("kernel32", k32)
            s.glaze.ligado = glaze_ligado
            if layout is not None:
                s.escrever("LAYOUT_FILE", json.dumps(layout))
            inicio = s.relogio.agora
            s.bh.layout_restore()
            return s, (s.ler("RESTORE_LOG") or ""), s.relogio.agora - inicio

    def test_cede_ao_boot_ou_sem_layout_nao_faz_nada(self):
        _, registo, _ = self.repor({"windows": []}, arranque_a_correr=True)
        self.assertEqual(registo, "")
        _, registo, _ = self.repor(None)
        self.assertEqual(registo, "")

    def test_glaze_que_nao_responde_em_30_s(self):
        _, registo, duracao = self.repor({"windows": []}, glaze_ligado=False)
        self.assertTrue(registo.endswith("GlazeWM não respondeu; nada feito"))
        self.assertEqual(duracao, 30)

    def test_repoe_regista_o_que_falta_e_foca_o_workspace_gravado(self):
        layout = {"focused": "3", "windows": [{"workspace": "2", "process": "fantasma", "title_hash": "x"}]}
        s, registo, _ = self.repor(layout)
        self.assertIn("não encontrei janela para fantasma (ws 2)", registo)
        self.assertTrue(registo.endswith("fim"))
        self.assertEqual(s.glaze.comandos, [("command", "focus", "--workspace", "3")])

    def test_ja_no_workspace_gravado_ou_sem_gravado_nao_muda(self):
        for layout in ({"focused": "1", "windows": []}, {"windows": []}):
            with self.subTest(layout=layout):
                s, _, _ = self.repor(layout)
                self.assertEqual(s.glaze.comandos, [])
        s, _, _ = self.repor({"focused": "1", "windows": []}, workspaces=[espaco("1"), espaco("2")])
        self.assertEqual(s.glaze.comandos, [("command", "focus", "--workspace", "1")])


if __name__ == "__main__":
    unittest.main()
