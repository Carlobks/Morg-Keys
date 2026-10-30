"""Portão da identidade (scripts/portoes/identidade.py): o e-mail e o nome de cada commit são públicos."""

import io
import runpy
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from carregar_por_caminho import PASTA_PORTOES, carregar_portao

identidade = carregar_portao("identidade")
NOREPLY = "123+conta-ficticia@users.noreply.github.com"


class Erros(unittest.TestCase):

    def setUp(self):
        pasta = tempfile.TemporaryDirectory()
        self.addCleanup(pasta.cleanup)
        self.lista = Path(pasta.name) / "lista.txt"
        self.lista.write_text("Zacarias\n", encoding="utf-8")

    def test_noreply_e_nome_limpo_passam(self):
        self.assertEqual(identidade.erros(NOREPLY, "Ana", self.lista), [])

    def test_outro_email_e_recusado(self):
        erros = identidade.erros("ana@example.com", "Ana", self.lista)
        self.assertEqual(len(erros), 1)
        self.assertIn("noreply", erros[0])

    def test_nome_da_lista_negra_e_recusado(self):
        erros = identidade.erros(NOREPLY, "Zacarias Silva", self.lista)
        self.assertEqual(len(erros), 1)
        self.assertIn("user.name", erros[0])

    def test_sem_lista_so_verifica_o_email(self):
        self.assertEqual(identidade.erros(NOREPLY, "Zacarias", None), [])


class PontoDeEntrada(unittest.TestCase):

    def test_le_a_configuracao_do_git(self):
        correr = mock.Mock(return_value=SimpleNamespace(stdout=" valor \n"))
        self.assertEqual(identidade.ler_config("user.email", correr), "valor")
        self.assertEqual(correr.call_args.args[0], ["git", "config", "--get", "user.email"])

    def correr_main(self, email):
        falso = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
        with mock.patch.object(identidade, "ler_config", side_effect=lambda chave: {"user.email": email}.get(chave, "Ana")), \
                mock.patch.object(identidade.lista_negra, "caminho_da_lista", return_value=None), \
                mock.patch("sys.stderr", falso):
            codigo = identidade.main()
        falso.flush()
        return codigo, falso.buffer.getvalue().decode("utf-8")

    def test_recusa_e_explica(self):
        codigo, erro = self.correr_main("ana@example.com")
        self.assertEqual(codigo, 1)
        self.assertIn("user.email é 'ana@example.com'", erro)

    def test_aceita(self):
        self.assertEqual(self.correr_main(NOREPLY), (0, ""))

    def test_corre_como_script(self):
        respostas = {"user.email": NOREPLY, "user.name": "Ana", "morg.listaNegra": ""}
        correr = mock.Mock(side_effect=lambda comando, **_: SimpleNamespace(stdout=respostas[comando[-1]]))
        with mock.patch("subprocess.run", correr), self.assertRaises(SystemExit) as saida:
            runpy.run_path(str(PASTA_PORTOES / "identidade.py"), run_name="__main__")
        self.assertEqual(saida.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
