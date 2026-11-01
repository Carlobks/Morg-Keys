"""Regras de janela do config.yaml para os jogos em ecrã inteiro (P5, docs/pesquisa/jogos-ecra-inteiro.md).

Com o GlazeWM a arrumar o Baldur's Gate 3 no mosaico, o jogo ficava no tamanho da área do mosaico (1894x979) e
minimizado. A prova da correção é uma regra `ignore` só para o processo do jogo: tira-o da arrumação e mantém os
atalhos (o dono quer usá-los com o jogo aberto, por isso a pausa não serve). O cliente da Steam (steamwebhelper)
tem a mesma classe de janela (SDL_app), por isso a regra é pelo processo e nunca pela classe.
"""

import re
import unittest

from carregar_por_caminho import RAIZ

CONFIG = RAIZ / "2-configuracao" / "glzr" / "glazewm" / "config.yaml"


def bloco_ignore(texto):
    """O texto da primeira regra `commands: ['ignore']`, até à regra seguinte."""
    inicio = texto.index("  - commands: ['ignore']\n")
    fim = texto.find("\n  - commands:", inicio + 1)
    return texto[inicio:fim]


class JogosForaDoMosaico(unittest.TestCase):

    def setUp(self):
        self.ignore = bloco_ignore(CONFIG.read_text(encoding="utf-8"))

    def test_o_baldurs_gate_3_nao_entra_no_mosaico(self):
        self.assertIn("- window_process: { equals: 'bg3_dx11' }", self.ignore)

    def test_a_steam_nao_e_ignorada_pela_classe_dos_jogos(self):
        self.assertNotRegex(self.ignore, r"window_class: \{ (equals|regex): '[^']*SDL_app")
        self.assertNotIn("steamwebhelper", self.ignore)

    def test_le_so_o_bloco_do_ignore(self):
        texto = "x\n  - commands: ['ignore']\n    match:\n      - a\n\n  - commands: ['outra']\n      - b\n"
        self.assertEqual(bloco_ignore(texto), "  - commands: ['ignore']\n    match:\n      - a\n")
        self.assertTrue(re.search(r"commands: \['ignore'\]", self.ignore))


if __name__ == "__main__":
    unittest.main()
