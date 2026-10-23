"""Testes dos hooks do Claude Code em .claude/hooks/ (as decisões; o ligar ao settings.json prova-se à mão).

Cada caso vem de um comando real deste projeto: os que têm de passar (glazewm command, tarefa agendada,
ler ficheiros) e os que têm de ser recusados (arrancar o GlazeWM, o Zebar ou o boot — armadilha A2).
"""

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

PASTA_HOOKS = Path(__file__).resolve().parent.parent / ".claude" / "hooks"


def carregar(nome):
    """Importa um hook pelo caminho (a pasta .claude não é um pacote)."""
    especificacao = importlib.util.spec_from_file_location(nome, PASTA_HOOKS / f"{nome}.py")
    modulo = importlib.util.module_from_spec(especificacao)
    especificacao.loader.exec_module(modulo)
    return modulo


arranque = carregar("bloquear_arranque")
commit = carregar("testes_antes_do_commit")
linhas = carregar("limite_de_linhas")


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


class TestesAntesDoCommit(unittest.TestCase):

    def test_reconhece_commits(self):
        for comando in ['git commit -m "x"', 'git -C "C:/a b" commit -q -m x', "git add -A && git commit -F m.txt",
                        "git -c user.name=x commit --amend"]:
            with self.subTest(comando=comando):
                self.assertTrue(commit.e_commit(comando))

    def test_ignora_o_resto(self):
        for comando in ["git status", "git log --grep commit", "echo commit", "git push", "git show HEAD"]:
            with self.subTest(comando=comando):
                self.assertFalse(commit.e_commit(comando))

    def test_sem_commit_nao_corre_os_testes(self):
        # Se corresse os testes, demoraria segundos; aqui só verifica que sai logo com 0.
        codigo, _ = correr_hook("testes_antes_do_commit", {"tool_name": "Bash", "tool_input": {"command": "git status"}})
        self.assertEqual(codigo, 0)

    def test_dentro_dos_testes_nao_volta_a_correr_os_testes(self):
        # Regressão A30: sem esta proteção, testes -> hook -> testes -> hook… (650 processos).
        # Testa-se a decisão, não o processo: um hook estragado aqui voltaria a entrar em ciclo.
        self.assertTrue(commit.deve_correr_testes('git commit -m "x"', {}))
        self.assertFalse(commit.deve_correr_testes('git commit -m "x"', {commit.MARCA_A_TESTAR: "1"}))
        self.assertFalse(commit.deve_correr_testes("git status", {}))


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
