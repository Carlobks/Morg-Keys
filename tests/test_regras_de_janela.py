"""Regras de janela do config.yaml para os jogos em ecrã inteiro (P5, docs/pesquisa/jogos-ecra-inteiro.md).

Com o GlazeWM a arrumar o Baldur's Gate 3 no mosaico, o jogo ficava no tamanho da área do mosaico (1894x979) e
minimizado.
- 1.ª prova: uma regra `ignore` só para o processo do jogo. Tirava-o da arrumação e mantinha os atalhos, mas ao
  trocar de workspace o jogo minimizava-se (o DirectX larga o ecrã inteiro exclusivo quando fica tapado) e o
  GlazeWM não o voltava a mostrar, porque não o arrumava.
- 2.ª prova (P5.2): o jogo em "janela sem bordas" e uma regra `set-fullscreen`. O GlazeWM arruma-o em ecrã inteiro,
  esconde-o ao sair do workspace e mostra-o ao voltar.
O cliente da Steam (steamwebhelper) tem a mesma classe de janela (SDL_app), por isso a regra é pelo processo e nunca
pela classe.
"""

import re
import unittest

from carregar_por_caminho import RAIZ

CONFIG = RAIZ / "2-configuracao" / "glzr" / "glazewm" / "config.yaml"
JOGO = "- window_process: { equals: 'bg3_dx11' }"


def bloco_da_regra(texto, comandos):
    """O texto da primeira regra `commands: [<comandos>]`, até à regra seguinte."""
    inicio = texto.index(f"  - commands: ['{comandos}']\n")
    fim = texto.find("\n  - commands:", inicio + 1)
    return texto[inicio:fim]


class JogosEmEcraInteiro(unittest.TestCase):

    def setUp(self):
        texto = CONFIG.read_text(encoding="utf-8")
        self.ignore = bloco_da_regra(texto, "ignore")
        self.ecra_inteiro = bloco_da_regra(texto, "set-fullscreen")

    def test_o_baldurs_gate_3_vai_para_ecra_inteiro(self):
        self.assertIn(JOGO, self.ecra_inteiro)

    def test_o_baldurs_gate_3_nao_esta_no_ignore(self):
        self.assertNotIn("bg3_dx11", self.ignore)

    def test_a_steam_nao_apanhada_pela_classe_dos_jogos(self):
        for bloco in (self.ignore, self.ecra_inteiro):
            self.assertNotRegex(bloco, r"window_class: \{ (equals|regex): '[^']*SDL_app")
            self.assertNotIn("steamwebhelper", bloco)

    def test_le_so_o_bloco_pedido(self):
        texto = "x\n  - commands: ['ignore']\n    match:\n      - a\n\n  - commands: ['outra']\n      - b\n"
        self.assertEqual(bloco_da_regra(texto, "ignore"), "  - commands: ['ignore']\n    match:\n      - a\n")
        self.assertTrue(re.search(r"commands: \['ignore'\]", self.ignore))


if __name__ == "__main__":
    unittest.main()
