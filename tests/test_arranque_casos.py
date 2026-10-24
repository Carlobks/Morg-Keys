"""Arranque do PC (morg_arranque): medição do arranque, portas e casos do `boot` que test_arranque.py não fixava."""

import json
import socket
import sys
import time
import unittest

from falsos_windows import Gravador
from sistema_falso import SistemaFalso, carregar_bar_helper
from test_arranque import ArranqueFalso

carregar_bar_helper()
ARRANQUE = sys.modules["morg_arranque"]
PORT_OPEN, TIMING_LOG = ARRANQUE._port_open, ARRANQUE._boot_timing_log

# 2026-01-01 00:00:00 UTC em FILETIME (100 ns desde 1601).
EPOCA_2026 = 1767225600
FT_2026 = (EPOCA_2026 + 11644473600) * 10_000_000


def k32_com_tempos(ok=1, handle=50):
    def tempos(h, criado, *resto):
        criado._obj.dwHighDateTime, criado._obj.dwLowDateTime = FT_2026 >> 32, FT_2026 & 0xFFFFFFFF
        return ok
    return Gravador("kernel32", GetCurrentProcess=60, OpenProcess=handle, GetProcessTimes=tempos, CloseHandle=1)


class MedicaoDoArranque(unittest.TestCase):

    def test_process_created_deste_e_de_outro_processo(self):
        with SistemaFalso() as s:
            k32 = k32_com_tempos()
            s.trocar("kernel32", k32)
            self.assertEqual(s.bh._process_created(), EPOCA_2026)
            self.assertNotIn("CloseHandle", k32.nomes())
            self.assertEqual(s.bh._process_created(1234), EPOCA_2026)
            self.assertEqual(k32.de("OpenProcess"), [(0x1000, False, 1234)])
            self.assertEqual(k32.de("CloseHandle"), [(50,)])

    def test_process_created_sem_acesso_ou_sem_tempos(self):
        with SistemaFalso() as s:
            s.trocar("kernel32", k32_com_tempos(handle=0))
            self.assertIsNone(s.bh._process_created(1234))
            s.trocar("kernel32", k32_com_tempos(ok=0))
            self.assertIsNone(s.bh._process_created(1234))

    def test_hms(self):
        bh = carregar_bar_helper()
        self.assertEqual(bh._hms(None), "?")
        t = 1767225600.25
        self.assertEqual(bh._hms(t), time.strftime("%H:%M:%S", time.localtime(t)) + ".250")

    def medir(self, bandeja, criado=1):
        with SistemaFalso() as s:
            k32 = k32_com_tempos(ok=criado)
            s.trocar("kernel32", k32)
            s.trocar("user32", Gravador("user32", FindWindowW=bandeja,
                                        GetWindowThreadProcessId=lambda h, ref: setattr(ref._obj, "value", 77) or 9))
            registo = []
            TIMING_LOG(registo.append, EPOCA_2026 + 5, EPOCA_2026 + 7.5)
            return registo

    def test_boot_timing_log_com_e_sem_a_barra_de_tarefas(self):
        registo = self.medir(bandeja=13)
        self.assertEqual(len(registo), 2)
        self.assertIn("fundo à vista sem cortina ≈ 7.5 s (arranque do pythonw 5.0 s)", registo[1])
        self.assertEqual(len(self.medir(bandeja=0)), 1)
        self.assertEqual(len(self.medir(bandeja=13, criado=0)), 1)  # sem hora do explorador: só a 1.ª linha

    def test_boot_timing_log_sem_hora_de_criacao(self):
        with SistemaFalso() as s:
            s.trocar("_process_created", lambda pid=None: None if pid is None else EPOCA_2026)
            s.trocar("user32", Gravador("user32", FindWindowW=13, GetWindowThreadProcessId=9))
            registo = []
            TIMING_LOG(registo.append, EPOCA_2026 + 5, EPOCA_2026 + 7.5)
            self.assertIn("pythonw criado ?", registo[0])
            self.assertIn("(arranque do pythonw nan s)", registo[1])


class Portas(unittest.TestCase):

    def test_url_port_invalido(self):
        self.assertIsNone(carregar_bar_helper()._url_port("http://[::1"))

    def test_port_open_com_e_sem_quem_escute(self):
        with socket.socket() as servidor:
            servidor.bind(("127.0.0.1", 0))
            servidor.listen()
            porta = servidor.getsockname()[1]
            self.assertTrue(PORT_OPEN(porta))
        self.assertFalse(PORT_OPEN(porta))


class CasosDoBoot(unittest.TestCase):

    def test_refocar_numa_janela_real_no_fim(self):
        with SistemaFalso() as s:
            comandos = []
            s.trocar("_glaze", lambda *a: comandos.append(a) or {"data": {"focused": {"type": "window", "id": "j3"}}})
            s.bh._refocus_after_boot(None)
            self.assertEqual(comandos[-1], ("command", "focus", "--container-id", "j3"))

    def test_medicao_que_rebenta_nao_estraga_o_arranque(self):
        def rebenta(*a):
            raise RuntimeError("sem relógio")
        with ArranqueFalso() as s:
            s.trocar("_boot_timing_log", rebenta)
            s.bh.boot()
            self.assertIn("medição falhou: RuntimeError('sem relógio')", s.registo_do_arranque())
            self.assertTrue(s.progresso()["fim"])

    def test_glazewm_que_nao_abre(self):
        with ArranqueFalso() as s:
            del s.abridor.janelas_por_ficheiro[str(s.bh.GLAZEWM_EXE)]
            s.glaze.ligado = False
            s.bh.boot()
            self.assertIn("não consegui abrir o GlazeWM: falso: não sei abrir", s.registo_do_arranque())
            estados = {p["id"]: p["state"] for p in s.progresso()["steps"]}
            self.assertEqual(estados["glazewm"], "falhou")

    def test_bat_sem_endereco_fica_feito_logo(self):
        with ArranqueFalso() as s:
            s.arranque_txt.write_text(f"bat = {s.bat}\n", encoding="utf-8")
            s.bh.boot()
            self.assertEqual([(p["id"], p["state"]) for p in s.progresso()["steps"] if p["id"].startswith("bat")],
                             [("bat:0", "feito")])

    def test_app_com_uma_janela_colocada_e_outra_em_falta(self):
        with ArranqueFalso() as s:
            s.abridor.app("notas.exe", "notas", "Notas")
            entrada = {"title_hash": "", "label": "Notas", "value": "notas.exe", "launch": {"file": "notas.exe"},
                       "process": "notas"}
            s.escrever("LAYOUT_FILE", json.dumps({"windows": [{**entrada, "workspace": "2"},
                                                              {**entrada, "workspace": "3"}]}))
            s.abridor.janelas_por_ficheiro["notas.exe"] = ("notas", "Notas", 0)
            abertos = []
            original = s.abridor.shell_open

            def abre_so_uma(launch, log=None):
                abertos.append(launch)
                return original(launch, log) if len(abertos) == 1 else False
            s.trocar("_shell_open", abre_so_uma)
            s.bh.boot()
            self.assertEqual({p["id"]: p["state"] for p in s.progresso()["steps"]}["app:notas"], "falhou")
            self.assertIn("não encontrei janela para Notas (ws 3)", s.registo_do_arranque())

    def test_espera_enquanto_as_janelas_mudam(self):
        with ArranqueFalso() as s:
            s.arranque_txt.write_text("animacao = cafe\n", encoding="utf-8")
            s.abridor.aparece_sozinha("chrome", "A carregar", atraso=2)
            s.bh.boot()
            registo = s.registo_do_arranque()
            assente = next(linha for linha in registo.splitlines() if "tudo assente" in linha)
            self.assertGreaterEqual(float(assente.rsplit(": ", 1)[1].rstrip(" s")), 5)


if __name__ == "__main__":
    unittest.main()
