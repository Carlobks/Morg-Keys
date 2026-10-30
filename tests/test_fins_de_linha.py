"""Fins de linha coerentes com o .gitattributes (regra FINS DE LINHA do CLAUDE.md; armadilhas A27 e A45).

O git guarda todos os ficheiros de texto em LF; no disco ficam em CRLF só os que o Windows corre (.ps1, .psm1,
.cmd, .bat) e em LF todos os outros. Regressão: com `* -text` os fins de linha ficavam como calhava (16 em CRLF,
11 .ps1/.cmd em LF) e já houve 2 incidentes, ex.: o 17ce46f, em que os estragos com "\\n" pareciam escapar.
"""

import subprocess
import unittest

from carregar_por_caminho import RAIZ

EM_CRLF = (".ps1", ".psm1", ".cmd", ".bat")
BINARIOS = (".png", ".ico", ".bmp", ".jpg", ".ttf", ".woff2", ".exe")


def estado_dos_ficheiros():
    """[(índice, disco, atributos, caminho)] de `git ls-files --eol`."""
    saida = subprocess.run(["git", "ls-files", "--eol"], cwd=RAIZ, capture_output=True, text=True,
                           encoding="utf-8", check=True).stdout
    resultado = []
    for linha in saida.splitlines():
        info, caminho = linha.split("\t", 1)
        indice, disco, atributos = info.split(None, 2)
        resultado.append((indice[2:], disco[2:], atributos.strip()[5:], caminho))
    return resultado


class FinsDeLinha(unittest.TestCase):

    def test_ha_ficheiros(self):
        self.assertGreater(len(estado_dos_ficheiros()), 100)

    def test_o_git_guarda_o_texto_em_lf(self):
        errados = [caminho for indice, _, _, caminho in estado_dos_ficheiros()
                   if not caminho.endswith(BINARIOS) and indice != "lf"]
        self.assertEqual(errados, [], "falta normalizar: git add --renormalize -- <ficheiros>")

    def test_no_disco_crlf_so_no_que_o_windows_corre(self):
        errados = [f"{caminho} ({disco})" for _, disco, _, caminho in estado_dos_ficheiros()
                   if not caminho.endswith(BINARIOS) and disco != ("crlf" if caminho.endswith(EM_CRLF) else "lf")]
        self.assertEqual(errados, [])

    def test_atributos_do_gitattributes(self):
        for _, _, atributos, caminho in estado_dos_ficheiros():
            with self.subTest(ficheiro=caminho):
                if caminho.endswith(BINARIOS):
                    self.assertEqual(atributos, "-text", "binário marcado como binary")
                else:
                    esperado = "eol=crlf" if caminho.endswith(EM_CRLF) else "eol=lf"
                    self.assertIn(esperado, atributos)


if __name__ == "__main__":
    unittest.main()
