"""Nomes de ficheiros e pastas que dizem a função (regra NOMES PESQUISÁVEIS do CLAUDE.md; Morg Laws).

Um nome genérico solto (`comum`, `utils`, `helper`…) esconde onde está a lógica e dá dezenas de resultados no grep.
Conta o nome inteiro ou uma parte separada por ponto (`instalar.Comum.ps1`); um nome composto que diz o quê
(`bar_helper.py`, o ajudante da barra) não é solto. Regressão de 2026-10-31 (auditoria Q8 e verificação 01):
`comum/comum.mjs` e `tests/*.Comum.ps1`.
"""

import re
import subprocess
import unittest
from pathlib import PurePosixPath

from carregar_por_caminho import RAIZ

PROIBIDOS = {"comum", "common", "utils", "util", "helper", "helpers", "data", "misc", "tmp", "info", "manager",
             "handler", "stuff", "geral"}


def nomes_proibidos(caminhos):
    """Ficheiros ou pastas cujo nome (ou uma parte separada por ponto) é uma palavra genérica solta."""
    achados = set()
    for caminho in caminhos:
        for parte in PurePosixPath(caminho).parts:
            if PROIBIDOS & {pedaco.lower() for pedaco in parte.split(".")}:
                achados.add(parte)
    return sorted(achados)


class NomesPesquisaveis(unittest.TestCase):

    def test_o_detetor_apanha_os_soltos_e_deixa_os_compostos(self):
        self.assertEqual(nomes_proibidos(["a/comum/x.mjs", "tests/instalar.Comum.ps1", "bar_helper.py", "dados.py"]),
                         ["comum", "instalar.Comum.ps1"])

    def test_nenhum_nome_generico_solto(self):
        caminhos = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=RAIZ,
                                  capture_output=True, text=True, encoding="utf-8", check=True).stdout.splitlines()
        existentes = [caminho for caminho in caminhos if (RAIZ / caminho).exists()]
        self.assertEqual(nomes_proibidos(existentes), [], "dê um nome que diga a função (menos de 5 resultados no grep)")

    def test_nenhum_identificador_generico_solto_nas_paginas(self):
        # B8 da 2.ª verificação (ML16): `const helper` no bar.html e `const data` no painel/apps-logica.mjs.
        declaracao = re.compile(r"\b(?:const|let|var|function)\s+(\w+)\b")
        pack = RAIZ / "2-configuracao" / "glzr" / "zebar" / "omarchy-catppuccin"
        for ficheiro in [*pack.rglob("*.mjs"), *pack.rglob("*.html")]:
            if "vendor" in ficheiro.parts:
                continue
            soltos = [nome for nome in declaracao.findall(ficheiro.read_text(encoding="utf-8")) if nome.lower() in PROIBIDOS]
            with self.subTest(ficheiro=ficheiro.name):
                self.assertEqual(soltos, [], "dê um nome que diga a função")


if __name__ == "__main__":
    unittest.main()
