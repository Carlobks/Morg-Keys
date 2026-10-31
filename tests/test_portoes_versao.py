"""Portão da versão (scripts/portoes/versao_lancada.py, ADR 0011): uma versão lançada não muda e o VERSION só muda
no lançamento, na mesma corrida do juntar_changelog.py que escreve a secção nova no topo do CHANGELOG.md."""

import io
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from carregar_por_caminho import carregar_portao

versao = carregar_portao("versao_lancada")
mensagem = carregar_portao("mensagem_commit")
INTRO = "# Changelog\n\nIntrodução.\n"
V010 = "\n## [0.1.0] - 2026-10-31\n\n### Corrigido\n\n- Uma correção.\n"
V020 = "\n## [0.2.0] - 2026-11-02\n\n### Adicionado\n\n- Uma novidade.\n"
DOCS = "docs: título\n"


class VersaoLancadaNaoMuda(unittest.TestCase):

    def test_acrescentar_uma_versao_no_topo_passa(self):
        self.assertEqual(versao.erros(DOCS, ["CHANGELOG.md", "VERSION"], INTRO + V010, INTRO + V020 + V010, "0.2.0"),
                         [])

    def test_mudar_a_introducao_passa(self):
        self.assertEqual(versao.erros(DOCS, ["CHANGELOG.md"], INTRO + V010, "# Changelog\n\nOutra.\n" + V010, None),
                         [])

    def test_mudar_uma_versao_lancada_pede_o_motivo(self):
        mudado = INTRO + V010.replace("Uma correção", "Outra correção")
        for depois in (mudado, INTRO, INTRO + V020):
            with self.subTest(depois=depois):
                motivos = versao.erros(DOCS, ["CHANGELOG.md"], INTRO + V010, depois, None)
                self.assertEqual(len(motivos), 1)
                self.assertIn("Changelog-corrigido", motivos[0])
        self.assertEqual(versao.erros(DOCS + "\nChangelog-corrigido: erro de escrita\n", ["CHANGELOG.md"],
                                      INTRO + V010, mudado, None), [])
        self.assertEqual(len(versao.erros(DOCS + "\nChangelog-corrigido: \n", ["CHANGELOG.md"], INTRO + V010, mudado,
                                          None)), 1)

    def test_sem_versoes_lancadas_tudo_pode_mudar(self):
        self.assertEqual(versao.erros(DOCS, ["CHANGELOG.md"], INTRO, "# Outro\n", None), [])


class VersionSoNoLancamento(unittest.TestCase):

    def test_o_primeiro_lancamento_passa(self):
        self.assertEqual(versao.erros(DOCS, ["CHANGELOG.md", "VERSION"], INTRO, INTRO + V010, "0.1.0"), [])

    def test_version_mudado_a_mao_e_recusado(self):
        casos = [
            (INTRO + V010, "0.2.0"),  # sem a secção nova
            (INTRO + V010, "0.1.0"),  # a secção já estava lançada
            (INTRO + V020 + V010, "0.3.0"),  # o topo não é a versão do VERSION
            (INTRO + V020 + V010, None),  # o VERSION foi apagado
        ]
        for depois, nova in casos:
            with self.subTest(nova=nova):
                motivos = versao.erros(DOCS, ["VERSION"], INTRO + V010, depois, nova)
                self.assertEqual(len(motivos), 1)
                self.assertIn("juntar_changelog.py", motivos[0])

    def test_outros_ficheiros_nao_pedem_nada(self):
        self.assertEqual(versao.erros(DOCS, ["a.py"], INTRO + V010, INTRO, "9.9.9"), [])


class LeDoGit(unittest.TestCase):

    def test_le_o_ultimo_commit_e_o_indice(self):
        respostas = {"HEAD:CHANGELOG.md": (0, INTRO + V010), ":CHANGELOG.md": (0, INTRO + V020 + V010),
                     ":VERSION": (0, "0.2.0\n")}

        def correr(comando, **_):
            codigo, saida = respostas.get(comando[2], (128, ""))
            return SimpleNamespace(returncode=codigo, stdout=saida)

        self.assertEqual(versao.erros_do_commit(DOCS, ["CHANGELOG.md", "VERSION"], correr), [])
        respostas[":VERSION"] = (128, "")  # o VERSION apagado no commit
        self.assertEqual(len(versao.erros_do_commit(DOCS, ["CHANGELOG.md", "VERSION"], correr)), 1)

    def test_sem_changelog_nem_version_nao_pergunta_ao_git(self):
        correr = mock.Mock()
        self.assertEqual(versao.erros_do_commit(DOCS, ["a.py", "tests/b.py"], correr), [])
        correr.assert_not_called()

    def test_o_commit_msg_usa_este_portao(self):
        with tempfile.TemporaryDirectory() as pasta:
            ficheiro = Path(pasta) / "COMMIT_EDITMSG"
            ficheiro.write_bytes(DOCS.encode())
            falso = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
            with mock.patch.object(mensagem, "ficheiros_do_commit", return_value=["VERSION"]), \
                    mock.patch.object(mensagem, "testes_com_linhas_tiradas", return_value=[]), \
                    mock.patch.object(mensagem.versao_lancada, "erros_do_commit", return_value=["ERRO: à mão"]), \
                    mock.patch("sys.stderr", falso):
                self.assertEqual(mensagem.main(["m.py", str(ficheiro)]), 1)
            falso.flush()
            self.assertIn("ERRO: à mão", falso.buffer.getvalue().decode("utf-8"))

    def test_changelog_corrigido_e_rodape_e_nao_conta_como_corpo(self):
        motivos = mensagem.erros("fix: t\n\nChangelog-corrigido: erro de escrita\n", ["tests/a.py"])
        self.assertEqual(motivos, ["ERRO: um commit fix leva corpo com o que mudou e porquê."])


if __name__ == "__main__":
    unittest.main()
