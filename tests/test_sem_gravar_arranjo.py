"""O "Alt+Esc G" (gravar arranjo) saiu: o painel "Apps e arranque" é o único sítio do arranque (P2, 2026-10-31).

O G e o painel escreviam no mesmo layout.json com significados diferentes: o G reescrevia-o só com as janelas
abertas, apagando as apps do painel que não estavam abertas e mudando as outras de workspace; sem janelas, dava o
som de erro e não mostrava nada. Decisão do dono: tirar o G. Este teste falha se voltar a aparecer uma tecla, um
subcomando ou um texto vivo que o cite (os documentos históricos ficam como estão).
"""

import re
import unittest

from carregar_por_caminho import RAIZ

CITACAO = re.compile(r"layout[-_]save|Alt\+Esc,? G\b|Gravar arranjo")
VIVOS = [*sorted((RAIZ / "2-configuracao").rglob("*.py")), *sorted((RAIZ / "2-configuracao").rglob("*.mjs")),
         *sorted((RAIZ / "2-configuracao").rglob("*.html")), *sorted((RAIZ / "2-configuracao").rglob("*.yaml")),
         *[RAIZ / "docs" / nome for nome in ("arquitetura.md", "painel-apps.md", "validacao-manual.md")],
         RAIZ / "Tutorial.html", RAIZ / "README.md", *sorted((RAIZ / "tests").glob("test_*.py")),
         *sorted((RAIZ / "tests").glob("*.test.mjs"))]


class SemGravarArranjo(unittest.TestCase):

    def test_nada_vivo_cita_o_gravar_arranjo(self):
        este = __file__.replace("\\", "/").rsplit("/", 1)[-1]
        for ficheiro in VIVOS:
            if "vendor" in ficheiro.parts or ficheiro.name == este:
                continue
            achados = [n for n, linha in enumerate(ficheiro.read_text(encoding="utf-8").splitlines(), 1)
                       if CITACAO.search(linha)]
            with self.subTest(ficheiro=str(ficheiro.relative_to(RAIZ))):
                self.assertEqual(achados, [])

    def test_a_camada_sistema_ja_nao_tem_a_tecla_g(self):
        config = (RAIZ / "2-configuracao" / "glzr" / "glazewm" / "config.yaml").read_text(encoding="utf-8")
        sistema = config.split("name: 'sistema'", 1)[1].split("\n  - name:", 1)[0]
        self.assertNotIn("bindings: ['g']", sistema)


if __name__ == "__main__":
    unittest.main()
