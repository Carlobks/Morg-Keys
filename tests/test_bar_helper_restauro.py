"""Caracterização do arranjo dos workspaces: `_restore` (arranque) e `layout_save` (Alt+Esc, G).

Fase 1 da experiência 0001: fixa o comportamento de 2026-10-23. GlazeWM, relógio e abridor falsos
(sistema_falso): abrir uma app faz aparecer a janela dela no workspace focado, como no PC real.
"""

import json
import unittest

from sistema_falso import SistemaFalso, espaco

LAUNCH_OBSIDIAN = r"shell:AppsFolder\md.obsidian"


def workspaces_com_foco_no_1():
    return [espaco(str(n), foco=(n == 1)) for n in range(1, 11)]


def entrada_do_painel(ws, ficheiro, processo=None, label=None):
    entrada = {"workspace": ws, "title_hash": "", "label": label or ficheiro, "value": ficheiro,
               "launch": {"file": ficheiro}}
    if processo:
        entrada["process"] = processo
    return entrada


class RestaurarEntradasAntigas(unittest.TestCase):
    """Entradas gravadas com Alt+Esc, G (sem "launch"): abrem-se pela tabela LAUNCH."""

    def test_abre_a_app_que_falta_e_poe_a_janela_no_workspace(self):
        with SistemaFalso(workspaces_com_foco_no_1()) as s:
            s.abridor.app(LAUNCH_OBSIDIAN, "Obsidian", "Notas")
            layout = {"windows": [{"workspace": "3", "process": "Obsidian", "title_hash": s.bh._title_hash("Notas")}]}
            lancados = []
            faltam = s.bh._restore(layout, s.log, on_launched=lancados.append)
            self.assertEqual(faltam, [])
            self.assertEqual(lancados, ["Obsidian"])
            self.assertEqual(s.glaze.onde_esta("j1"), "3")
            self.assertIn("abri Obsidian", s.registo)
            self.assertIn("movi Obsidian do 1 para o 3", s.registo)

    def test_nao_abre_se_o_processo_ja_corre(self):
        with SistemaFalso(workspaces_com_foco_no_1(), processos_a_correr={"obsidian"}) as s:
            s.abridor.app(LAUNCH_OBSIDIAN, "Obsidian")
            layout = {"windows": [{"workspace": "3", "process": "Obsidian", "title_hash": "x"}]}
            faltam = s.bh._restore(layout, s.log, wait_s=2)
            self.assertEqual(s.abridor.abertos, [])
            self.assertEqual([e["process"] for e in faltam], ["Obsidian"])

    def test_processo_fora_da_tabela_launch_nao_abre(self):
        with SistemaFalso(workspaces_com_foco_no_1()) as s:
            layout = {"windows": [{"workspace": "3", "process": "desconhecido", "title_hash": "x"}]}
            s.bh._restore(layout, s.log, wait_s=1)
            self.assertEqual(s.abridor.abertos, [])

    def test_janela_ja_aberta_no_sitio_certo_nao_se_move(self):
        with SistemaFalso(workspaces_com_foco_no_1()) as s:
            ident = s.glaze.janela("chrome", "Gmail", "2")
            layout = {"windows": [{"workspace": "2", "process": "chrome", "title_hash": s.bh._title_hash("Gmail")}]}
            colocadas = []
            self.assertEqual(s.bh._restore(layout, s.log, on_placed=colocadas.append), [])
            self.assertEqual((s.glaze.onde_esta(ident), s.glaze.comandos, len(colocadas)), ("2", [], 1))


class RestaurarPorTitulo(unittest.TestCase):

    def test_duas_janelas_da_mesma_app_vao_cada_uma_para_o_seu_workspace(self):
        with SistemaFalso(workspaces_com_foco_no_1()) as s:
            h = s.bh._title_hash
            gmail = s.glaze.janela("chrome", "Gmail", "1")
            docs = s.glaze.janela("chrome", "Docs", "1")
            layout = {"windows": [{"workspace": "4", "process": "chrome", "title_hash": h("Docs")},
                                  {"workspace": "5", "process": "chrome", "title_hash": h("Gmail")}]}
            self.assertEqual(s.bh._restore(layout, s.log), [])
            self.assertEqual((s.glaze.onde_esta(docs), s.glaze.onde_esta(gmail)), ("4", "5"))

    def test_menos_janelas_que_entradas_so_aceita_titulo_diferente_no_ultimo_terco(self):
        with SistemaFalso(workspaces_com_foco_no_1()) as s:
            ident = s.glaze.janela("chrome", "Outro título", "1")  # 1 janela para 2 entradas: espera
            layout = {"windows": [{"workspace": "6", "process": "chrome", "title_hash": "naobate1"},
                                  {"workspace": "7", "process": "chrome", "title_hash": "naobate2"}]}
            inicio = s.relogio.agora
            horas = []
            faltam = s.bh._restore(layout, s.log, on_placed=lambda e: horas.append(s.relogio.agora - inicio),
                                   wait_s=9, poll=0.5)
            self.assertEqual(len(horas), 1)
            self.assertGreater(horas[0], 6)  # só depois de 2/3 de 9 s
            self.assertEqual(s.glaze.onde_esta(ident), "6")
            self.assertEqual([e["workspace"] for e in faltam], ["7"])

    def test_mais_janelas_que_entradas_aceita_logo_qualquer_uma(self):
        with SistemaFalso(workspaces_com_foco_no_1()) as s:
            ident = s.glaze.janela("chrome", "Outro título", "1")
            s.glaze.janela("chrome", "Mais um", "1")
            layout = {"windows": [{"workspace": "6", "process": "chrome", "title_hash": "naobate"}]}
            inicio = s.relogio.agora
            self.assertEqual(s.bh._restore(layout, s.log, wait_s=9), [])
            self.assertEqual((s.relogio.agora, s.glaze.onde_esta(ident)), (inicio, "6"))

    def test_tantas_janelas_como_entradas_aceita_logo(self):
        with SistemaFalso(workspaces_com_foco_no_1()) as s:
            ident = s.glaze.janela("chrome", "Outro título", "1")
            layout = {"windows": [{"workspace": "6", "process": "Chrome", "title_hash": "naobate"}]}
            inicio = s.relogio.agora
            self.assertEqual(s.bh._restore(layout, s.log, wait_s=9), [])
            self.assertEqual(s.relogio.agora, inicio)  # processo comparado sem maiúsculas; sem esperar
            self.assertEqual(s.glaze.onde_esta(ident), "6")

    def test_se_abriu_alguma_app_espera_pelo_menos_40_s(self):
        with SistemaFalso(workspaces_com_foco_no_1()) as s:
            s.abridor.app(LAUNCH_OBSIDIAN, "Obsidian", atraso=1000)  # abre mas a janela nunca chega
            layout = {"windows": [{"workspace": "3", "process": "Obsidian", "title_hash": "x"}]}
            inicio = s.relogio.agora
            faltam = s.bh._restore(layout, s.log, wait_s=1, poll=1)
            self.assertEqual(len(faltam), 1)
            self.assertGreaterEqual(s.relogio.agora - inicio, 40)

    def test_sem_janela_devolve_as_entradas_ao_fim_do_prazo(self):
        with SistemaFalso(workspaces_com_foco_no_1(), processos_a_correr={"chrome"}) as s:
            layout = {"windows": [{"workspace": "6", "process": "chrome", "title_hash": "x"},
                                  {"workspace": "7", "title_hash": "y"}]}
            inicio = s.relogio.agora
            faltam = s.bh._restore(layout, s.log, wait_s=5, poll=1)
            self.assertEqual([e["workspace"] for e in faltam], ["6", "7"])
            self.assertGreaterEqual(s.relogio.agora - inicio, 5)


class RestaurarEntradasDoPainel(unittest.TestCase):
    """Entradas criadas no painel (com "launch")."""

    def test_aprende_o_processo_sem_apanhar_a_janela_de_outra_entrada(self):
        # Regressão: aprendia a janela errada (uma janela do Chrome que abriu entretanto).
        with SistemaFalso(workspaces_com_foco_no_1()) as s:
            s.abridor.app("shell:AppsFolder\\Notas", "Notas", "Notas", atraso=2)
            layout = {"windows": [
                entrada_do_painel("3", "shell:AppsFolder\\Notas", label="Notas"),
                {"workspace": "2", "process": "chrome", "title_hash": s.bh._title_hash("Gmail")},
            ]}
            # O Chrome (de outra entrada) abre sozinho DEPOIS de pedir as Notas e ANTES da janela delas.
            s.abridor.aparece_sozinha("chrome", "Gmail", atraso=1)
            self.assertEqual(s.bh._restore(layout, s.log, wait_s=3), [])
            gravado = json.loads(s.ler("LAYOUT_FILE"))
            self.assertEqual(gravado["windows"][0]["process"], "Notas")
            self.assertNotIn("_placed", gravado["windows"][0])
            self.assertIn("aprendi Notas = Notas; ficou no 3", s.registo)

    def test_sem_janela_nova_em_12_s_desiste(self):
        with SistemaFalso(workspaces_com_foco_no_1()) as s:
            s.abridor.app("shell:AppsFolder\\Lenta", "Lenta", atraso=30)
            layout = {"windows": [entrada_do_painel("3", "shell:AppsFolder\\Lenta", label="Lenta")]}
            faltam = s.bh._restore(layout, s.log, wait_s=1)
            self.assertIn("Lenta: nenhuma janela nova em 12 s", s.registo)
            self.assertEqual(len(faltam), 1)
            self.assertIsNone(s.ler("LAYOUT_FILE"))  # nada aprendido: não grava

    def test_processo_conhecido_conta_as_janelas_que_ja_existem(self):
        with SistemaFalso(workspaces_com_foco_no_1()) as s:
            s.abridor.app("chrome", "chrome", "novo")
            s.glaze.janela("chrome", "já aberta", "1")
            layout = {"windows": [entrada_do_painel("4", "chrome", "chrome", "A"),
                                  entrada_do_painel("5", "chrome", "chrome", "B")]}
            self.assertEqual(s.bh._restore(layout, s.log), [])
            self.assertEqual(len(s.abridor.abertos), 1)  # uma janela já existia: só abre a outra

    def test_janela_existente_conta_primeiro_para_a_entrada_antiga(self):
        with SistemaFalso(workspaces_com_foco_no_1()) as s:
            s.abridor.app("chrome", "chrome", "Gmail")
            s.glaze.janela("chrome", "Docs", "1")
            layout = {"windows": [
                {"workspace": "2", "process": "chrome", "title_hash": s.bh._title_hash("Docs")},  # Alt+Esc, G
                {**entrada_do_painel("4", "chrome", "chrome", "Gmail"),
                 "launch": {"file": "chrome", "args": "--app=https://mail"}},
            ]}
            self.assertEqual(s.bh._restore(layout, s.log), [])
            self.assertEqual(s.abridor.abertos, [("chrome", "--app=https://mail")])

    def test_app_a_arrancar_sozinha_nao_abre_em_duplicado(self):
        with SistemaFalso(workspaces_com_foco_no_1(), processos_a_correr={"notas"}) as s:
            s.abridor.app("Notas.exe", "Notas")
            layout = {"windows": [entrada_do_painel("4", "Notas.exe", "Notas")]}
            s.bh._restore(layout, s.log, wait_s=1)
            self.assertEqual(s.abridor.abertos, [])

    def test_com_argumentos_abre_mesmo_a_correr(self):
        with SistemaFalso(workspaces_com_foco_no_1(), processos_a_correr={"chrome"}) as s:
            s.abridor.app("chrome", "chrome", "Gmail")
            entrada = entrada_do_painel("4", "chrome", "chrome", "Gmail")
            entrada["launch"]["args"] = "--app=https://mail.google.com"
            self.assertEqual(s.bh._restore({"windows": [entrada]}, s.log), [])
            self.assertEqual(s.abridor.abertos, [("chrome", "--app=https://mail.google.com")])


class GravarArranjo(unittest.TestCase):

    def test_glaze_desligado_nao_grava_e_avisa(self):
        with SistemaFalso() as s:
            s.glaze.ligado = False
            s.bh.layout_save()
            self.assertIsNone(s.ler("LAYOUT_FILE"))
            self.assertEqual(s.bipes, [0x10])

    def test_grava_janelas_e_workspace_focado(self):
        with SistemaFalso(workspaces_com_foco_no_1()) as s:
            s.glaze.janela("chrome", "Gmail", "2")
            s.bh.layout_save()
            gravado = json.loads(s.ler("LAYOUT_FILE"))
            self.assertEqual(gravado["focused"], "1")
            self.assertEqual(gravado["windows"], [{"workspace": "2", "process": "chrome",
                                                   "title_hash": s.bh._title_hash("Gmail")}])
            self.assertEqual(s.bipes, [0])

    def test_herda_o_como_abrir_pelo_titulo_uma_entrada_por_janela(self):
        with SistemaFalso(workspaces_com_foco_no_1()) as s:
            h = s.bh._title_hash
            antigo = {"windows": [
                {"workspace": "3", "process": "chrome", "title_hash": h("Docs"), "label": "Docs",
                 "value": "web: https://docs", "launch": {"file": "chrome", "args": "--app=https://docs"}},
                {"workspace": "4", "process": "chrome", "title_hash": h("Gmail"), "label": "Gmail",
                 "value": "web: https://mail", "launch": {"file": "chrome", "args": "--app=https://mail"}},
            ]}
            s.escrever("LAYOUT_FILE", json.dumps(antigo))
            s.glaze.janela("chrome", "Gmail", "7")
            s.glaze.janela("chrome", "Sem título conhecido", "8")
            s.bh.layout_save()
            janelas = json.loads(s.ler("LAYOUT_FILE"))["windows"]
            self.assertEqual([(j["workspace"], j.get("label")) for j in janelas], [("7", "Gmail"), ("8", "Docs")])

    def test_duas_janelas_sem_titulo_conhecido_nao_herdam_a_mesma_entrada(self):
        with SistemaFalso(workspaces_com_foco_no_1()) as s:
            antigo = {"windows": [
                {"workspace": "3", "process": "chrome", "title_hash": "a", "label": "Docs", "launch": {"file": "x"}},
                {"workspace": "4", "process": "chrome", "title_hash": "b", "label": "Gmail", "launch": {"file": "y"}},
            ]}
            s.escrever("LAYOUT_FILE", json.dumps(antigo))
            s.glaze.janela("chrome", "Primeira", "7")
            s.glaze.janela("chrome", "Segunda", "8")
            s.bh.layout_save()
            janelas = json.loads(s.ler("LAYOUT_FILE"))["windows"]
            self.assertEqual([j.get("label") for j in janelas], ["Docs", "Gmail"])


if __name__ == "__main__":
    unittest.main()
