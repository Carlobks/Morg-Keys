"""Programas .bat de arranque.txt com ícone na área de notificação (bat_tray.py), com o Windows falso.

user32/kernel32/shell32/subprocess são Gravadores (rebentam no que o teste não previu), o relógio é falso,
os registos vão para uma pasta temporária e a porta "responde" quando o teste diz.
"""

import contextlib
import importlib.util
import socket
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from falsos_windows import Gravador, SubprocessFalso
from sistema_falso import PASTA_PACK, RelogioFalso

_especificacao = importlib.util.spec_from_file_location("bat_tray", PASTA_PACK / "bat_tray.py")
bt = importlib.util.module_from_spec(_especificacao)
_especificacao.loader.exec_module(bt)
PORT_OPEN = bt._port_open


class ProcessoFalso:
    def __init__(self, pid=4321, vivo=True):
        self.pid, self.vivo = pid, vivo

    def poll(self):
        return None if self.vivo else 0


class Bandeja:
    """`with Bandeja() as b:` — o bat_tray.py fica a falar só com falsos; `b.porta_aberta` manda na porta."""

    def __init__(self, saida_powershell=""):
        self.saida_powershell = saida_powershell
        self.porta_aberta = False
        self.abertos = []
        self.relogio = RelogioFalso()
        self._pilha = contextlib.ExitStack()

    def __enter__(self):
        self.pasta = Path(self._pilha.enter_context(tempfile.TemporaryDirectory()))
        self.u32 = Gravador("user32", RegisterClassW=1, CreateWindowExW=70, RegisterWindowMessageW=0xC0DE,
                            SetTimer=1, LoadIconW=2, CreatePopupMenu=80, AppendMenuW=1, GetCursorPos=1,
                            SetForegroundWindow=1, TrackPopupMenu=0, PostMessageW=1, DestroyMenu=1,
                            DestroyWindow=1, PostQuitMessage=0, DefWindowProcW=99, GetMessageW=0,
                            TranslateMessage=1, DispatchMessageW=1)
        self.sh32 = Gravador("shell32", ExtractIconW=3, Shell_NotifyIconW=1)
        self.k32 = Gravador("kernel32", GetModuleHandleW=60, CreateMutexW=90, CloseHandle=1)
        self.sp = SubprocessFalso(lambda cmd: self.saida_powershell if cmd[0] == "powershell" else "")
        trocas = {"user32": self.u32, "shell32": self.sh32, "kernel32": self.k32, "subprocess": self.sp,
                  "time": self.relogio, "LOG_DIR": self.pasta / "registos",
                  "_port_open": lambda porta: self.porta_aberta}
        for nome, valor in trocas.items():
            self._pilha.enter_context(mock.patch.object(bt, nome, valor))
        self._pilha.enter_context(mock.patch.object(bt.os, "startfile", self.abertos.append, create=True))
        self._pilha.callback(self._fechar_registos)
        return self

    def _fechar_registos(self):
        for _, kw in self.sp.lancados:
            if hasattr(kw.get("stdout"), "close"):
                kw["stdout"].close()

    def __exit__(self, *erro):
        return self._pilha.__exit__(*erro)

    def bat(self, texto="@echo off\n", nome="servidor.bat"):
        caminho = self.pasta / nome
        caminho.write_text(texto, encoding="utf-8")
        return caminho


class EnderecoEPorta(unittest.TestCase):

    def test_local_port(self):
        self.assertEqual(bt._local_port("http://localhost:3000/x"), 3000)
        self.assertEqual(bt._local_port("https://127.0.0.1"), 443)
        self.assertEqual(bt._local_port("http://localhost"), 80)
        self.assertIsNone(bt._local_port("http://exemplo.pt:3000"))
        self.assertIsNone(bt._local_port("http://[::1"))

    def test_port_open(self):
        with socket.socket() as servidor:
            servidor.bind(("127.0.0.1", 0))
            servidor.listen()
            porta = servidor.getsockname()[1]
            self.assertTrue(PORT_OPEN(porta))
        self.assertFalse(PORT_OPEN(porta))


class Programa(unittest.TestCase):

    def test_nome_do_registo_e_porta(self):
        with Bandeja() as b:
            p = bt.Program(b.bat(), "http://localhost:3000", "Servidor do site!")
            self.assertEqual((p.port, p.log.name), (3000, "Servidor_do_site_.log"))
            self.assertIsNone(bt.Program(b.bat(), "", "x").port)

    def test_a_correr_pela_porta_ou_pelo_processo(self):
        with Bandeja() as b:
            com_porta = bt.Program(b.bat(), "http://localhost:3000", "S")
            self.assertFalse(com_porta.running())
            b.porta_aberta = True
            self.assertTrue(com_porta.running())
            sem_porta = bt.Program(b.bat(), "", "S")
            self.assertFalse(sem_porta.running())
            sem_porta.proc = ProcessoFalso(vivo=True)
            self.assertTrue(sem_porta.running())
            sem_porta.proc = ProcessoFalso(vivo=False)
            self.assertFalse(sem_porta.running())

    def test_start_corre_o_bat_na_pasta_dele_com_a_saida_no_registo(self):
        with Bandeja() as b:
            bat = b.bat()
            p = bt.Program(bat, "", "Servidor")
            p.start()
            cmd, kw = b.sp.lancados[0]
            self.assertEqual(cmd, ["cmd.exe", "/c", str(bat)])
            self.assertEqual((kw["cwd"], kw["creationflags"], kw["stdin"]), (str(b.pasta), 0x08000000, bt.subprocess.DEVNULL))
            kw["stdout"].close()
            self.assertIn(f"{bat} iniciado ---", p.log.read_text(encoding="utf-8"))
            p.start()  # já a correr (o processo falso está vivo): não lança outro
            self.assertEqual(len(b.sp.lancados), 1)

    def test_stop_mata_a_arvore_e_quem_escuta_na_porta(self):
        with Bandeja(saida_powershell="1234\n4\nabc\n1234\n") as b:
            p = bt.Program(b.bat(), "http://localhost:3000", "S")
            p.proc = ProcessoFalso(pid=77)
            b.porta_aberta = True
            inicio = b.relogio.agora
            b.relogio.ao_avancar.append(lambda agora: setattr(b, "porta_aberta", agora - inicio < 1))
            p.stop()
            mortos = [cmd[-1] for cmd, _ in b.sp.corridos if cmd[0] == "taskkill"]
            self.assertEqual(mortos, ["77", "1234", "1234"])
            self.assertIsNone(p.proc)
            self.assertEqual(b.relogio.agora - inicio, 1.0)

    def test_stop_sem_processo_vivo_e_porta_que_nunca_fecha(self):
        with Bandeja() as b:
            p = bt.Program(b.bat(), "http://localhost:3000", "S")
            p.proc = ProcessoFalso(vivo=False)
            b.porta_aberta = True
            inicio = b.relogio.agora
            p.stop()
            self.assertEqual([cmd[0] for cmd, _ in b.sp.corridos], ["powershell"])
            self.assertEqual(b.relogio.agora - inicio, 5.0)
        with Bandeja() as b:
            bt.Program(b.bat(), "", "S").stop()
            self.assertEqual(b.sp.corridos, [])


class Icone(unittest.TestCase):

    def tray(self, b, texto="@echo off\n", url="", node_existe=False):
        programas = b.pasta / "Programas"
        if node_existe:
            (programas / "nodejs").mkdir(parents=True)
            (programas / "nodejs" / "node.exe").write_text("")
        with mock.patch.dict(bt.os.environ, {"ProgramFiles": str(programas), "SystemRoot": r"C:\Windows"}):
            return bt.Tray(bt.Program(b.bat(texto), url, "Servidor"))

    def test_cria_a_janela_o_icone_e_o_temporizador(self):
        with Bandeja() as b:
            t = self.tray(b)
            self.assertEqual((t.hwnd, t.taskbar_created, t.icon, t.running), (70, 0xC0DE, 3, False))
            self.assertEqual(b.u32.de("SetTimer"), [(70, 1, 3000, None)])
            self.assertEqual([c[0] for c in b.sh32.de("Shell_NotifyIconW")], [bt.NIM_ADD, bt.NIM_MODIFY])

    def test_icone_do_node_so_para_npm_com_o_node_instalado(self):
        casos = (("npm run dev", True, r"nodejs\node.exe"), ("npm run dev", False, r"System32\cmd.exe"),
                 ("@echo off", True, r"System32\cmd.exe"))
        for texto, node_existe, fim in casos:
            with self.subTest(texto=texto, node=node_existe), Bandeja() as b:
                self.tray(b, texto, node_existe=node_existe)
                self.assertTrue(b.sh32.de("ExtractIconW")[0][1].endswith(fim))

    def test_bat_ilegivel_e_icone_por_omissao(self):
        with Bandeja() as b:
            b.sh32._respostas["ExtractIconW"] = 0
            p = bt.Program(b.pasta / "nao-existe.bat", "", "X")
            t = bt.Tray(p)
            self.assertEqual(t.icon, 2)
            self.assertEqual(b.u32.de("LoadIconW")[0][1].value, 32512)

    def test_dica_com_o_estado(self):
        with Bandeja() as b:
            t = self.tray(b)
            self.assertEqual(t._nid().szTip, "Servidor — parado")
            t.running = True
            self.assertEqual(t._nid().szTip, "Servidor — a correr")
            t.program.name = "x" * 200
            self.assertEqual(len(t._nid().szTip), 127)

    def test_refresh_so_atualiza_quando_muda(self):
        with Bandeja() as b:
            t = self.tray(b, url="http://localhost:3000")
            antes = len(b.sh32.chamadas)
            t.refresh()
            self.assertEqual(len(b.sh32.chamadas), antes)
            b.porta_aberta = True
            t.refresh()
            self.assertEqual((t.running, len(b.sh32.chamadas)), (True, antes + 1))


class Menu(unittest.TestCase):

    def menu(self, url, a_correr, escolha=0):
        with Bandeja() as b:
            t = Icone().tray(b, url=url)
            t.running = a_correr
            b.u32._respostas["TrackPopupMenu"] = escolha
            comandos = []
            t.command = comandos.append
            t.menu()
            return [(flags, texto) for _, flags, _, texto in b.u32.de("AppendMenuW")], comandos

    def test_itens_conforme_o_estado(self):
        itens, comandos = self.menu("http://localhost:3000", a_correr=True, escolha=bt.ID_LOG)
        self.assertEqual(itens, [(0, "Abrir no navegador"), (0, "Ver registo ao vivo"), (0x800, None),
                                 (0, "Reiniciar"), (0, "Parar"), (0x800, None), (0, "Fechar (para o programa)")])
        self.assertEqual(comandos, [bt.ID_LOG])
        itens, _ = self.menu("http://localhost:3000", a_correr=False)
        self.assertEqual((itens[0], itens[4]), ((0x1, "Abrir no navegador"), (0, "Iniciar")))
        itens, _ = self.menu("", a_correr=False)
        self.assertEqual(itens[0], (0, "Ver registo ao vivo"))

    def comando(self, cmd, a_correr=False):
        with Bandeja() as b:
            t = Icone().tray(b, url="http://localhost:3000")
            t.running = a_correr
            feitos = []
            t.program.stop = lambda: feitos.append("parar")
            t.program.start = lambda: feitos.append("iniciar")
            t.refresh = lambda: feitos.append("refresh")
            with mock.patch.dict(bt.os.environ, {"LOCALAPPDATA": r"C:\L"}):
                t.command(cmd)
            return feitos, b

    def test_comandos(self):
        feitos, b = self.comando(bt.ID_OPEN)
        self.assertEqual((feitos, b.abertos), (["refresh"], ["http://localhost:3000"]))
        feitos, b = self.comando(bt.ID_LOG)
        cmd = b.sp.lancados[0][0]
        self.assertEqual(cmd[:5], [r"C:\L\Microsoft\WindowsApps\wt.exe", "-w", "new", "--title", "Servidor (registo)"])
        self.assertTrue(cmd[-1].endswith("Servidor.log' -Tail 200 -Wait"))
        self.assertEqual(self.comando(bt.ID_RESTART)[0], ["parar", "iniciar", "refresh"])
        self.assertEqual(self.comando(bt.ID_TOGGLE, a_correr=True)[0], ["parar", "refresh"])
        self.assertEqual(self.comando(bt.ID_TOGGLE, a_correr=False)[0], ["iniciar", "refresh"])
        feitos, b = self.comando(bt.ID_QUIT)
        self.assertEqual((feitos, b.u32.de("DestroyWindow")), (["parar"], [(70,)]))
        self.assertEqual(self.comando(0)[0], ["refresh"])  # menu fechado sem escolher

    def test_mensagens_da_janela(self):
        with Bandeja() as b:
            t = Icone().tray(b)
            feitos = []
            t.menu, t.refresh, t._add = (lambda: feitos.append("menu")), (lambda: feitos.append("refresh")), \
                (lambda: feitos.append("add"))
            for lp in (0x0202, 0x0205, 0x0200):
                t._wndproc(70, bt.WM_TRAY, 0, lp)
            self.assertEqual(t._wndproc(70, 0x0113, 0, 0), 0)
            t._wndproc(70, 0xC0DE, 0, 0)
            self.assertEqual(t._wndproc(70, 0x0002, 0, 0), 0)
            self.assertEqual(t._wndproc(70, 0x0005, 1, 2), 99)
            self.assertEqual(feitos, ["menu", "menu", "refresh", "add"])
            self.assertEqual(b.sh32.chamadas[-1][1], bt.NIM_DELETE)
            self.assertEqual(b.u32.de("DefWindowProcW"), [(70, bt.WM_TRAY, 0, 0x0200), (70, 0x0005, 1, 2)])


class PontoDeEntrada(unittest.TestCase):

    def test_sem_bat_ou_bat_inexistente(self):
        with Bandeja() as b:
            self.assertEqual(bt.main(["bat_tray.py"]), 2)
            self.assertEqual(bt.main(["bat_tray.py", str(b.pasta / "nao.bat")]), 2)
            self.assertEqual(b.k32.chamadas, [])

    def test_ja_ha_um_icone_para_este_bat(self):
        with Bandeja() as b, mock.patch.object(bt.ctypes, "get_last_error", return_value=183):
            bat = b.bat()
            self.assertEqual(bt.main(["bat_tray.py", str(bat)]), 0)
            self.assertEqual(b.sp.lancados, [])
            nome = b.k32.de("CreateMutexW")[0][2]
            self.assertTrue(nome.startswith("Local\\MorgBatTray_"))
            self.assertEqual(len(nome), len("Local\\MorgBatTray_") + 12)

    def test_arranca_o_programa_e_corre_o_laco_de_mensagens(self):
        mensagens = iter([1, 1, 0])
        for argv_extra, nome in (([], "servidor"), (["http://localhost:3000", ""], "servidor"),
                                 (["", "Meu servidor"], "Meu servidor")):
            with self.subTest(argv=argv_extra), Bandeja() as b, \
                    mock.patch.object(bt.ctypes, "get_last_error", return_value=0):
                mensagens = iter([1, 1, 0])
                b.u32._respostas["GetMessageW"] = lambda *a, m=mensagens: next(m)
                bat = b.bat()
                self.assertEqual(bt.main(["bat_tray.py", str(bat), *argv_extra]), 0)
                self.assertEqual(b.sp.lancados[0][0], ["cmd.exe", "/c", str(bat.resolve())])
                self.assertEqual(b.u32.nomes().count("DispatchMessageW"), 2)
                self.assertEqual(b.k32.de("CloseHandle"), [(90,)])
                self.assertEqual(b.u32.de("CreateWindowExW")[0][2], nome)


if __name__ == "__main__":
    unittest.main()
