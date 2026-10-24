"""Não suspender (morg_acordado), ações do Windows (morg_acoes_windows), cortina (morg_cortina) e o
progress.json do ecrã de arranque (morg_ecra_arranque), com o Windows falso.
"""

import sys
import unittest
from types import SimpleNamespace
from unittest import mock

from falsos_windows import Gravador, SubprocessFalso, falha_uma_vez
from sistema_falso import SistemaFalso, carregar_bar_helper

carregar_bar_helper()
ACORDADO, CORTINA, ECRA = (sys.modules[n] for n in ("morg_acordado", "morg_cortina", "morg_ecra_arranque"))


class MutexFalso:
    livre = True

    def __init__(self, nome, timeout_ms=2000):
        pass

    def __enter__(self):
        return MutexFalso.livre

    def __exit__(self, *erro):
        return False


class AcordadoFalso(SistemaFalso):
    """O processo awake-hold é falso: `ligado` diz se o mutex dele existe; arranca/sai ao fim de `demora` s."""

    def __init__(self, ligado=False, arranca_aos=0.1, sai_aos=0.1):
        super().__init__()
        self.ligado, self.arranca_aos, self.sai_aos = ligado, arranca_aos, sai_aos

    def __enter__(self):
        super().__enter__()
        self.k32 = Gravador("kernel32", OpenMutexW=lambda *a: 5 if self.ligado else 0, CloseHandle=1,
                            OpenEventW=lambda *a: 6 if self.ligado else 0, SetEvent=self._parar)
        self.trocar("kernel32", self.k32)
        self.trocar("_NamedMutex", MutexFalso)
        self.sp = SubprocessFalso(self._arrancar)
        self.trocar("subprocess", self.sp)
        MutexFalso.livre = True
        return self

    def _quando(self, segundos, ligado):
        inicio = self.relogio.agora

        def mudar(agora):
            if agora - inicio >= segundos:
                self.ligado = ligado
        self.relogio.ao_avancar.append(mudar)

    def _parar(self, handle):
        self._quando(self.sai_aos, False)
        return 1

    def _arrancar(self, cmd):
        self._quando(self.arranca_aos, True)
        return ""


class NaoSuspender(unittest.TestCase):

    def test_status(self):
        for ligado, esperado in ((True, "on"), (False, "off")):
            with self.subTest(ligado=ligado), AcordadoFalso(ligado) as s:
                self.assertEqual(s.bh.awake_status(), esperado)
                self.assertEqual(s.k32.nomes(), ["OpenMutexW", "CloseHandle"] if ligado else ["OpenMutexW"])

    def test_toggle_liga_fora_do_job_e_confirma(self):
        with AcordadoFalso() as s:
            self.assertEqual(s.bh.awake_toggle(), "on")
            cmd, kw = s.sp.lancados[0]
            self.assertEqual(cmd, [str(s.bh.PYTHONW), "-I", str(s.bh.BAR_HELPER), "awake-hold"])
            self.assertEqual(kw["creationflags"], 0x01000208)

    def test_toggle_sem_breakaway_tenta_de_novo(self):
        with AcordadoFalso() as s:
            s.sp.ao_correr = falha_uma_vez()
            s.relogio.ao_avancar.append(lambda agora: setattr(s, "ligado", True))
            self.assertEqual(s.bh.awake_toggle(), "on")
            self.assertEqual([kw["creationflags"] for _, kw in s.sp.lancados], [0x01000208, 0x208])

    def test_toggle_que_nao_arranca_desiste_ao_fim_de_3_s(self):
        with AcordadoFalso(arranca_aos=99) as s:
            inicio = s.relogio.agora
            self.assertEqual(s.bh.awake_toggle(), "off")
            self.assertAlmostEqual(s.relogio.agora - inicio, 3.0, places=5)

    def test_toggle_ligado_desliga(self):
        with AcordadoFalso(ligado=True) as s:
            self.assertEqual(s.bh.awake_toggle(), "off")
            self.assertEqual(s.sp.lancados, [])

    def test_toggle_com_o_mutex_ocupado_so_diz_o_estado(self):
        with AcordadoFalso(ligado=True) as s:
            MutexFalso.livre = False
            self.assertEqual(s.bh.awake_toggle(), "on")

    def test_off_espera_ate_2_s_pelo_processo(self):
        with AcordadoFalso(ligado=True, sai_aos=99) as s:
            inicio = s.relogio.agora
            self.assertEqual(s.bh.awake_off(), "on")
            self.assertAlmostEqual(s.relogio.agora - inicio, 2.0, places=5)
        with AcordadoFalso() as s:
            self.assertEqual(s.bh.awake_off(), "off")
            self.assertNotIn("SetEvent", s.k32.nomes())

    def hold(self, mutex, ultimo_erro, aceita):
        with SistemaFalso() as s:
            k32 = Gravador("kernel32", CreateMutexW=mutex, CreateEventW=8, WaitForSingleObject=0,
                           SetThreadExecutionState=lambda flags: aceita)
            s.trocar("kernel32", k32)
            with mock.patch.object(ACORDADO, "ctypes", SimpleNamespace(get_last_error=lambda: ultimo_erro)):
                s.bh.awake_hold()
            return k32.chamadas

    def test_hold_mantem_acordado_ate_ao_evento(self):
        self.assertEqual(self.hold(5, 0, 1)[1:], [
            ("CreateEventW", None, True, False, "Local\\OmarchyAwakeStop"),
            ("SetThreadExecutionState", 0x80000003), ("WaitForSingleObject", 8, 0xFFFFFFFF),
            ("SetThreadExecutionState", 0x80000000)])

    def test_hold_sai_se_ja_houver_outro_ou_o_windows_recusar(self):
        self.assertEqual(len(self.hold(0, 0, 1)), 1)
        self.assertEqual(len(self.hold(5, 183, 1)), 1)
        self.assertEqual([c[0] for c in self.hold(5, 0, 0)], ["CreateMutexW", "CreateEventW",
                                                              "SetThreadExecutionState"])


class AcoesDoWindows(unittest.TestCase):

    def test_quick_carrega_win_a(self):
        with SistemaFalso() as s:
            enviados = []
            s.trocar("user32", Gravador("user32", SendInput=lambda n, seq, tam: enviados.extend(
                (seq[i].type, seq[i].ki.wVk, seq[i].ki.dwFlags) for i in range(n)) or n))
            s.bh.quick_settings()
            self.assertEqual(enviados, [(1, 0x5B, 0), (1, 0x41, 0), (1, 0x41, 2), (1, 0x5B, 2)])

    def test_lock_e_on_exit(self):
        with SistemaFalso() as s:
            u32 = Gravador("user32", LockWorkStation=1)
            s.trocar("user32", u32)
            lancados = []
            s.trocar("_spawn_detached", lambda *a: lancados.append(a))
            s.bh.lock()
            s.bh.on_exit()
            self.assertEqual((u32.nomes(), lancados), (["LockWorkStation"], [("after-exit",)]))

    def test_power_so_com_sim(self):
        for resposta, esperado in ((6, [["shutdown", "/r", "/t", "0"]]), (7, [])):
            with self.subTest(resposta=resposta), SistemaFalso() as s:
                u32 = Gravador("user32", MessageBoxW=resposta)
                sp = SubprocessFalso()
                s.trocar("user32", u32)
                s.trocar("subprocess", sp)
                s.bh.power("reboot")
                self.assertEqual([cmd for cmd, _ in sp.corridos], esperado)
                self.assertEqual(u32.de("MessageBoxW")[0][1:3], ("Reiniciar o computador agora?", "Sistema"))
        with SistemaFalso() as s:
            sp = SubprocessFalso()
            s.trocar("user32", Gravador("user32", MessageBoxW=6))
            s.trocar("subprocess", sp)
            s.bh.power("shutdown")
            self.assertEqual(sp.corridos[0][0], ["shutdown", "/s", "/t", "0"])

    def after_exit(self, glaze_ate, com_uncloak):
        with SistemaFalso() as s:
            inicio = s.relogio.agora
            sp = SubprocessFalso(lambda cmd: "glazewm.exe 123" if s.relogio.agora - inicio < glaze_ate else "")
            s.trocar("subprocess", sp)
            desligado = []
            s.trocar("awake_off", lambda: desligado.append(True))
            ps1 = s.pasta / "uncloak.ps1"
            if com_uncloak:
                ps1.write_text("")
            s.trocar("UNCLOAK_PS1", ps1)
            s.bh.after_exit()
            return [cmd[0] for cmd, _ in sp.corridos], desligado, s.relogio.agora - inicio

    def test_after_exit_espera_o_glaze_desliga_o_cafe_e_mostra_as_janelas(self):
        corridos, desligado, duracao = self.after_exit(glaze_ate=1.2, com_uncloak=True)
        self.assertEqual(corridos, ["tasklist"] * 4 + ["powershell"])
        self.assertEqual((desligado, duracao), ([True], 1.5))

    def test_after_exit_desiste_aos_20_s_e_sem_uncloak(self):
        corridos, desligado, duracao = self.after_exit(glaze_ate=999, com_uncloak=False)
        self.assertNotIn("powershell", corridos)
        self.assertEqual((desligado, duracao), ([True], 20.0))


class CortinaPreta(unittest.TestCase):

    def test_cria_com_a_imagem_da_animacao_e_espera_a_janela(self):
        def run_falso(self):
            self.hwnd = 77
            self._ready.set()
        with SistemaFalso() as s, mock.patch.object(CORTINA._BlackCover, "_run", run_falso):
            s.trocar("ANIMACOES", {"cafe": ("Café", "cafe.bmp", 280, 280), "lua": ("Lua", "lua.bmp", 10, 20)})
            cortina = s.bh._BlackCover("lua")
            self.assertEqual((cortina.image, cortina.img_w, cortina.img_h, cortina.hwnd), ("lua.bmp", 10, 20, 77))
            self.assertEqual(s.bh._BlackCover("nenhuma").image, "cafe.bmp")

    def test_close_mostra_o_cursor_e_fecha_uma_vez(self):
        with SistemaFalso() as s:
            u32 = Gravador("user32", ShowCursor=1, PostMessageW=1)
            s.trocar("user32", u32)
            cortina = CORTINA._BlackCover.__new__(CORTINA._BlackCover)
            cortina.hwnd = 77
            cortina.close()
            cortina.close()
            self.assertEqual(u32.chamadas, [("ShowCursor", True), ("PostMessageW", 77, 0x0010, 0, 0)])


class EcraDeArranque(unittest.TestCase):

    def test_save_tenta_de_novo_se_o_zebar_estiver_a_ler(self):
        for falhas, gravou in ((3, True), (10, False)):
            with self.subTest(falhas=falhas), SistemaFalso() as s:
                destino = s.pasta / "progress.json"
                s.trocar("PROGRESS_FILE", destino)
                tentativas = []

                def substituir(origem, alvo, falhas=falhas, tentativas=tentativas):
                    tentativas.append(1)
                    if len(tentativas) <= falhas:
                        raise PermissionError("em uso")
                    origem.replace(alvo)
                with mock.patch.object(ECRA, "os", SimpleNamespace(replace=substituir)):
                    ECRA._Progress("cafe")
                self.assertEqual((destino.exists(), len(tentativas)), (gravou, min(falhas + 1, 10)))

    def test_splash_to_top_sem_ativar(self):
        for hwnd in (0, 14):
            with self.subTest(hwnd=hwnd), SistemaFalso() as s:
                u32 = Gravador("user32", FindWindowW=hwnd, SetWindowPos=1)
                s.trocar("user32", u32)
                s.bh._splash_to_top()
                posicoes = u32.de("SetWindowPos")
                self.assertEqual(len(posicoes), 1 if hwnd else 0)
                if hwnd:
                    self.assertEqual((posicoes[0][0], posicoes[0][1].value, posicoes[0][6]), (14, 2**64 - 1, 0x13))  # HWND_TOPMOST = -1

    def test_splash_ready_sinaliza_o_evento(self):
        for handle, esperado in ((9, ["OpenEventW", "SetEvent", "CloseHandle"]), (0, ["OpenEventW"])):
            with self.subTest(handle=handle), SistemaFalso() as s:
                k32 = Gravador("kernel32", OpenEventW=handle, SetEvent=1, CloseHandle=1)
                s.trocar("kernel32", k32)
                s.bh.splash_ready()
                self.assertEqual(k32.nomes(), esperado)


if __name__ == "__main__":
    unittest.main()
