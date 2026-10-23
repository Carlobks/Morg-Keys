"""Proteção contra ficheiros de texto estragados por substituições em massa.

Regressão de 2026-10-23 (commit dc975df): um script de substituição trocou cada
quebra de linha do Tutorial.html por uma frase; o ficheiro ficou numa só linha
de 65 000 caracteres e foi publicado assim. Estes testes falham nesse caso.

Correr: py -I -m unittest discover -s tests -v   (na raiz do repositório)
"""

import subprocess
import unittest
from pathlib import Path

RAIZ_REPOSITORIO = Path(__file__).resolve().parent.parent
# Ficheiros gerados por outras ferramentas (não editados à mão) e binários.
CAMINHOS_EXCLUIDOS = ("vendor/",)
EXTENSOES_BINARIAS = (".ttf", ".png", ".bmp", ".ico", ".exe")
MAIOR_LINHA_ACEITE = 2000  # o Tutorial tem linhas de ~650 caracteres; 2000 dá folga


def ficheiros_de_texto_rastreados():
    """Caminhos (relativos) dos ficheiros de texto que o git guarda."""
    saida = subprocess.run(["git", "ls-files"], cwd=RAIZ_REPOSITORIO, capture_output=True,
                           text=True, encoding="utf-8", check=True).stdout
    return [caminho for caminho in saida.splitlines()
            if not caminho.endswith(EXTENSOES_BINARIAS)
            and not any(excluido in caminho for excluido in CAMINHOS_EXCLUIDOS)]


class FicheirosDeTextoIntactos(unittest.TestCase):

    def test_ha_ficheiros_para_verificar(self):
        self.assertGreater(len(ficheiros_de_texto_rastreados()), 20)

    def test_cada_ficheiro_tem_varias_linhas(self):
        for caminho in ficheiros_de_texto_rastreados():
            with self.subTest(ficheiro=caminho):
                texto = (RAIZ_REPOSITORIO / caminho).read_text(encoding="utf-8-sig")
                self.assertGreaterEqual(texto.count("\n"), 2, "sem quebras de linha: foi estragado?")

    def test_nenhuma_linha_e_absurdamente_longa(self):
        for caminho in ficheiros_de_texto_rastreados():
            with self.subTest(ficheiro=caminho):
                texto = (RAIZ_REPOSITORIO / caminho).read_text(encoding="utf-8-sig")
                maior = max((len(linha) for linha in texto.splitlines()), default=0)
                self.assertLessEqual(maior, MAIOR_LINHA_ACEITE, f"linha com {maior} caracteres")


if __name__ == "__main__":
    unittest.main()
