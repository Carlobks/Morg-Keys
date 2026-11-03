"""Caracterização do arranque do PC (`boot`) e do arranque.txt, antes de partir o `boot` em passos (fase 2b).

O `boot` só corre de verdade pela tarefa agendada (A2): aqui corre com o sistema falso — cortina, Zebar,
GlazeWM, janelas e portas falsas — e fixa-se a sequência de etapas que o ecrã de arranque mostra.
"""

import json
import tempfile
import unittest
from pathlib import Path
from typing import ClassVar

from sistema_falso import Bomba, SistemaFalso, espaco

TITULO_SISTEMA = "Zebar - omarchy-catppuccin / sistema"


class CortinaFalsa:
    criadas: ClassVar[list] = []
    eventos: ClassVar[list] = []  # partilhado com o ArranqueFalso: mostra a ordem das coisas

    def __init__(self, animacao="cafe"):
        self.animacao, self.fechada = animacao, False
        CortinaFalsa.criadas.append(self)

    def close(self):
        if not self.fechada:
            CortinaFalsa.eventos.append("cortina fechada")
        self.fechada = True


class ArranqueFalso(SistemaFalso):
    """SistemaFalso com o que o `boot` precisa: kernel32/user32 permissivos, Zebar e portas falsos."""

    def __init__(self, splash_avisa=True, splash_fecha_sozinho=True, zebar_existe=True, porta_abre_aos=2.0):
        super().__init__([espaco(str(n), foco=(n == 1)) for n in range(1, 11)])
        self.splash_avisa, self.splash_fecha_sozinho = splash_avisa, splash_fecha_sozinho
        self.zebar_existe, self.porta_abre_aos = zebar_existe, porta_abre_aos
        self.lancados, self.mensagens, self.medicoes, self.chamadas_k32 = [], [], [], []

    def __enter__(self):
        super().__enter__()
        bh = self.bh
        self.inicio = self.relogio.agora
        self.zebar = self.pasta / "zebar.exe"
        if self.zebar_existe:
            self.zebar.write_text("")
        self.arranque_txt = self.pasta / "arranque.txt"
        self.bat = self.pasta / "servidor.bat"
        self.bat.write_text("@echo off\n")
        self.arranque_txt.write_text(f"animacao = cafe\nbat = {self.bat} | http://localhost:3000 | Servidor\n"
                                     "bat = C:\\nao\\existe.bat\n", encoding="utf-8")
        self.janelas = {bh.BAR_TITLE: 11, TITULO_SISTEMA: 12, "Shell_TrayWnd": 13, bh.SPLASH_TITLE: 14}
        k32 = {
            "SetPriorityClass": lambda *a: self.chamadas_k32.append("SetPriorityClass") or 1,
            "GetCurrentProcess": lambda: 99,
            "CreateMutexW": lambda *a: self.chamadas_k32.append("CreateMutexW") or 101,
            "CreateEventW": lambda *a: 102,
            "WaitForSingleObject": lambda h, ms: 0 if self.splash_avisa else 0x102,  # WAIT_TIMEOUT
            "ReleaseMutex": lambda h: self.chamadas_k32.append("ReleaseMutex") or 1,
            "CloseHandle": lambda h: 1,
        }
        u32 = {
            "FindWindowW": self._encontrar_janela,
            "SetWindowPos": lambda *a: 1,
            "PostMessageW": lambda hwnd, msg, wp, lp: self.mensagens.append((hwnd, msg)) or 1,
            "MessageBeep": self.bipes.append,
        }
        self.trocar("kernel32", Bomba("kernel32", k32))
        self.trocar("user32", Bomba("user32", u32))
        self.trocar("_BlackCover", CortinaFalsa)
        self.trocar("ZEBAR", self.zebar)
        self.trocar("ARRANQUE_FILE", self.arranque_txt)
        self.trocar("PROGRESS_FILE", self.pasta / "progress.json")
        self.trocar("_popen_detached", self._lancar)
        self.trocar("_port_open", lambda porta: self.relogio.agora - self.inicio >= self.porta_abre_aos)
        self.trocar("_boot_timing_log", lambda log, t_boot, t_cover: self.medicoes.append((t_boot, t_cover)))
        self.abridor.app(str(bh.GLAZEWM_EXE), None)
        CortinaFalsa.criadas.clear()
        self.eventos = CortinaFalsa.eventos = []
        return self

    def _lancar(self, cmd, **kw):
        self.lancados.append([str(c) for c in cmd])
        self.eventos.append("lançou " + " ".join(str(c) for c in cmd[1:3]))

    def _encontrar_janela(self, classe, titulo):
        chave = titulo if titulo is not None else classe
        if chave == self.bh.SPLASH_TITLE and self.splash_fecha_sozinho and self.relogio.agora - self.inicio > 1:
            return 0
        return self.janelas.get(chave, 0)

    def progresso(self):
        return json.loads((self.pasta / "progress.json").read_text(encoding="utf-8"))

    def registo_do_arranque(self):
        return self.ler("RESTORE_LOG") or ""


class Arranque(unittest.TestCase):

    def test_sequencia_normal(self):
        with ArranqueFalso() as s:
            s.abridor.app(r"shell:AppsFolder\md.obsidian", "Obsidian", "Notas")
            s.escrever("LAYOUT_FILE", json.dumps({"focused": "1", "windows": [
                {"workspace": "3", "process": "Obsidian", "title_hash": s.bh._title_hash("Notas")}]}))
            s.bh.boot()
            progresso = s.progresso()
            self.assertEqual([(p["id"], p["label"], p["state"]) for p in progresso["steps"]], [
                ("barra", "Barra", "feito"),
                ("glazewm", "Gestor de janelas", "feito"),
                ("bat:0", "Servidor", "feito"),
                ("bat:1", "existe", "falhou"),
                ("app:Obsidian", "Obsidian", "feito"),
                ("fim", "A finalizar", "feito"),
            ])
            self.assertTrue(progresso["fim"])
            self.assertEqual(progresso["animacao"], "cafe")
            zebar = str(s.zebar)
            self.assertEqual(s.lancados[0], [zebar, "start-widget-preset", "--pack", "omarchy-catppuccin",
                                             "--widget-name", "splash", "--preset", "default"])
            self.assertEqual(s.lancados[1], [zebar, "startup"])
            self.assertEqual(s.lancados[2], [str(s.bh.PYTHONW), "-I", str(s.bh.BAT_TRAY), str(s.bat),
                                             "http://localhost:3000", "Servidor"])
            self.assertEqual(len(s.lancados), 3)
            self.assertIn((str(s.bh.GLAZEWM_EXE), None), s.abridor.abertos)
            cortina = CortinaFalsa.criadas[0]
            self.assertEqual((cortina.animacao, cortina.fechada), ("cafe", True))
            self.assertEqual(s.chamadas_k32, ["SetPriorityClass", "CreateMutexW", "ReleaseMutex"])
            self.assertEqual(len(s.medicoes), 1)
            self.assertEqual(s.mensagens, [])  # o splash fechou-se sozinho
            # A cortina sai quando a animação avisa (logo a seguir ao splash), antes da barra.
            self.assertEqual(s.eventos[:3], ["lançou start-widget-preset --pack", "cortina fechada", "lançou startup"])
            registo = s.registo_do_arranque()
            for frase in ["cortina preta:", "animação visível:", "GlazeWM e barra:", "não existe: C:\\nao\\existe.bat",
                          "Servidor a responder na porta 3000:", "janelas arrumadas:", "tudo assente, ecrã a sair:",
                          "fim:"]:
                self.assertIn(frase, registo)

    def test_usa_a_cortina_aberta_cedo_pelo_bar_helper(self):
        # O bar_helper.py abre a cortina antes de importar o resto (abrir_cedo): o boot usa essa, não abre outra.
        with ArranqueFalso() as s:
            cedo = CortinaFalsa("cafe")
            s.trocar("CORTINA_CEDO", cedo)
            s.trocar("INICIO_CEDO", 1000.0)
            s.bh.boot()
            self.assertEqual(CortinaFalsa.criadas, [cedo])
            self.assertTrue(cedo.fechada)
            self.assertEqual(s.medicoes[0][0], 1000.0)  # a medição conta desde o início do abrir_cedo

    def test_abrir_cedo_poe_prioridade_normal_e_abre_a_cortina(self):
        with ArranqueFalso() as s:
            s.trocar("CORTINA_CEDO", None)  # o abrir_cedo muda-a; o `with` repõe-na no fim
            s.trocar("INICIO_CEDO", None)
            s.bh.abrir_cedo("cafe")
            self.assertEqual(s.chamadas_k32, ["SetPriorityClass"])
            self.assertEqual(CortinaFalsa.criadas, [s.bh.CORTINA_CEDO])
            self.assertIsNotNone(s.bh.INICIO_CEDO)

    def test_splash_que_nao_avisa_e_nao_fecha(self):
        with ArranqueFalso(splash_avisa=False, splash_fecha_sozinho=False) as s:
            s.bh.boot()
            self.assertIn("a animação não avisou em 20 s; continua com a cortina preta", s.registo_do_arranque())
            self.assertIn("splash fechado à força", s.registo_do_arranque())
            self.assertEqual(s.mensagens, [(14, 0x0010)])  # WM_CLOSE ao splash
            self.assertTrue(CortinaFalsa.criadas[0].fechada)

    def test_sem_zebar_nao_lanca_o_ecra_nem_a_barra(self):
        with ArranqueFalso(zebar_existe=False) as s:
            s.bh.boot()
            self.assertTrue(all(cmd[0] != str(s.zebar) for cmd in s.lancados))
            ids = [p["id"] for p in s.progresso()["steps"]]
            self.assertEqual(ids[:2], ["glazewm", "barra"])  # a barra só aparece como etapa no fim (falhou/feito)

    def test_porta_que_nunca_responde_falha_no_limite(self):
        with ArranqueFalso(porta_abre_aos=10_000) as s:
            s.bh.boot()
            estados = {p["id"]: p["state"] for p in s.progresso()["steps"]}
            self.assertEqual(estados["bat:0"], "falhou")
            self.assertGreaterEqual(s.relogio.agora - s.inicio, s.bh.BOOT_CAP_S)


class ConfiguracaoDoArranque(unittest.TestCase):

    def ler(self, texto):
        with SistemaFalso() as s, tempfile.TemporaryDirectory() as pasta:
            ficheiro = Path(pasta) / "arranque.txt"
            if texto is not None:
                ficheiro.write_text(texto, encoding="utf-8")
            s.trocar("ARRANQUE_FILE", ficheiro)
            return s.bh._arranque_cfg()

    def test_le_animacao_e_bats(self):
        cfg = self.ler("# comentário\nAnimação = Café\nbat = \"C:\\a b\\x.bat\" | http://localhost:8080 | X\n"
                       "bat = C:\\y.bat\nbat =\noutra = coisa\n")
        self.assertEqual(cfg, {"animacao": "cafe", "bats": [
            {"path": "C:\\a b\\x.bat", "url": "http://localhost:8080", "name": "X"},
            {"path": "C:\\y.bat", "url": "", "name": "y"}]})

    def test_animacao_com_acento_no_nome(self):
        with SistemaFalso() as s, tempfile.TemporaryDirectory() as pasta:
            ficheiro = Path(pasta) / "arranque.txt"
            ficheiro.write_text("animacao = Pé\n", encoding="utf-8")
            s.trocar("ARRANQUE_FILE", ficheiro)
            s.trocar("ANIMACOES", {"cafe": ("Café", "cafe.bmp", 1, 1), "pe": ("Pé", "pe.bmp", 1, 1)})
            self.assertEqual(s.bh._arranque_cfg()["animacao"], "pe")

    def test_animacao_desconhecida_ou_ficheiro_em_falta(self):
        self.assertEqual(self.ler("animacao = nenhuma\n")["animacao"], "cafe")
        self.assertEqual(self.ler(None), {"animacao": "cafe", "bats": []})

    def test_set_animacao_troca_so_essa_linha(self):
        with SistemaFalso() as s, tempfile.TemporaryDirectory() as pasta:
            ficheiro = Path(pasta) / "arranque.txt"
            ficheiro.write_text("# x\nanimação = cafe\nbat = C:\\y.bat\n", encoding="utf-8")
            s.trocar("ARRANQUE_FILE", ficheiro)
            s.bh._set_animacao("cafe")
            self.assertEqual(ficheiro.read_text(encoding="utf-8"), "# x\nanimacao = cafe\nbat = C:\\y.bat\n")
            ficheiro.write_text("bat = C:\\y.bat\n", encoding="utf-8")
            s.bh._set_animacao("cafe")
            self.assertEqual(ficheiro.read_text(encoding="utf-8"), "bat = C:\\y.bat\nanimacao = cafe\n")

    def test_url_port(self):
        bh = SistemaFalso().bh
        self.assertEqual(bh._url_port("http://localhost:3000/x"), 3000)
        self.assertEqual(bh._url_port("https://127.0.0.1"), 443)
        self.assertEqual(bh._url_port("http://localhost"), 80)
        self.assertIsNone(bh._url_port("https://exemplo.pt:3000"))
        self.assertIsNone(bh._url_port(""))


if __name__ == "__main__":
    unittest.main()
