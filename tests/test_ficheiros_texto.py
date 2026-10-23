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
LIMITE_DE_LINHAS = 500  # regra do CLAUDE.md: ficheiros pequenos, uma responsabilidade cada
# Textos de terceiros que não se dividem.
SEM_LIMITE_DE_LINHAS = ("LICENSE",)
# Ficheiros antigos acima do limite, com o tamanho que tinham em 2026-10-23: só podem encolher.
# A fase 2 da experiência 0001 divide-os; quando um descer das 500 linhas, sai desta lista.
GRANDES_POR_DIVIDIR = {
    "2-configuracao/glzr/zebar/omarchy-catppuccin/bar_helper.py": 1982,
    "2-configuracao/glzr/zebar/omarchy-catppuccin/painel/apps.html": 830,
    "2-configuracao/glzr/zebar/omarchy-catppuccin/guia/guia.html": 622,
}


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

    def test_sem_caracteres_de_controlo(self):
        # Regressão de 2026-10-23: texto escrito por uma string "…" do PowerShell perdeu as crases e
        # transformou `a / `v / `0 em caracteres invisíveis (campainha, tabulação vertical, nulo) — A28.
        proibidos = {chr(c) for c in range(32)} - {"\n", "\r", "\t"}
        for caminho in ficheiros_de_texto_rastreados():
            with self.subTest(ficheiro=caminho):
                texto = (RAIZ_REPOSITORIO / caminho).read_text(encoding="utf-8-sig")
                encontrados = sorted({hex(ord(c)) for c in texto if c in proibidos})
                self.assertEqual(encontrados, [], "caracteres de controlo no ficheiro")

    def test_nenhuma_linha_e_absurdamente_longa(self):
        for caminho in ficheiros_de_texto_rastreados():
            with self.subTest(ficheiro=caminho):
                texto = (RAIZ_REPOSITORIO / caminho).read_text(encoding="utf-8-sig")
                maior = max((len(linha) for linha in texto.splitlines()), default=0)
                self.assertLessEqual(maior, MAIOR_LINHA_ACEITE, f"linha com {maior} caracteres")


    def test_nenhum_ficheiro_passa_o_limite_de_linhas(self):
        # Apanha também o que escapa ao hook .claude/hooks/limite_de_linhas.py (edições feitas pela shell).
        for caminho in ficheiros_de_texto_rastreados():
            if caminho in SEM_LIMITE_DE_LINHAS:
                continue
            with self.subTest(ficheiro=caminho):
                linhas = len((RAIZ_REPOSITORIO / caminho).read_text(encoding="utf-8-sig").splitlines())
                maximo = GRANDES_POR_DIVIDIR.get(caminho, LIMITE_DE_LINHAS)
                self.assertLessEqual(linhas, maximo, f"{linhas} linhas (máximo {maximo})")

    def test_lista_de_grandes_esta_atualizada(self):
        for caminho in GRANDES_POR_DIVIDIR:
            with self.subTest(ficheiro=caminho):
                linhas = len((RAIZ_REPOSITORIO / caminho).read_text(encoding="utf-8-sig").splitlines())
                self.assertGreater(linhas, LIMITE_DE_LINHAS, "já cabe no limite: tirar de GRANDES_POR_DIVIDIR")


if __name__ == "__main__":
    unittest.main()
