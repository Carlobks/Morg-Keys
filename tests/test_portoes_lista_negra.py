"""Portão da lista negra (scripts/portoes/lista_negra.py): os dados pessoais nunca entram num commit.

A lista fica fora do repositório (git config morg.listaNegra); os termos destes testes são fictícios.
"""

import io
import runpy
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from carregar_por_caminho import PASTA_PORTOES, carregar_portao

lista_negra = carregar_portao("lista_negra")


def stderr_falso():
    """stderr com .buffer, como o real (o portão escreve os bytes em UTF-8)."""
    return io.TextIOWrapper(io.BytesIO(), encoding="utf-8")


def texto_do(falso):
    falso.flush()
    return falso.buffer.getvalue().decode("utf-8")


class ListaEmFicheiro(unittest.TestCase):

    def setUp(self):
        self.pasta = tempfile.TemporaryDirectory()
        self.addCleanup(self.pasta.cleanup)
        self.lista = Path(self.pasta.name) / "lista.txt"
        self.lista.write_bytes("﻿# comentário\n\n  Zacarias  \nempresa-ficticia\n".encode())


class Termos(ListaEmFicheiro):

    def test_le_termos_sem_comentarios_linhas_vazias_nem_bom(self):
        self.assertEqual(lista_negra.ler_termos(self.lista), ["Zacarias", "empresa-ficticia"])

    def test_encontra_palavra_inteira_sem_olhar_a_maiusculas(self):
        self.assertEqual(lista_negra.termos_encontrados("olá ZACARIAS!", ["Zacarias", "outro"]), ["Zacarias"])

    def test_nao_encontra_dentro_de_outra_palavra(self):
        self.assertEqual(lista_negra.termos_encontrados("Zacariasinho", ["Zacarias"]), [])


class CaminhoDaLista(unittest.TestCase):

    def test_sem_configuracao_nao_ha_lista(self):
        correr = mock.Mock(return_value=SimpleNamespace(stdout="\n"))
        self.assertIsNone(lista_negra.caminho_da_lista(correr))
        self.assertEqual(correr.call_args.args[0], ["git", "config", "--get", "morg.listaNegra"])

    def test_com_configuracao_expande_a_pasta_pessoal(self):
        correr = mock.Mock(return_value=SimpleNamespace(stdout="~/lista.txt\n"))
        self.assertEqual(lista_negra.caminho_da_lista(correr), Path.home() / "lista.txt")


class Verificar(ListaEmFicheiro):

    def test_sem_lista_avisa_e_deixa_passar(self):
        codigo, mensagem = lista_negra.verificar("Zacarias", "a mensagem", None)
        self.assertEqual(codigo, 0)
        self.assertIn("AVISO", mensagem)

    def test_lista_configurada_mas_em_falta_recusa(self):
        codigo, mensagem = lista_negra.verificar("texto", "a mensagem", self.lista.with_name("nao-existe.txt"))
        self.assertEqual(codigo, 1)
        self.assertIn("não existe", mensagem)

    def test_termo_encontrado_recusa_e_diz_qual(self):
        codigo, mensagem = lista_negra.verificar("feito por zacarias", "a mensagem", self.lista)
        self.assertEqual(codigo, 1)
        self.assertIn("a mensagem", mensagem)
        self.assertIn("Zacarias", mensagem)

    def test_texto_limpo_passa_sem_mensagem(self):
        self.assertEqual(lista_negra.verificar("feito pela Ana", "a mensagem", self.lista), (0, ""))


class PontoDeEntrada(ListaEmFicheiro):

    def correr_main(self, texto, argv=("lista_negra.py", "os ficheiros")):
        falso = stderr_falso()
        with mock.patch.object(lista_negra, "caminho_da_lista", return_value=self.lista), \
                mock.patch("sys.stderr", falso):
            codigo = lista_negra.main(list(argv), io.BytesIO(texto.encode()))
        return codigo, texto_do(falso)

    def test_recusa_com_o_rotulo_e_acentos_em_utf8(self):
        codigo, erro = self.correr_main("linha do Zacarias")
        self.assertEqual(codigo, 1)
        self.assertIn("há dados da lista negra (os ficheiros): Zacarias", erro)

    def test_passa_calado_sem_termos(self):
        self.assertEqual(self.correr_main("nada a ver", ("lista_negra.py",)), (0, ""))

    def test_corre_como_script(self):
        correr = mock.Mock(return_value=SimpleNamespace(stdout=str(self.lista)))
        entrada = io.TextIOWrapper(io.BytesIO(b"o Zacarias"), encoding="utf-8")
        with mock.patch("subprocess.run", correr), mock.patch("sys.stdin", entrada), \
                mock.patch("sys.stderr", stderr_falso()), mock.patch("sys.argv", ["lista_negra.py", "x"]), \
                self.assertRaises(SystemExit) as saida:
            runpy.run_path(str(PASTA_PORTOES / "lista_negra.py"), run_name="__main__")
        self.assertEqual(saida.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
