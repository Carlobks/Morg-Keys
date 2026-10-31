"""O formulário de issue para um erro (.github/ISSUE_TEMPLATE/erro.yml, P3.3).

Lido como texto (sem biblioteca de YAML). Pede o que o guia de bugs da Mozilla pede (resumo, passos, o que
esperava, o que aconteceu) e um campo onde se cola o relatório que o Morg Keys guardou, formatado como código
(`render: shell`, GitHub). Avisa para rever o relatório antes de o publicar (RFC 9457: a informação é revista).
"""

import re
import unittest

from carregar_por_caminho import RAIZ

FORMULARIO = RAIZ / ".github" / "ISSUE_TEMPLATE" / "erro.yml"


class FormularioDeErro(unittest.TestCase):

    def setUp(self):
        self.texto = FORMULARIO.read_bytes().decode("utf-8")

    def test_tem_as_chaves_do_github(self):
        for chave in ("name:", "description:", "body:"):
            with self.subTest(chave=chave):
                self.assertRegex(self.texto, rf"(?m)^{chave}")

    def test_pede_os_campos_da_pesquisa(self):
        ids = re.findall(r"(?m)^\s+id: ([\w-]+)$", self.texto)
        self.assertEqual(ids, ["resumo", "passos", "esperado", "aconteceu", "relatorio"])
        self.assertEqual(self.texto.count("required: true"), 4)  # o relatório é opcional (pode não ter havido)

    def test_o_relatorio_cola_se_como_codigo_e_revisto(self):
        relatorio = self.texto.split("id: relatorio", 1)[1]
        self.assertIn("render: shell", relatorio)
        self.assertIn(".glzr\\erros", relatorio)
        self.assertIn("Reveja", relatorio)


if __name__ == "__main__":
    unittest.main()
