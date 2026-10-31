"""A versão do Morg Keys (ADR 0011): o VERSION é a única fonte e bate com o CHANGELOG.md e as tags.

- o VERSION segue o SemVer (MAIOR.MENOR.CORREÇÃO) e é igual à secção mais recente do CHANGELOG.md; antes do 1.º
  lançamento não há nem VERSION nem secções;
- as versões do CHANGELOG.md só descem de cima para baixo e não se repetem (catraca: uma versão nunca volta atrás);
- cada tag local v* tem a sua secção no CHANGELOG.md.
"""

import re
import subprocess
import unittest
from itertools import pairwise

from carregar_por_caminho import RAIZ, carregar_changelog

changelog = carregar_changelog()
SECCAO = re.compile(r"^## \[([^\]]+)\] - \d{4}-\d{2}-\d{2}$", re.MULTILINE)


def versoes_do_changelog(texto):
    """As versões das secções, de cima para baixo."""
    return SECCAO.findall(texto)


def ordem_das_versoes(versoes):
    """Os motivos para recusar a lista (vazia se cada versão for SemVer e menor do que a de cima)."""
    motivos = [f"{v}: não é MAIOR.MENOR.CORREÇÃO" for v in versoes if not changelog.SEMVER.match(v)]
    certas = [v for v in versoes if changelog.SEMVER.match(v)]
    motivos += [f"{baixo} vem depois de {cima}, mas não é menor" for cima, baixo in pairwise(certas)
                if changelog.numeros(baixo) >= changelog.numeros(cima)]
    return motivos


class OrdemDasVersoes(unittest.TestCase):

    def test_apanha_versoes_fora_de_ordem_repetidas_ou_mal_escritas(self):
        self.assertEqual(ordem_das_versoes(["0.10.0", "0.9.1", "0.2.0"]), [])
        self.assertEqual(ordem_das_versoes(["0.2.0", "0.2.0"]), ["0.2.0 vem depois de 0.2.0, mas não é menor"])
        self.assertEqual(ordem_das_versoes(["0.1.0", "0.2.0"]), ["0.2.0 vem depois de 0.1.0, mas não é menor"])
        self.assertEqual(ordem_das_versoes(["v1.0", "0.1.0"]), ["v1.0: não é MAIOR.MENOR.CORREÇÃO"])

    def test_le_as_seccoes_do_changelog(self):
        texto = "# Changelog\n\n## [0.2.0] - 2026-11-02\n\n### Corrigido\n\n- x\n\n## [0.1.0] - 2026-10-31\n"
        self.assertEqual(versoes_do_changelog(texto), ["0.2.0", "0.1.0"])


class VersaoDoRepositorio(unittest.TestCase):

    def setUp(self):
        self.versoes = versoes_do_changelog((RAIZ / "CHANGELOG.md").read_bytes().decode("utf-8"))
        ficheiro = RAIZ / "VERSION"
        self.version = ficheiro.read_bytes().decode("utf-8").strip() if ficheiro.exists() else None

    def test_version_igual_a_versao_mais_recente(self):
        if not self.versoes:
            self.assertIsNone(self.version, "há VERSION mas o CHANGELOG.md ainda não tem versões")
            return
        self.assertIsNotNone(self.version, "o CHANGELOG.md tem versões mas falta o VERSION")
        self.assertRegex(self.version, changelog.SEMVER)
        self.assertEqual(self.version, self.versoes[0])

    def test_versoes_so_descem_e_nao_se_repetem(self):
        self.assertEqual(ordem_das_versoes(self.versoes), [])

    def test_cada_tag_tem_a_sua_seccao(self):
        tags = subprocess.run(["git", "tag", "--list", "v*"], cwd=RAIZ, capture_output=True, text=True,
                              encoding="utf-8", check=True).stdout.split()
        self.assertEqual([t for t in tags if t[1:] not in self.versoes], [])


if __name__ == "__main__":
    unittest.main()
