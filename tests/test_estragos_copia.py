"""Os estragos (scripts/estragos.py) correm numa cópia do repositório, nunca no disco partilhado (ML16, M4).

Na 2.ª verificação, durante os ~10 min dos estragos, cada ficheiro do pack ficou estragado no disco: outra sessão
que corresse os testes via-os falhar, e uma que commitasse esse ficheiro por caminho podia levar o mutante. Agora
o estragos.py faz um `git worktree add --detach` numa pasta temporária, trabalha lá e remove-a no fim, também se
rebentar. Importá-lo já não corre nada (antes mudava de pasta e corria a bateria ao ser carregado).
"""

import ast
import importlib.util
import os
import tempfile
import unittest
from pathlib import Path
from unittest import mock

from carregar_por_caminho import RAIZ

ESTRAGOS = RAIZ / "scripts" / "estragos.py"


def carregar():
    especificacao = importlib.util.spec_from_file_location("estragos", ESTRAGOS)
    modulo = importlib.util.module_from_spec(especificacao)
    especificacao.loader.exec_module(modulo)
    return modulo


class SemEfeitosAoImportar(unittest.TestCase):

    def test_so_ha_definicoes_no_topo(self):
        # Verificado pela árvore, sem importar: a versão antiga corria a bateria inteira ao ser importada.
        permitidos = (ast.Import, ast.ImportFrom, ast.Assign, ast.FunctionDef, ast.Expr, ast.If)
        for no in ast.parse(ESTRAGOS.read_text(encoding="utf-8")).body:
            with self.subTest(linha=no.lineno):
                self.assertIsInstance(no, permitidos)
                if isinstance(no, ast.If):
                    self.assertIn("__main__", ast.unparse(no.test))
                if isinstance(no, ast.Expr):
                    self.assertIsInstance(no.value, ast.Constant)  # só a docstring


class Copia(unittest.TestCase):

    def setUp(self):
        SemEfeitosAoImportar("test_so_ha_definicoes_no_topo").test_so_ha_definicoes_no_topo()
        self.estragos = carregar()
        self.correr = mock.Mock()

    def test_a_copia_e_um_worktree_fora_do_repositorio(self):
        with self.estragos.copia_do_repositorio(self.correr) as pasta:
            adicionar = self.correr.call_args_list[0].args[0]
            self.assertEqual(adicionar[:4], ["git", "-C", str(self.estragos.RAIZ), "worktree"])
            self.assertIn("--detach", adicionar)
            self.assertEqual(adicionar[-2:], [str(pasta), "HEAD"])
            self.assertNotEqual(pasta.resolve(), RAIZ)
            self.assertFalse(pasta.resolve().is_relative_to(RAIZ))
        remover = self.correr.call_args_list[-1].args[0]
        self.assertEqual(remover[3:6], ["worktree", "remove", "--force"])

    def test_remove_a_copia_tambem_se_rebentar(self):
        with self.assertRaises(RuntimeError), self.estragos.copia_do_repositorio(self.correr) as pasta:
            raise RuntimeError
        self.assertIn(str(pasta), self.correr.call_args_list[-1].args[0])
        self.assertFalse(pasta.parent.exists())

    def test_main_trabalha_dentro_da_copia_e_volta(self):
        antes = os.getcwd()
        with tempfile.TemporaryDirectory() as temporaria:
            vista = []
            copia = mock.MagicMock()
            copia.return_value.__enter__.return_value = Path(temporaria)
            with mock.patch.object(self.estragos, "copia_do_repositorio", copia), \
                    mock.patch.object(self.estragos, "correr_estragos", lambda: vista.append(os.getcwd()) or 0):
                self.assertEqual(self.estragos.main(), 0)
            self.assertEqual(Path(vista[0]).resolve(), Path(temporaria).resolve())
        self.assertEqual(os.getcwd(), antes)


if __name__ == "__main__":
    unittest.main()
