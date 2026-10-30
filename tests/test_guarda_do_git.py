"""Guarda do git (.claude/hooks/guarda_do_git.py): o agente não salta nem desliga os portões do git.

Os portões (testes, identidade, lista negra, mensagem) correm nos hooks do git em .githooks/. Esta guarda trava,
a partir do agente, o que os salta ou estraga. Testa-se a decisão; o ligar ao settings.json testa-se em
test_hooks.py.
"""

import json
import subprocess
import sys
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from carregar_por_caminho import PASTA_HOOKS, carregar_hook

guarda = carregar_hook("guarda_do_git")


def hooks_certos():
    return ".githooks"


class Recusa(unittest.TestCase):

    def assertRecusa(self, comandos, texto, hooks_path=hooks_certos):
        for comando in comandos:
            with self.subTest(comando=comando):
                motivo = guarda.motivo_para_bloquear(comando, hooks_path)
                self.assertIsNotNone(motivo)
                self.assertIn(texto, motivo)

    def test_saltar_os_hooks(self):
        self.assertRecusa(['git commit --no-verify -F m.txt', 'git commit -n -F m.txt', 'git commit -qn -F m',
                           'git -C "C:/a b" commit --no-verify -F m', 'git push --no-verify',
                           'git merge --no-verify main'], "--no-verify")

    def test_mudar_ou_desligar_o_hooks_path(self):
        self.assertRecusa(['git config core.hooksPath /dev/null', 'git config --unset core.hooksPath',
                           'git config --local core.hooksPath x', 'git -c core.hooksPath=x commit -F m',
                           'git config core.hookspath ""'], "core.hooksPath")

    def test_commit_com_o_hooks_path_errado(self):
        self.assertRecusa(['git commit -F m.txt -- a.py'], "não é .githooks", hooks_path=lambda: "")

    def test_preparar_tudo(self):
        self.assertRecusa(["git add -A", "git add .", "git add --all", "git add -Av", "git add :/",
                           "git commit -a -F m", "git commit -am x", "git commit --all -F m",
                           "git commit -F m -- .", "cd x && git add . && git commit -F m"], "caminho")

    def test_commit_sem_caminhos(self):
        # Um commit sem caminhos leva o que outra sessão deixou preparado (aconteceu na ML3 com c9f440b).
        self.assertRecusa(["git commit -F m.txt", "git commit --amend -F m.txt", "git commit -q -F m && git log"],
                          "por caminho")

    def test_saltar_os_testes_com_a_marca_a30(self):
        # MORG_A_TESTAR=1 é só para dentro dos testes (A30); num commit do agente salta o testar.ps1.
        self.assertRecusa(["MORG_A_TESTAR=1 git commit -F m -- a.py", "$env:MORG_A_TESTAR='1'; git commit -F m -- a",
                           "set MORG_A_TESTAR=1&& git commit -F m -- a"], "MORG_A_TESTAR")

    def test_mensagem_com_varias_linhas(self):
        self.assertRecusa(['git commit -m "título\n\ncorpo"', 'git commit --message="a\nb"',
                           "git commit -m \"$(cat <<'EOF'\nx\nEOF\n)\"", 'git commit -qm "a\nb"'], "-F")


class DeixaPassar(unittest.TestCase):

    def test_comandos_normais(self):
        lido = mock.Mock(return_value=".githooks")
        for comando in ['git add -- a.py "b c.md"', 'git commit -F m.txt -- a.py', 'git commit -m "uma linha" a.py',
                        'git config --get core.hooksPath', 'git config core.hooksPath',
                        'git config core.hooksPath .githooks', 'git push -n origin exp/a', 'git status --short -uall',
                        'git log --oneline -5', 'git commit --amend -F m.txt -- a.py', "echo 'sem aspas fechadas",
                        'git commit -F m --author "Ana <a@example.com>" -- a.py', 'git commit -C HEAD -- a.py',
                        'git commit -F m -- -ficheiro-com-hifen.py', 'git -C pasta --no-pager log', 'ls -la', '']:
            with self.subTest(comando=comando):
                self.assertIsNone(guarda.motivo_para_bloquear(comando, lido))

    def test_commit_que_fecha_um_merge_vai_sem_caminhos(self):
        with mock.patch.object(guarda, "merge_em_curso", return_value=True):
            self.assertIsNone(guarda.motivo_para_bloquear("git commit -F m.txt", hooks_certos))

    def test_merge_em_curso_ve_o_merge_head(self):
        self.assertEqual(guarda.merge_em_curso(), (Path(guarda.RAIZ) / ".git" / "MERGE_HEAD").exists())

    def test_so_le_o_hooks_path_quando_ha_commit(self):
        lido = mock.Mock(return_value="")
        guarda.motivo_para_bloquear("git status && git log", lido)
        lido.assert_not_called()

    def test_aspas_por_fechar_usam_a_divisao_simples(self):
        self.assertIsNotNone(guarda.motivo_para_bloquear("git add . ; echo 'x", hooks_certos))


class PontoDeEntrada(unittest.TestCase):

    def test_le_o_hooks_path_deste_repositorio(self):
        correr = mock.Mock(return_value=SimpleNamespace(stdout=" .githooks \n"))
        self.assertEqual(guarda.ler_hooks_path(correr), ".githooks")
        self.assertEqual(correr.call_args.args[0][-3:], ["config", "--get", "core.hooksPath"])

    def correr(self, comando):
        return subprocess.run([sys.executable, "-I", str(PASTA_HOOKS / "guarda_do_git.py")],
                              input=json.dumps({"tool_name": "Bash", "tool_input": {"command": comando}}),
                              capture_output=True, text=True, encoding="utf-8", check=False, timeout=30)

    def test_como_hook_sai_com_2_e_explica(self):
        resultado = self.correr("git add -A")
        self.assertEqual(resultado.returncode, 2)
        self.assertIn("Morg Laws", resultado.stderr)

    def test_como_hook_deixa_passar(self):
        self.assertEqual(self.correr("git status").returncode, 0)

    def test_este_repositorio_tem_os_portoes_ligados(self):
        self.assertEqual(guarda.ler_hooks_path(), ".githooks", "corra: git config core.hooksPath .githooks")
        self.assertTrue((Path(guarda.RAIZ) / ".githooks" / "pre-commit").is_file())


if __name__ == "__main__":
    unittest.main()
