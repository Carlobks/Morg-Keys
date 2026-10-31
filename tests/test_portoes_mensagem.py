"""Portão da mensagem do commit (scripts/portoes/mensagem_commit.py): formato do Morg Laws (git-e-commits).

Título `tipo(área): …` com até 72 caracteres e sem ponto final; linha em branco; corpo com o porquê em
fix/feat/refactor; um fix sem ficheiro em tests/ leva `Sem-teste: <motivo>`; um feat ou fix que mexa no que se
instala leva um fragmento em changelog.d/ ou `Sem-changelog: <motivo>`.
"""

import io
import runpy
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from carregar_por_caminho import PASTA_PORTOES, carregar_portao

mensagem = carregar_portao("mensagem_commit")
CORPO = "\n\nO que mudou e porquê.\n\nCo-Authored-By: Claude <noreply@anthropic.com>\n"
# Mexe no instalador: leva o teste e o fragmento do changelog.
COM_TESTE = ["scripts/instalar.ps1", "tests/instalar.Tests.ps1", "changelog.d/2026-10-31-instalador.md"]


class Titulo(unittest.TestCase):

    def test_formatos_aceites(self):
        for titulo in ("docs(morg-laws): plano 01", "fix: sem área", "chore(ci): versões fixas"):
            with self.subTest(titulo=titulo):
                self.assertEqual(mensagem.erros(titulo + CORPO, COM_TESTE), [])

    def test_merge_e_revert_passam_como_o_git_os_escreve(self):
        self.assertEqual(mensagem.erros("Merge branch 'main' into exp/a\n", []), [])
        self.assertEqual(mensagem.erros('Revert "feat: x"\n\nThis reverts commit abc.\n', []), [])

    def test_sem_tipo_e_recusado(self):
        erros = mensagem.erros("Instalador: só reinicia o Explorador" + CORPO, [])
        self.assertEqual(len(erros), 1)
        self.assertIn("tipo(área)", erros[0])

    def test_tipo_desconhecido_e_recusado(self):
        self.assertIn("tipo(área)", mensagem.erros("coisa(x): y" + CORPO, [])[0])

    def test_titulo_longo_e_recusado(self):
        erros = mensagem.erros("docs: " + "a" * 67 + CORPO, [])
        self.assertEqual(len(erros), 1)
        self.assertIn("73 caracteres", erros[0])

    def test_ponto_final_e_recusado(self):
        self.assertIn("ponto final", mensagem.erros("docs: frase." + CORPO, [])[0])

    def test_mensagem_vazia_ou_so_comentarios(self):
        self.assertIn("vazia", mensagem.erros("# Please enter the commit message\n\n", [])[0])


class Corpo(unittest.TestCase):

    def test_fix_feat_refactor_exigem_corpo(self):
        for tipo in ("fix", "feat", "refactor"):
            with self.subTest(tipo=tipo):
                erros = mensagem.erros(f"{tipo}(x): y\n\nCo-Authored-By: Claude <noreply@anthropic.com>\n", COM_TESTE)
                self.assertEqual(len(erros), 1)
                self.assertIn("corpo", erros[0])

    def test_docs_pode_ir_sem_corpo(self):
        self.assertEqual(mensagem.erros("docs: só o título\n", []), [])

    def test_falta_a_linha_em_branco_depois_do_titulo(self):
        self.assertIn("linha em branco", mensagem.erros("docs: x\ncorpo colado\n", [])[0])

    def test_comentarios_do_git_nao_contam(self):
        self.assertEqual(mensagem.erros("docs: x\n# Changes to be committed:\n#\tmodified: a\n", []), [])


class SemTeste(unittest.TestCase):

    def test_fix_sem_ficheiro_de_teste_e_recusado(self):
        erros = mensagem.erros("fix(x): y" + CORPO, ["scripts/portoes/a.py"])
        self.assertEqual(len(erros), 1)
        self.assertIn("Sem-teste:", erros[0])

    def test_fix_sem_teste_com_motivo_passa(self):
        texto = "fix(x): y\n\nPorquê.\n\nSem-teste: só muda os fins de linha\n"
        self.assertEqual(mensagem.erros(texto, ["a.py"]), [])

    def test_sem_teste_sem_motivo_nao_conta(self):
        self.assertIn("Sem-teste:", mensagem.erros("fix(x): y\n\nPorquê.\n\nSem-teste:\n", ["a.py"])[0])

    def test_outros_tipos_nao_precisam_de_teste(self):
        self.assertEqual(mensagem.erros("feat(x): y" + CORPO, ["a.py"]), [])



class SemChangelog(unittest.TestCase):

    def test_feat_ou_fix_no_que_se_instala_sem_fragmento_e_recusado(self):
        for ficheiro in ("2-configuracao/glzr/glazewm/config.yaml", "scripts/instalar.ps1",
                         "scripts/desinstalar.ps1", "INSTALAR.cmd", "DESINSTALAR.cmd"):
            for tipo in ("feat", "fix"):
                with self.subTest(ficheiro=ficheiro, tipo=tipo):
                    erros = mensagem.erros(f"{tipo}(x): y" + CORPO, [ficheiro, "tests/a.py"])
                    self.assertEqual(len(erros), 1)
                    self.assertIn("Sem-changelog:", erros[0])
                    self.assertIn("changelog.d/", erros[0])

    def test_com_fragmento_passa(self):
        ficheiros = ["2-configuracao/a.css", "tests/a.py", "changelog.d/2026-10-31-barra.md"]
        self.assertEqual(mensagem.erros("feat(barra): y" + CORPO, ficheiros), [])

    def test_fragmento_tem_de_ser_md_na_pasta(self):
        ficheiros = ["2-configuracao/a.css", "tests/a.py", "changelog.d/README.txt", "docs/changelog.d/x.md"]
        self.assertEqual(len(mensagem.erros("feat(barra): y" + CORPO, ficheiros)), 1)

    def test_sem_changelog_com_motivo_passa(self):
        texto = "fix(x): y\n\nPorquê.\n\nSem-changelog: só muda um comentário\n"
        self.assertEqual(mensagem.erros(texto, ["2-configuracao/a.py", "tests/a.py"]), [])

    def test_sem_changelog_sem_motivo_nao_conta(self):
        texto = "feat(x): y\n\nPorquê.\n\nSem-changelog:\n"
        self.assertIn("Sem-changelog:", mensagem.erros(texto, ["2-configuracao/a.py"])[0])

    def test_outros_tipos_e_outras_pastas_nao_precisam(self):
        self.assertEqual(mensagem.erros("refactor(x): y" + CORPO, ["2-configuracao/a.py"]), [])
        self.assertEqual(mensagem.erros("docs: y\n", ["2-configuracao/a.md"]), [])
        self.assertEqual(mensagem.erros("feat(portoes): y" + CORPO, ["scripts/portoes/a.py"]), [])


class PontoDeEntrada(unittest.TestCase):

    def setUp(self):
        pasta = tempfile.TemporaryDirectory()
        self.addCleanup(pasta.cleanup)
        self.ficheiro = Path(pasta.name) / "COMMIT_EDITMSG"

    def test_ficheiros_do_commit_vem_do_indice(self):
        correr = mock.Mock(return_value=SimpleNamespace(stdout="a.py\ntests/b.py\n"))
        self.assertEqual(mensagem.ficheiros_do_commit(correr), ["a.py", "tests/b.py"])
        self.assertEqual(correr.call_args.args[0], ["git", "diff", "--cached", "--name-only"])

    def correr_main(self, texto):
        self.ficheiro.write_bytes(texto.encode("utf-8"))
        falso = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
        with mock.patch.object(mensagem, "ficheiros_do_commit", return_value=["a.py"]), mock.patch("sys.stderr", falso):
            codigo = mensagem.main(["mensagem_commit.py", str(self.ficheiro)])
        falso.flush()
        return codigo, falso.buffer.getvalue().decode("utf-8")

    def test_recusa_e_mostra_como_corrigir(self):
        codigo, erro = self.correr_main("Instalador: título à moda antiga\n")
        self.assertEqual(codigo, 1)
        self.assertIn("tipo(área)", erro)
        self.assertIn("Commit recusado", erro)

    def test_aceita_calado(self):
        self.assertEqual(self.correr_main("docs: título\n"), (0, ""))

    def test_corre_como_script(self):
        self.ficheiro.write_bytes(b"docs: x\n")
        correr = mock.Mock(return_value=SimpleNamespace(stdout=""))
        with mock.patch("subprocess.run", correr), mock.patch("sys.argv", ["m.py", str(self.ficheiro)]), \
                self.assertRaises(SystemExit) as saida:
            runpy.run_path(str(PASTA_PORTOES / "mensagem_commit.py"), run_name="__main__")
        self.assertEqual(saida.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
