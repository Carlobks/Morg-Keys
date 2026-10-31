"""Changelog por fragmentos (scripts/changelog/juntar_changelog.py, ML13; Keep a Changelog 1.1.0 e towncrier).

Cada mudança que se vê de fora leva um ficheiro changelog.d/AAAA-MM-DD-assunto.md: a primeira linha diz a
categoria, depois uma linha em branco e os itens começados por "- ". O script junta-os no CHANGELOG.md na hora
de lançar uma versão e apaga-os; com --rascunho só mostra.
"""

import io
import tempfile
import unittest
from datetime import date
from pathlib import Path
from unittest import mock

from carregar_por_caminho import PASTA_CHANGELOG, RAIZ, carregar_changelog, correr_como_script

changelog = carregar_changelog()
INICIO = "# Changelog\n\nIntrodução.\n"


class Fragmento(unittest.TestCase):

    def test_le_a_categoria_e_os_itens(self):
        texto = "Categoria: Corrigido\n\n- A barra já não salta.\n  Continua aqui.\n- Outro.\n"
        self.assertEqual(changelog.ler_fragmento(texto),
                         ("Corrigido", ["- A barra já não salta.", "  Continua aqui.", "- Outro."]))

    def test_linhas_vazias_no_fim_nao_contam(self):
        self.assertEqual(changelog.ler_fragmento("Categoria: Removido\n\n- Saiu.\n\n\n"), ("Removido", ["- Saiu."]))

    def test_recusa_o_que_esta_mal(self):
        casos = {
            "": "Categoria:",
            "Corrigido\n\n- x\n": "Categoria:",
            "Categoria: Arranjado\n\n- x\n": "Arranjado",
            "Categoria: Corrigido\n- x\n": "linha em branco",
            "Categoria: Corrigido\n\n": "itens",
            "Categoria: Corrigido\n\nTexto solto.\n": "- ",
            "Categoria: Corrigido\n\n- x\n\n- y\n": "- ",
        }
        for texto, motivo in casos.items():
            with self.subTest(texto=texto), self.assertRaises(ValueError) as erro:
                changelog.ler_fragmento(texto)
            self.assertIn(motivo, str(erro.exception))

    def test_as_categorias_seguem_a_ordem_do_keep_a_changelog(self):
        self.assertEqual(changelog.CATEGORIAS,
                         ("Adicionado", "Alterado", "Obsoleto", "Removido", "Corrigido", "Segurança"))


class Pasta(unittest.TestCase):

    def setUp(self):
        pasta = tempfile.TemporaryDirectory()
        self.addCleanup(pasta.cleanup)
        self.raiz = Path(pasta.name)
        self.fragmentos = self.raiz / "changelog.d"
        self.fragmentos.mkdir()

    def escrever(self, nome, texto):
        (self.fragmentos / nome).write_bytes(texto.encode("utf-8"))

    def test_nomes_e_conteudos_errados_sao_apontados(self):
        self.escrever("README.md", "Explicação, ignorada.\n")
        self.escrever("2026-10-31-barra.md", "Categoria: Alterado\n\n- x\n")
        self.escrever("barra.md", "Categoria: Alterado\n\n- x\n")
        self.escrever("2026-10-31-Barra_Nova.md", "Categoria: Alterado\n\n- x\n")
        self.escrever("2026-10-31-mau.md", "Categoria: Nada\n\n- x\n")
        erros = changelog.erros_da_pasta(self.fragmentos)
        self.assertEqual(len(erros), 3)
        self.assertTrue(erros[0].startswith("2026-10-31-Barra_Nova.md: o nome"))
        self.assertTrue(erros[1].startswith("2026-10-31-mau.md: "))
        self.assertTrue(erros[2].startswith("barra.md: o nome"))

    def test_juntar_escreve_a_versao_por_categoria_e_apaga_os_fragmentos(self):
        (self.raiz / "CHANGELOG.md").write_bytes((INICIO + "\n## [0.1.0] - 2026-10-01\n\n- Antigo.\n").encode())
        self.escrever("README.md", "Fica.\n")
        self.escrever("2026-10-30-b.md", "Categoria: Corrigido\n\n- Correção.\n")
        self.escrever("2026-10-29-a.md", "Categoria: Adicionado\n\n- Novo A.\n")
        self.escrever("2026-10-31-c.md", "Categoria: Adicionado\n\n- Novo C.\n")
        codigo, texto = changelog.juntar(self.raiz, "0.2.0", date(2026, 10, 31))
        self.assertEqual(codigo, 0)
        secao = ("## [0.2.0] - 2026-10-31\n\n### Adicionado\n\n- Novo A.\n- Novo C.\n\n"
                 "### Corrigido\n\n- Correção.\n")
        self.assertEqual(texto, secao)
        escrito = (self.raiz / "CHANGELOG.md").read_bytes().decode()
        self.assertEqual(escrito, INICIO + "\n" + secao + "\n## [0.1.0] - 2026-10-01\n\n- Antigo.\n")
        self.assertEqual([p.name for p in self.fragmentos.iterdir()], ["README.md"])

    def test_a_primeira_versao_vai_para_o_fim(self):
        (self.raiz / "CHANGELOG.md").write_bytes(INICIO.encode())
        self.escrever("2026-10-31-a.md", "Categoria: Removido\n\n- Saiu.\n")
        changelog.juntar(self.raiz, "0.1.0", date(2026, 10, 31))
        self.assertEqual((self.raiz / "CHANGELOG.md").read_bytes().decode(),
                         INICIO + "\n## [0.1.0] - 2026-10-31\n\n### Removido\n\n- Saiu.\n")

    def test_rascunho_so_mostra(self):
        (self.raiz / "CHANGELOG.md").write_bytes(INICIO.encode())
        self.escrever("2026-10-31-a.md", "Categoria: Removido\n\n- Saiu.\n")
        codigo, texto = changelog.juntar(self.raiz, "0.1.0", date(2026, 10, 31), rascunho=True)
        self.assertEqual(codigo, 0)
        self.assertIn("- Saiu.", texto)
        self.assertEqual((self.raiz / "CHANGELOG.md").read_bytes().decode(), INICIO)
        self.assertTrue((self.fragmentos / "2026-10-31-a.md").exists())

    def test_sem_fragmentos_ou_com_erros_nao_mexe_em_nada(self):
        (self.raiz / "CHANGELOG.md").write_bytes(INICIO.encode())
        self.assertEqual(changelog.juntar(self.raiz, "0.1.0", date(2026, 10, 31)),
                         (1, "Não há fragmentos em changelog.d/ para juntar."))
        self.escrever("2026-10-31-a.md", "Categoria: Nada\n\n- x\n")
        codigo, texto = changelog.juntar(self.raiz, "0.1.0", date(2026, 10, 31))
        self.assertEqual(codigo, 1)
        self.assertIn("2026-10-31-a.md", texto)
        self.assertEqual((self.raiz / "CHANGELOG.md").read_bytes().decode(), INICIO)

    def test_main_mostra_o_uso_e_escreve_nos_canais_certos(self):
        (self.raiz / "CHANGELOG.md").write_bytes(INICIO.encode())
        self.escrever("2026-10-31-a.md", "Categoria: Removido\n\n- Saiu.\n")
        for argv, esperado in ((["j.py"], 2), (["j.py", "0.1.0", "--outra"], 2),
                               (["j.py", "0.1.0", "--rascunho"], 0), (["j.py", "0.1.0"], 0), (["j.py", "0.2.0"], 1)):
            with self.subTest(argv=argv):
                codigo, _, erro = self.correr_main(argv)
                self.assertEqual(codigo, esperado)
                self.assertEqual(bool(erro), esperado != 0)

    def correr_main(self, argv):
        """(código, stdout, stderr) com os canais numa consola cp1252, como a do Windows por um pipe."""
        saida = io.TextIOWrapper(io.BytesIO(), encoding="cp1252")
        erro = io.TextIOWrapper(io.BytesIO(), encoding="cp1252")
        with mock.patch("sys.stdout", saida), mock.patch("sys.stderr", erro):
            codigo = changelog.main(argv, self.raiz, lambda: date(2026, 10, 31))
        saida.flush()
        erro.flush()
        return codigo, saida.buffer.getvalue().decode("utf-8"), erro.buffer.getvalue().decode("utf-8")

    def test_caracteres_fora_do_cp1252_saem_em_utf8(self):
        # O "✻" do fragmento da quota rebentava o print numa consola cp1252 (A16).
        (self.raiz / "CHANGELOG.md").write_bytes(INICIO.encode())
        self.escrever("2026-10-31-a.md", "Categoria: Adicionado\n\n- O ✻ da barra.\n")
        self.assertIn("- O ✻ da barra.", self.correr_main(["j.py", "0.1.0", "--rascunho"])[1])
        self.escrever("2026-10-31-b.md", "Categoria: ✻\n\n- x\n")
        self.assertIn("categoria desconhecida: ✻", self.correr_main(["j.py", "0.1.0"])[2])


class FragmentosDoRepositorio(unittest.TestCase):

    def test_cada_fragmento_esta_certo(self):
        self.assertEqual(changelog.erros_da_pasta(RAIZ / "changelog.d"), [])

    def test_ha_um_changelog_com_a_introducao(self):
        texto = (RAIZ / "CHANGELOG.md").read_bytes().decode("utf-8")
        self.assertTrue(texto.startswith("# Changelog\n"))
        self.assertIn("changelog.d/", texto)

    def test_o_rascunho_corre_como_script(self):
        with mock.patch("sys.argv", ["juntar_changelog.py", "0.0.0", "--rascunho"]):
            codigo, saida, erro = correr_como_script(PASTA_CHANGELOG / "juntar_changelog.py", b"")
        self.assertEqual((codigo, erro), (0, ""))
        self.assertIn("## [0.0.0]", saida)


if __name__ == "__main__":
    unittest.main()
