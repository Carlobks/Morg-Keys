"""A bateria de estragos (scripts/estragos.py) não encolhe (regras NUNCA ENFRAQUECER UM TESTE e NÃO PIORAR).

Os estragos provam que os testes apanham código errado; tirar um estrago enfraquece essa prova sem que nenhum teste
falhe. Em 2026-10-31 a bateria tinha 80 estragos, todos apanhados. Estrago novo: subir MINIMO no mesmo commit.
Lê-se o ficheiro sem o importar (o estragos.py muda de pasta ao ser carregado).
"""

import ast
import unittest

from carregar_por_caminho import RAIZ

MINIMO = 80


def estragos():
    """Pares (texto certo, texto estragado) da lista MUTANTES do scripts/estragos.py."""
    arvore = ast.parse((RAIZ / "scripts" / "estragos.py").read_text(encoding="utf-8"))
    atribuicao = next(no for no in arvore.body if isinstance(no, ast.Assign)
                      and any(getattr(alvo, "id", "") == "MUTANTES" for alvo in no.targets))
    return ast.literal_eval(atribuicao.value)


class BateriaDeEstragos(unittest.TestCase):

    def test_nao_encolhe(self):
        self.assertGreaterEqual(len(estragos()), MINIMO, "um estrago tirado enfraquece a prova dos testes")

    def test_cada_estrago_muda_mesmo_o_codigo(self):
        for certo, estragado in estragos():
            with self.subTest(estrago=certo[:60]):
                self.assertNotEqual(certo, estragado)


if __name__ == "__main__":
    unittest.main()
