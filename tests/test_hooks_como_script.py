"""Os hooks do Claude Code corridos como o Claude Code os corre (JSON no stdin), dentro deste processo.

Os testes em subprocesso (test_hooks.py, test_guarda_do_git.py, test_perguntar_antes.py) provam o
`py -I` real mas não contam na cobertura; estes passam pelo mesmo main() e pelo `if __name__` e contam.
"""

import json
import tempfile
import unittest
from pathlib import Path

from carregar_por_caminho import PASTA_HOOKS, RAIZ, correr_como_script


def correr(nome, ferramenta, **entrada):
    """Corre .claude/hooks/<nome>.py com o pedido do Claude Code; devolve (código, stdout, stderr)."""
    pedido = {"tool_name": ferramenta, "tool_input": entrada}
    return correr_como_script(PASTA_HOOKS / f"{nome}.py", json.dumps(pedido).encode("utf-8"))


class BloquearArranque(unittest.TestCase):

    def test_recusa_com_2_e_explica_em_utf8(self):
        codigo, _, erro = correr("bloquear_arranque", "Bash", command="zebar.exe")
        self.assertEqual(codigo, 2)
        self.assertIn("armadilha A2", erro)
        self.assertIn("Peça ao utilizador", erro)

    def test_deixa_passar_em_silencio(self):
        self.assertEqual(correr("bloquear_arranque", "Bash", command="git status"), (0, "", ""))
        self.assertEqual(correr("bloquear_arranque", "Write"), (0, "", ""))  # sem comando


class GuardaDoGit(unittest.TestCase):

    def test_recusa_com_2_e_explica(self):
        codigo, _, erro = correr("guarda_do_git", "Bash", command="git commit --no-verify -F m -- a")
        self.assertEqual(codigo, 2)
        self.assertIn("portões do git", erro)

    def test_deixa_passar_lendo_o_hooks_path_deste_repositorio(self):
        # O commit lê o core.hooksPath real (ML3: tem de ser .githooks); um comando com ele certo passa.
        self.assertEqual(correr("guarda_do_git", "Bash", command="git commit -F m -- a.txt"), (0, "", ""))


class LimiteDeLinhas(unittest.TestCase):

    def test_recusa_um_write_grande_no_projeto(self):
        codigo, _, erro = correr("limite_de_linhas", "Write", file_path=str(RAIZ / "tests" / "nao_existe.py"),
                                 content="x\n" * 501)
        self.assertEqual(codigo, 2)
        self.assertIn("501 linhas", erro)

    def test_conta_o_ficheiro_que_ja_existe(self):
        # Este ficheiro tem menos de 500 linhas: um Edit pequeno passa.
        este = Path(__file__)
        self.assertEqual(correr("limite_de_linhas", "Edit", file_path=str(este), old_string="unittest.main()",
                                new_string="unittest.main()  "), (0, "", ""))

    def test_deixa_passar_o_que_nao_da_para_saber_ou_nao_e_do_projeto(self):
        with tempfile.TemporaryDirectory() as pasta:
            fora = correr("limite_de_linhas", "Write", file_path=str(Path(pasta) / "a.py"), content="x\n" * 900)
        casos = {
            "fora do projeto": fora,
            "sem caminho": correr("limite_de_linhas", "Write", content="x\n" * 900),
            "edit que não encaixa": correr("limite_de_linhas", "Edit", file_path=str(RAIZ / "tests" / "nao_existe.py"),
                                           old_string="z", new_string="x\n" * 900),
        }
        for caso, resultado in casos.items():
            with self.subTest(caso=caso):
                self.assertEqual(resultado, (0, "", ""))


class PerguntarAntes(unittest.TestCase):

    def decisao(self, saida):
        return json.loads(saida)["hookSpecificOutput"]

    def test_push_devolve_a_decisao_ask(self):
        codigo, saida, _ = correr("perguntar_antes", "Bash", command="git push origin exp/a")
        self.assertEqual(codigo, 0)
        self.assertEqual(self.decisao(saida)["permissionDecision"], "ask")

    def test_editar_as_regras_do_agente_tambem_pergunta(self):
        _, saida, _ = correr("perguntar_antes", "Edit", file_path=str(RAIZ / ".claude" / "settings.json"))
        self.assertIn(".claude/settings.json", self.decisao(saida)["permissionDecisionReason"])

    def test_sem_motivo_nao_diz_nada(self):
        self.assertEqual(correr("perguntar_antes", "Bash", command="git status"), (0, "", ""))
        self.assertEqual(correr("perguntar_antes", "Write", file_path=str(RAIZ / "README.md")), (0, "", ""))


if __name__ == "__main__":
    unittest.main()
