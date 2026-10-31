"""As regras do agente (CLAUDE.md) ficam curtas, com barreira e sem apontar para o que não existe (Morg Laws).

- O CLAUDE.md é lido em todo o turno: no máximo 100 linhas de 160 caracteres (skill escrevendo-regras-de-agente).
- Cada regra (`**TÍTULO:** …`) tem uma linha em docs/regras-e-barreiras.md com a barreira que a obriga
  ("texto é conselho; o que tem de ser cumprido vira hook, teste ou CI").
- Um caminho citado que já não existe ensina o agente a saltar a regra inteira: todos têm de existir.
- As skills do índice estão instaladas, e as instaladas estão no índice e no skills-lock.json.
"""

import json
import re
import unittest

from carregar_por_caminho import RAIZ

CLAUDE_MD = RAIZ / "CLAUDE.md"
MAPA = RAIZ / "docs" / "regras-e-barreiras.md"
PASTA_SKILLS = RAIZ / ".claude" / "skills"
MAXIMO_DE_LINHAS, MAXIMO_POR_LINHA = 100, 160
TITULO = re.compile(r"\*\*([A-ZÀ-Ý0-9][A-ZÀ-Ý0-9 ,.º%/-]*[A-ZÀ-Ý0-9%]):\*\*")
BARREIRAS = ("hook", "git", "teste", "permissão", "CI", "texto", "por fazer")
CAMINHO = re.compile(r"`((?:\.githooks|\.claude|\.seguranca|docs|scripts|tests|2-configuracao)/[^`<>{}*\s]*"
                     r"|[\w.-]+\.(?:md|ps1|cmd|json|txt))`")


def texto(caminho):
    return caminho.read_text(encoding="utf-8")


def linhas_do_mapa():
    """{título: (barreira, onde)} da tabela do mapa."""
    resultado = {}
    for linha in texto(MAPA).splitlines():
        colunas = [coluna.strip() for coluna in linha.strip().strip("|").split("|")]
        if len(colunas) == 3 and TITULO.fullmatch(f"**{colunas[0]}:**"):
            resultado[colunas[0]] = (colunas[1], colunas[2])
    return resultado


class ClaudeMdCurto(unittest.TestCase):

    def test_tamanho(self):
        linhas = texto(CLAUDE_MD).splitlines()
        self.assertLessEqual(len(linhas), MAXIMO_DE_LINHAS)
        longas = [numero for numero, linha in enumerate(linhas, 1) if len(linha) > MAXIMO_POR_LINHA]
        self.assertEqual(longas, [], f"linhas com mais de {MAXIMO_POR_LINHA} caracteres")

    def test_regras_com_titulo_unico(self):
        titulos = TITULO.findall(texto(CLAUDE_MD))
        self.assertGreaterEqual(len(titulos), 15)
        self.assertEqual(len(titulos), len(set(titulos)), "dois títulos iguais acabam por se contradizer")


def regras():
    """{título: texto da regra com as linhas de continuação} do CLAUDE.md."""
    blocos, atual = {}, None
    for linha in texto(CLAUDE_MD).splitlines():
        cabeca = TITULO.match(linha[2:]) if linha.startswith("- ") else None
        if cabeca:
            atual = cabeca.group(1)
            blocos[atual] = linha
        elif atual and linha.startswith("  "):
            blocos[atual] += " " + linha.strip()
        else:
            atual = None
    return blocos


class CadaRegraDizOPorque(unittest.TestCase):
    """B6 da 2.ª verificação (ML16): o motivo é o que torna a regra aplicável a casos novos (skill §3)."""

    def test_cada_regra_tem_o_motivo(self):
        todas = regras()
        self.assertEqual(set(todas), set(TITULO.findall(texto(CLAUDE_MD))))
        self.assertEqual([titulo for titulo, corpo in todas.items() if "· *" not in corpo], [])


class CadaRegraTemBarreira(unittest.TestCase):

    def test_cada_regra_esta_no_mapa_e_o_mapa_nao_tem_regras_a_mais(self):
        self.assertEqual(set(TITULO.findall(texto(CLAUDE_MD))), set(linhas_do_mapa()))

    def test_a_barreira_e_de_um_tipo_conhecido(self):
        for titulo, (barreira, _) in linhas_do_mapa().items():
            with self.subTest(regra=titulo):
                self.assertTrue(barreira.startswith(BARREIRAS), f"barreira '{barreira}' fora de {BARREIRAS}")


    def test_por_fazer_so_de_fases_por_fazer(self):
        # B4 da 2.ª verificação (ML16): FINS DE LINHA dizia "por fazer (ML8)" com a ML8 feita há um dia.
        plano = texto(RAIZ / "docs" / "morg-laws" / "plano-01.md")
        for titulo, (barreira, _) in linhas_do_mapa().items():
            fase = re.match(r"por fazer \((ML\d+\w?)\)", barreira)
            if fase:
                with self.subTest(regra=titulo, fase=fase.group(1)):
                    self.assertNotIn(f"- [x] **{fase.group(1)} ", plano, "a fase já está feita: atualize o mapa")


class NadaApontaParaOQueNaoExiste(unittest.TestCase):

    def test_caminhos_citados_existem(self):
        # Um caminho com pasta conta a partir da raiz; um nome solto (ex.: `zpack.json`) pode estar em qualquer pasta.
        nomes = {caminho.name for caminho in RAIZ.rglob("*") if "node_modules" not in caminho.parts}
        for ficheiro in (CLAUDE_MD, MAPA):
            for caminho in CAMINHO.findall(texto(ficheiro)):
                with self.subTest(ficheiro=ficheiro.name, caminho=caminho):
                    existe = (RAIZ / caminho.rstrip("/")).exists() if "/" in caminho else caminho in nomes
                    self.assertTrue(existe, "caminho citado que já não existe")

    def test_skills_do_indice_instaladas_e_no_lock(self):
        citadas = set(re.findall(r"`([a-z-]+)`", texto(CLAUDE_MD).split("## Quando ler que skill")[1]))
        instaladas = {pasta.name for pasta in PASTA_SKILLS.iterdir() if (pasta / "SKILL.md").is_file()}
        no_lock = set(json.loads(texto(RAIZ / "skills-lock.json"))["skills"])
        self.assertEqual(citadas, instaladas)
        self.assertEqual(no_lock, instaladas)


if __name__ == "__main__":
    unittest.main()
