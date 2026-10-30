"""Testes dos hooks do Claude Code em .claude/hooks/ (as decisões e a ligação no .claude/settings.json).

Cada caso vem de um comando real deste projeto: os que têm de passar (glazewm command, tarefa agendada,
ler ficheiros) e os que têm de ser recusados (arrancar o GlazeWM, o Zebar ou o boot — armadilha A2).
A guarda do git tem os seus testes em test_guarda_do_git.py.
"""

import json
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

from carregar_por_caminho import PASTA_HOOKS, RAIZ, carregar_hook

arranque = carregar_hook("bloquear_arranque")
linhas = carregar_hook("limite_de_linhas")


class LigacaoNoSettings(unittest.TestCase):
    """Os hooks são a rede (Morg Laws): cada um está ligado, existe e bloqueia também se ele próprio falhar."""

    def hooks_ligados(self):
        definicoes = json.loads((RAIZ / ".claude" / "settings.json").read_text(encoding="utf-8"))
        return [hook for grupo in definicoes["hooks"]["PreToolUse"] for hook in grupo["hooks"]]

    def test_cada_hook_existe_e_bloqueia_se_falhar(self):
        for hook in self.hooks_ligados():
            nome = re.search(r"\.claude/hooks/(\w+\.py)", hook["command"]).group(1)
            with self.subTest(hook=nome):
                self.assertTrue((PASTA_HOOKS / nome).is_file())
                self.assertEqual(hook.get("onFailure"), "block", "sem onFailure: block, um hook partido deixa passar")

    def test_todos_os_hooks_da_pasta_estao_ligados(self):
        ligados = {re.search(r"(\w+\.py)", hook["command"]).group(1) for hook in self.hooks_ligados()}
        self.assertEqual(ligados, {p.name for p in PASTA_HOOKS.glob("*.py")})


def correr_hook(nome, pedido, ambiente=None):
    """Corre o hook como o Claude Code o corre (JSON no stdin); devolve o código de saída e o stderr.

    Com limite de tempo: um hook que entre em ciclo falha o teste em vez de encher a máquina (A30).
    """
    resultado = subprocess.run([sys.executable, "-I", str(PASTA_HOOKS / f"{nome}.py")], input=json.dumps(pedido),
                               capture_output=True, text=True, encoding="utf-8", check=False, timeout=30,
                               env=ambiente)
    return resultado.returncode, resultado.stderr


class BloquearArranque(unittest.TestCase):

    def test_recusa_arrancar_o_ambiente(self):
        perigosos = [
            "glazewm.exe",
            "glazewm start",
            r'& "C:\Program Files\glzr.io\GlazeWM\glazewm.exe"',
            r"Start-Process 'C:\Program Files\glzr.io\GlazeWM\glazewm.exe'",
            "Start-Process -FilePath zebar.exe",
            "zebar startup",
            "zebar start-widget-preset omarchy-catppuccin/bar",
            "cd x; zebar.exe",
            'cmd /c start "" glazewm.exe',
            r'C:\Windows\pyw.exe -I "C:/Users/u/.glzr/zebar/omarchy-catppuccin/bar_helper.py" boot',
            "py -I bar_helper.py layout-restore",
            "python bar_helper.py animacao next",
        ]
        for comando in perigosos:
            with self.subTest(comando=comando):
                self.assertIsNotNone(arranque.motivo_para_bloquear(comando))

    def test_deixa_passar_o_que_e_seguro(self):
        seguros = [
            "glazewm command wm-reload-config",
            "glazewm.exe command wm-exit",
            "glazewm query workspaces",
            'Start-ScheduledTask "GlazeWM (arranque)"',
            "Get-Process glazewm, zebar -ErrorAction SilentlyContinue",
            'grep -n "bar_helper.py boot" docs/armadilhas.md',
            "py -I bar_helper.py panel state",
            "git log --oneline",
        ]
        for comando in seguros:
            with self.subTest(comando=comando):
                self.assertIsNone(arranque.motivo_para_bloquear(comando))

    def test_como_hook_sai_com_2_e_explica(self):
        codigo, erro = correr_hook("bloquear_arranque", {"tool_name": "Bash", "tool_input": {"command": "zebar.exe"}})
        self.assertEqual(codigo, 2)
        self.assertIn("A2", erro)
        codigo, _ = correr_hook("bloquear_arranque", {"tool_name": "Bash", "tool_input": {"command": "ls"}})
        self.assertEqual(codigo, 0)


class TestesNoPreCommitDoGit(unittest.TestCase):
    """Os testes passaram do hook do Claude para o .githooks/pre-commit, com a mesma guarda da A30."""

    def test_pre_commit_corre_os_testes_e_respeita_a_guarda_a30(self):
        # Regressão A30: sem a guarda, testes -> commit -> testes -> commit… (650 processos em 2026-10-23).
        texto = (RAIZ / ".githooks" / "pre-commit").read_text(encoding="utf-8")
        self.assertIn("scripts/testar.ps1", texto)
        self.assertIn('if [ -n "$MORG_A_TESTAR" ]', texto)
        self.assertIn("MORG_A_TESTAR=1 powershell", texto)


class LimiteDeLinhas(unittest.TestCase):

    def test_conta_linhas_como_o_editor(self):
        self.assertEqual(linhas.contar_linhas("a\nb\n"), 2)
        self.assertEqual(linhas.contar_linhas("a\nb"), 2)
        self.assertEqual(linhas.contar_linhas(""), 0)

    def test_texto_depois_do_write_e_do_edit(self):
        self.assertEqual(linhas.texto_depois("Write", {"content": "novo"}, "velho"), "novo")
        self.assertEqual(linhas.texto_depois("Edit", {"old_string": "a", "new_string": "b"}, "a a"), "b a")
        self.assertEqual(linhas.texto_depois("Edit", {"old_string": "a", "new_string": "b", "replace_all": True},
                                             "a a"), "b b")
        self.assertIsNone(linhas.texto_depois("Edit", {"old_string": "z", "new_string": "b"}, "a"))

    def test_recusa_crescer_acima_do_limite(self):
        self.assertIsNotNone(linhas.motivo_para_bloquear(Path("x.py"), 10, 501))
        self.assertIsNotNone(linhas.motivo_para_bloquear(Path("x.html"), 600, 601))

    def test_deixa_encolher_e_ficar_no_limite(self):
        self.assertIsNone(linhas.motivo_para_bloquear(Path("x.py"), 1982, 1900))  # refatoração
        self.assertIsNone(linhas.motivo_para_bloquear(Path("x.py"), 10, 500))
        self.assertIsNone(linhas.motivo_para_bloquear(Path("x.json"), 10, 9000))  # não é código

    def test_como_hook_recusa_um_write_grande_no_projeto(self):
        caminho = str(PASTA_HOOKS.parent.parent / "tests" / "nao_existe.py")
        pedido = {"tool_name": "Write", "tool_input": {"file_path": caminho, "content": "x\n" * 501}}
        codigo, erro = correr_hook("limite_de_linhas", pedido)
        self.assertEqual(codigo, 2)
        self.assertIn("501", erro)

    def test_como_hook_ignora_ficheiros_fora_do_projeto(self):
        with tempfile.TemporaryDirectory() as pasta:
            pedido = {"tool_name": "Write", "tool_input": {"file_path": str(Path(pasta) / "a.py"),
                                                           "content": "x\n" * 900}}
            codigo, _ = correr_hook("limite_de_linhas", pedido)
        self.assertEqual(codigo, 0)


if __name__ == "__main__":
    unittest.main()
