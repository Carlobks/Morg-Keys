"""A documentação continua achável e coerente (regras ÍNDICE DOS DOCS, DECISÕES EM ADR, ARMADILHAS REGISTADAS,
PESQUISA ANTES DE IMPLEMENTAR e PLANO ANTES DE MEXER do CLAUDE.md; skill orquestrando-sessoes para os handoffs).

Regressão de 2026-10-30: a docs/auditoria-2026-10-24.md nunca entrou no índice; o plano 01 não dizia o que
ficava fora do escopo. Estas regras eram só texto e falharam.
"""

import re
import subprocess
import unittest

from carregar_por_caminho import RAIZ

DOCS = RAIZ / "docs"
DATA = re.compile(r"\|\s*20\d\d-\d\d-\d\d(?:/\d\d)?\s*\|\s*$")  # aceita um intervalo: 2026-10-22/23
SECCOES_DO_HANDOFF = ("Objetivo", "Estado verificado", "Decisões", "Descartado", "Próximos passos")
HASH = re.compile(r"`([0-9a-f]{7,40})`")


def texto(caminho):
    return caminho.read_text(encoding="utf-8-sig")


def titulos(caminho):
    """Títulos (## …) de um ficheiro Markdown."""
    return [linha.lstrip("#").strip() for linha in texto(caminho).splitlines() if linha.startswith("#")]


class IndiceDosDocs(unittest.TestCase):

    def test_cada_ficheiro_e_pasta_de_docs_estao_no_indice(self):
        indice = texto(DOCS / "README.md")
        for caminho in sorted(DOCS.iterdir()):
            if caminho.name == "README.md" or caminho.suffix not in ("", ".md"):
                continue
            alvo = f"]({caminho.name}/" if caminho.is_dir() else f"]({caminho.name})"
            with self.subTest(caminho=caminho.name):
                self.assertIn(alvo, indice, "ficheiro .md novo → linha em docs/README.md")

    def test_cada_adr_esta_na_tabela_com_numeros_seguidos(self):
        indice = texto(DOCS / "README.md")
        adrs = sorted(caminho.name for caminho in (DOCS / "decisoes").glob("*.md"))
        self.assertEqual([nome[:4] for nome in adrs], [f"{n:04d}" for n in range(1, len(adrs) + 1)])
        for nome in adrs:
            with self.subTest(adr=nome):
                self.assertIn(f"](decisoes/{nome})", indice)


class Pesquisa(unittest.TestCase):

    def test_cada_pesquisa_esta_no_indice_com_data(self):
        linhas = texto(DOCS / "pesquisa" / "README.md").splitlines()
        for caminho in sorted((DOCS / "pesquisa").glob("*.md")):
            if caminho.name == "README.md":
                continue
            with self.subTest(pesquisa=caminho.name):
                linha = next((linha for linha in linhas if f"]({caminho.name})" in linha), "")
                self.assertRegex(linha, DATA, "linha no índice da pesquisa com a data na última coluna")


class Armadilhas(unittest.TestCase):

    def test_numeracao_seguida_e_cada_uma_com_a_regra(self):
        linhas = [linha for linha in texto(DOCS / "armadilhas.md").splitlines() if re.match(r"\| A\d+ \|", linha)]
        numeros = [int(re.match(r"\| A(\d+)", linha).group(1)) for linha in linhas]
        self.assertEqual(numeros, list(range(1, len(numeros) + 1)), "A1, A2, … sem saltos nem repetidos")
        for linha in linhas:
            colunas = [coluna.strip() for coluna in linha.strip().strip("|").split("|")]
            with self.subTest(armadilha=colunas[0]):
                self.assertGreaterEqual(len(colunas), 4)
                self.assertTrue(colunas[-1], "falta a regra para o evitar")


class Planos(unittest.TestCase):

    def test_planos_dizem_o_fora_do_escopo_e_a_prova(self):
        planos = [*DOCS.glob("planos/*.md"), *DOCS.glob("*/plano-*.md")]
        self.assertGreater(len(planos), 0)
        for plano in planos:
            seccoes = " | ".join(titulos(plano))
            with self.subTest(plano=plano.name):
                self.assertIn("Fora do escopo", seccoes)
                self.assertRegex(seccoes, r"Prova|Verificação")


class Handoffs(unittest.TestCase):

    def test_um_ficheiro_por_assunto_com_as_seccoes_e_hashes_que_existem(self):
        pasta = RAIZ / ".context"
        self.assertFalse((pasta / "HANDOFF.md").exists(), "um ficheiro por assunto: HANDOFF-<assunto>.md")
        for handoff in sorted(pasta.glob("HANDOFF-*.md")):
            with self.subTest(handoff=handoff.name):
                seccoes = titulos(handoff)
                for seccao in SECCOES_DO_HANDOFF:
                    self.assertTrue(any(s.startswith(seccao) for s in seccoes), f"falta a secção {seccao}")
                for sha in HASH.findall(texto(handoff)):
                    existe = subprocess.run(["git", "cat-file", "-e", f"{sha}^{{commit}}"], cwd=RAIZ,
                                            capture_output=True, check=False).returncode == 0
                    self.assertTrue(existe, f"o commit {sha} não existe: o estado não foi verificado")


if __name__ == "__main__":
    unittest.main()
