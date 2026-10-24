"""Ligação ao Windows (morg_win32), lançar processos (morg_processos) e a CLI do GlazeWM (morg_glaze).

O Windows é sempre falso (Gravador/SubprocessFalso): fixa-se a sequência de chamadas e as decisões
(ligar-se à fila de entrada só quando é preciso, tentar sem BREAKAWAY quando o job o recusa, …).
"""

import json
import sys
import tempfile
import unittest
from pathlib import Path

from falsos_windows import Gravador, SubprocessFalso, falha_uma_vez
from sistema_falso import SistemaFalso, carregar_bar_helper, espaco

# As funções reais (o SistemaFalso troca-as pelos falsos do GlazeWM e do abridor).
carregar_bar_helper()
SHELL_OPEN = sys.modules["morg_processos"]._shell_open
GLAZE = sys.modules["morg_glaze"]._glaze


class MutexComNome(unittest.TestCase):

    def entrar(self, cria, espera):
        with SistemaFalso() as s:
            k32 = Gravador("kernel32", CreateMutexW=cria, WaitForSingleObject=espera, ReleaseMutex=1, CloseHandle=1)
            s.trocar("kernel32", k32)
            with s.bh._NamedMutex("Local\\x", 500) as obtido:
                pass
            return obtido, k32.nomes()

    def test_obtido_ou_abandonado_entra_e_liberta(self):
        for espera in (0x0, 0x80):
            with self.subTest(espera=espera):
                self.assertEqual(self.entrar(9, espera),
                                 (True, ["CreateMutexW", "WaitForSingleObject", "ReleaseMutex", "CloseHandle"]))

    def test_ocupado_nao_liberta_mas_fecha(self):
        self.assertEqual(self.entrar(9, 0x102), (False, ["CreateMutexW", "WaitForSingleObject", "CloseHandle"]))

    def test_sem_handle_nao_faz_mais_nada(self):
        self.assertEqual(self.entrar(0, 0), (False, ["CreateMutexW"]))


class FocoEVisibilidade(unittest.TestCase):

    def u32(self, fg_thread, **mais):
        return Gravador("user32", GetForegroundWindow=50, GetWindowThreadProcessId=lambda h, p: fg_thread,
                        AttachThreadInput=1, ShowWindow=1, BringWindowToTop=1, SetForegroundWindow=1,
                        SetFocus=1, PostMessageW=1, **mais)

    def test_is_cloaked_le_o_atributo_do_dwm(self):
        for valor in (0, 1):
            with self.subTest(valor=valor), SistemaFalso() as s:
                s.trocar("dwmapi", Gravador("dwmapi", DwmGetWindowAttribute=lambda h, a, ref, n, v=valor: setattr(
                    ref._obj, "value", v)))
                self.assertEqual(s.bh._is_cloaked(7), bool(valor))

    def test_bring_to_front_liga_e_desliga_a_fila_de_outra_thread(self):
        with SistemaFalso() as s:
            u32 = self.u32(fg_thread=11)
            s.trocar("user32", u32)
            s.trocar("kernel32", Gravador("kernel32", GetCurrentThreadId=22))
            s.bh._bring_to_front(7)
            self.assertEqual(u32.nomes(), ["GetForegroundWindow", "GetWindowThreadProcessId", "AttachThreadInput",
                                           "ShowWindow", "BringWindowToTop", "SetForegroundWindow",
                                           "AttachThreadInput"])
            self.assertEqual(u32.de("AttachThreadInput"), [(22, 11, True), (22, 11, False)])

    def test_bring_to_front_sem_fila_alheia_nao_se_liga(self):
        for fg_thread in (0, 22):  # sem janela em primeiro plano, ou já é esta thread
            with self.subTest(fg_thread=fg_thread), SistemaFalso() as s:
                u32 = self.u32(fg_thread)
                s.trocar("user32", u32)
                s.trocar("kernel32", Gravador("kernel32", GetCurrentThreadId=22))
                s.bh._bring_to_front(7)
                self.assertNotIn("AttachThreadInput", u32.nomes())
                self.assertEqual(u32.de("ShowWindow"), [(7, 5)])

    def test_focus_webview_foca_a_janela_de_topo_e_manda_wm_setfocus(self):
        for tid, ligou in ((11, True), (22, False)):
            with self.subTest(tid=tid), SistemaFalso() as s:
                u32 = self.u32(tid)
                s.trocar("user32", u32)
                s.trocar("kernel32", Gravador("kernel32", GetCurrentThreadId=22))
                s.bh._focus_webview(7)
                self.assertEqual(u32.de("SetFocus"), [(7,)])
                self.assertEqual(u32.de("PostMessageW"), [(7, 0x0007, 0, 0)])
                self.assertEqual("AttachThreadInput" in u32.nomes(), ligou)


class EsconderQuandoPerdeOFoco(unittest.TestCase):
    """_hide_when_unfocused: espera que o guia fique ativo e esconde-o 0,7 s depois de outra janela o ser."""

    def correr(self, primeiro_plano, visivel=lambda agora: True):
        with SistemaFalso() as s:
            inicio = s.relogio.agora
            u32 = Gravador("user32", GetForegroundWindow=lambda: primeiro_plano(s.relogio.agora - inicio),
                           IsWindowVisible=lambda h: visivel(s.relogio.agora - inicio), ShowWindow=1)
            s.trocar("user32", u32)
            s.bh._hide_when_unfocused(7)
            return u32.de("ShowWindow"), s.relogio.agora - inicio

    def test_outra_janela_ativa_ha_mais_de_0_7_s_esconde(self):
        # Ativa aos 0,2 s; outra janela a partir de 1 s; um regresso breve aos 1,3 s recomeça a contagem.
        def primeiro_plano(t):
            return 7 if 0.2 <= t < 1.0 or 1.3 <= t < 1.4 else 99
        escondeu, duracao = self.correr(primeiro_plano)
        self.assertEqual(escondeu, [(7, 0)])
        self.assertGreater(duracao, 2.1)

    def test_nunca_fica_ativa_continua_a_vigiar_e_esconde(self):
        escondeu, _ = self.correr(lambda t: 99)
        self.assertEqual(escondeu, [(7, 0)])

    def test_a_pagina_esconde_se_sozinha(self):
        escondeu, _ = self.correr(lambda t: 7, visivel=lambda t: t < 3)
        self.assertEqual(escondeu, [])


class LancarProcessos(unittest.TestCase):

    def test_shell_open_ok_e_falha(self):
        for rc, ok, registo in ((42, True, "abri app.exe -x"), (2, False, "não consegui abrir app.exe (2)"),
                                (None, False, "não consegui abrir app.exe (None)")):
            with self.subTest(rc=rc), SistemaFalso() as s:
                sh = Gravador("shell32", ShellExecuteW=rc)
                s.trocar("shell32", sh)
                self.assertEqual(SHELL_OPEN({"file": "app.exe", "args": "-x"}, s.log), ok)
                self.assertEqual(s.registo, [registo])
                self.assertEqual(sh.de("ShellExecuteW"), [(None, "open", "app.exe", "-x", None, 1)])

    def test_shell_open_sem_argumentos_nem_registo(self):
        with SistemaFalso() as s:
            sh = Gravador("shell32", ShellExecuteW=33)
            s.trocar("shell32", sh)
            self.assertTrue(SHELL_OPEN({"file": "explorer"}))
            SHELL_OPEN({"file": "explorer"}, s.log)
            self.assertEqual(sh.de("ShellExecuteW")[0][3], None)
            self.assertEqual(s.registo, ["abri explorer"])

    def test_start_widget(self):
        with SistemaFalso() as s, tempfile.TemporaryDirectory() as pasta:
            zebar = Path(pasta) / "zebar.exe"
            s.trocar("ZEBAR", zebar)
            self.assertFalse(s.bh._start_widget("pack", "guia"))  # sem o Zebar instalado
            zebar.write_text("")
            sp = SubprocessFalso()
            s.trocar("subprocess", sp)
            self.assertTrue(s.bh._start_widget("pack", "guia"))
            self.assertEqual(sp.lancados[0][0], [str(zebar), "start-widget-preset", "--pack", "pack",
                                                 "--widget-name", "guia", "--preset", "default"])
            s.trocar("subprocess", SubprocessFalso(falha_uma_vez()))
            self.assertFalse(s.bh._start_widget("pack", "guia"))

    def test_popen_detached_tenta_fora_do_job_e_depois_sem_isso(self):
        with SistemaFalso() as s:
            sp = SubprocessFalso()
            s.trocar("subprocess", sp)
            s.bh._popen_detached(["a"], cwd="x")
            sp2 = SubprocessFalso(falha_uma_vez())
            s.trocar("subprocess", sp2)
            s.bh._popen_detached(["b"])
            self.assertEqual(sp.lancados, [(["a"], {"creationflags": 0x01000208, "close_fds": True, "cwd": "x"})])
            self.assertEqual([kw["creationflags"] for _, kw in sp2.lancados], [0x01000208, 0x208])

    def test_spawn_detached_relanca_o_bar_helper(self):
        with SistemaFalso() as s:
            sp = SubprocessFalso(falha_uma_vez())
            s.trocar("subprocess", sp)
            s.bh._spawn_detached("after-exit")
            esperado = [str(s.bh.PYTHONW), "-I", str(s.bh.BAR_HELPER), "after-exit"]
            self.assertEqual([(cmd, kw["creationflags"]) for cmd, kw in sp.lancados],
                             [(esperado, 0x01000208), (esperado, 0x208)])
            sp = SubprocessFalso()
            s.trocar("subprocess", sp)
            s.bh._spawn_detached("x")
            self.assertEqual(len(sp.lancados), 1)

    def test_wait_for_devolve_o_resultado_ou_none_no_fim_do_prazo(self):
        with SistemaFalso() as s:
            inicio = s.relogio.agora
            self.assertEqual(s.bh._wait_for(lambda: s.relogio.agora - inicio >= 1 and "ok", 5, poll=0.5), "ok")
            self.assertIsNone(s.bh._wait_for(lambda: False, 2))
            self.assertAlmostEqual(s.relogio.agora - inicio, 3.0, places=5)


class CliDoGlaze(unittest.TestCase):

    def test_json_vazio_ou_estragado(self):
        with SistemaFalso() as s:
            for saida, esperado in (('{"success": true}', {"success": True}), ("", {}), ("lixo", {})):
                with self.subTest(saida=saida):
                    sp = SubprocessFalso(lambda cmd, saida=saida: saida)
                    s.trocar("subprocess", sp)
                    self.assertEqual(GLAZE("query", "workspaces"), esperado)
                    self.assertEqual(sp.corridos[0][0], [str(s.bh.GLAZE_CLI), "query", "workspaces"])

    def test_glaze_ausente_ou_pendurado(self):
        with SistemaFalso() as s:
            for erro in (OSError("não existe"), SubprocessFalso.TimeoutExpired("glazewm", 10)):
                with self.subTest(erro=type(erro).__name__):
                    def rebenta(cmd, erro=erro):
                        raise erro
                    s.trocar("subprocess", SubprocessFalso(rebenta))
                    self.assertEqual(GLAZE("query", "workspaces"), {})


def janela(ident, estado="tiling"):
    return {"id": ident, "type": "window", "processName": "x", "state": {"type": estado}}


class RestaurarMinimizada(unittest.TestCase):

    def test_restaura_a_mais_recente_pela_ordem_do_foco_dentro_das_divisoes(self):
        divisao = {"id": "d", "type": "split", "childFocusOrder": ["m2", "fantasma"],
                   "children": [janela("m1", "minimized"), janela("m2", "minimized")]}
        ws = espaco("1", foco=True)
        ws.update(childFocusOrder=["t"], children=[divisao, janela("t")])
        with SistemaFalso([ws, espaco("2")]) as s:
            s.bh.restore_minimized()
            self.assertEqual(s.glaze.comandos, [("command", "--id", "m2", "toggle-minimized"),
                                                ("command", "focus", "--container-id", "m2")])

    def test_sem_minimizadas_ou_sem_workspace_focado_nao_faz_nada(self):
        ws = espaco("1", foco=True)
        ws["children"] = [{"id": "d", "type": "split", "children": [janela("a")]}]
        for workspaces in ([ws], [espaco("1")]):
            with self.subTest(focado=workspaces[0]["hasFocus"]), SistemaFalso(workspaces) as s:
                s.bh.restore_minimized()
                self.assertEqual(s.glaze.comandos, [])

    def test_glaze_desligado(self):
        with SistemaFalso() as s:
            s.glaze.ligado = False
            s.bh.restore_minimized()
            self.assertEqual(json.dumps(s.glaze.comandos), "[]")


if __name__ == "__main__":
    unittest.main()
