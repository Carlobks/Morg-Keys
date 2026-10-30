"""Hook perguntar_antes (.claude/hooks/perguntar_antes.py): push e instalações pedem sempre o "sim" do dono.

Regressão de 2026-10-30 (ML4): com a regra "ask" de `Bash(git push *)` no settings.json, um
`git push --dry-run` correu sem pergunta (modo automático ou o `cd …;` antes do comando). O hook devolve a
decisão "ask" ao Claude Code, que pergunta seja qual for o modo.
"""

import json
import subprocess
import sys
import unittest

from carregar_por_caminho import PASTA_HOOKS, carregar_hook

perguntar = carregar_hook("perguntar_antes")


class Decisao(unittest.TestCase):

    def test_pergunta_antes_de_publicar_ou_instalar(self):
        for comando in ['cd "C:/x y"; git push --dry-run C:/b.git HEAD:refs/heads/t', "git push origin exp/a",
                        'git -C "C:/a b" push', "git -c x=y push --tags", "npm install", "npm i -D x", "npm ci",
                        "npx skills@1.7.4 add a/b", "pip install coverage", "py -m pip install ruff",
                        "winget install Gitleaks.Gitleaks", "Install-Module Pester -Force", "choco install x",
                        "scoop install x", "x && git.exe push"]:
            with self.subTest(comando=comando):
                self.assertIsNotNone(perguntar.motivo_para_perguntar(comando))

    def test_nao_pergunta_o_resto(self):
        for comando in ["git status", "git log --grep push", "git commit -F m -- a.py", "npm audit --json",
                        "npm --version", "pip list", "winget show Gitleaks.Gitleaks", "Get-Module Pester", ""]:
            with self.subTest(comando=comando):
                self.assertIsNone(perguntar.motivo_para_perguntar(comando))


class RegrasDoProprioAgente(unittest.TestCase):
    """O agente não muda as próprias regras de segurança sem o "sim" do dono (Akita #79)."""

    def test_pergunta_ao_editar_as_regras(self):
        raiz = perguntar.RAIZ
        for caminho in [raiz / ".claude" / "settings.json", raiz / ".claude" / "settings.local.json",
                        raiz / ".claude" / "hooks" / "guarda_do_git.py", raiz / ".githooks" / "pre-commit",
                        str(raiz / ".claude" / "hooks" / "novo.py").replace("\\", "/")]:
            with self.subTest(caminho=str(caminho)):
                self.assertIsNotNone(perguntar.motivo_para_perguntar_ficheiro(str(caminho)))

    def test_nao_pergunta_nos_outros_ficheiros(self):
        for caminho in [perguntar.RAIZ / "scripts" / "testar.ps1", perguntar.RAIZ / "docs" / "README.md",
                        perguntar.RAIZ.parent / ".claude" / "settings.json", ""]:
            with self.subTest(caminho=str(caminho)):
                self.assertIsNone(perguntar.motivo_para_perguntar_ficheiro(str(caminho)))


class ComoHook(unittest.TestCase):

    def correr(self, comando, ferramenta="Bash"):
        entrada = {"file_path": comando} if ferramenta in ("Write", "Edit") else {"command": comando}
        return subprocess.run([sys.executable, "-I", str(PASTA_HOOKS / "perguntar_antes.py")],
                              input=json.dumps({"tool_name": ferramenta, "tool_input": entrada}),
                              capture_output=True, text=True, encoding="utf-8", check=False, timeout=30)

    def test_no_edit_das_regras_tambem_pergunta(self):
        resultado = self.correr(str(perguntar.RAIZ / ".claude" / "settings.json"), "Edit")
        self.assertEqual(json.loads(resultado.stdout)["hookSpecificOutput"]["permissionDecision"], "ask")
        self.assertEqual(self.correr(str(perguntar.RAIZ / "README.md"), "Write").stdout, "")

    def test_devolve_a_decisao_ask_com_o_motivo(self):
        resultado = self.correr("git push origin exp/a")
        self.assertEqual(resultado.returncode, 0)
        saida = json.loads(resultado.stdout)["hookSpecificOutput"]
        self.assertEqual(saida["hookEventName"], "PreToolUse")
        self.assertEqual(saida["permissionDecision"], "ask")
        self.assertIn("push", saida["permissionDecisionReason"])

    def test_sem_motivo_nao_diz_nada(self):
        resultado = self.correr("git status")
        self.assertEqual((resultado.returncode, resultado.stdout), (0, ""))


if __name__ == "__main__":
    unittest.main()
