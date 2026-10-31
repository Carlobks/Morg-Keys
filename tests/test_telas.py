"""Regras de tela das páginas do pack (skill desenhando-telas, ML12): movimento e algarismos.

- Movimento: quem desliga as animações no Windows (prefers-reduced-motion) deixa de ver o movimento, mas o
  estado final e os sinais ficam (0,01 ms em vez de "none", para os eventos de fim continuarem a disparar).
- Algarismos de largura fixa (tabular-nums): a hora, as percentagens e as contagens não saltam ao mudar.
"""

import re
import unittest

from carregar_por_caminho import RAIZ

PACK = RAIZ / "2-configuracao" / "glzr" / "zebar" / "omarchy-catppuccin"
FOLHAS_CSS = ["styles.css", "guia/guia.css", "painel/apps.css"]
PAGINAS_COM_ESTILO = ["arranque/splash.html", "guia/sistema.html"]
SEM_MOVIMENTO = ["animation-duration: 0.01ms !important", "animation-delay: 0ms !important",
                 "animation-iteration-count: 1 !important", "transition-duration: 0.01ms !important",
                 "transition-delay: 0ms !important"]


def folhas_de_estilo():
    """{caminho: CSS} das folhas do pack e dos <style> das páginas que o têm."""
    folhas = {rel: (PACK / rel).read_text(encoding="utf-8") for rel in FOLHAS_CSS}
    for rel in PAGINAS_COM_ESTILO:
        folhas[rel] = re.search(r"<style>(.*?)</style>", (PACK / rel).read_text(encoding="utf-8"), re.DOTALL).group(1)
    return folhas


def bloco_sem_movimento(css):
    """Texto do @media (prefers-reduced-motion: reduce) até ao fim da folha (fica sempre no fim), ou None."""
    inicio = css.find("@media (prefers-reduced-motion: reduce)")
    return css[inicio:] if inicio >= 0 else None


class Movimento(unittest.TestCase):

    def test_cada_folha_com_movimento_respeita_o_windows(self):
        for rel, css in folhas_de_estilo().items():
            if not re.search(r"\b(animation|transition)\s*:", css):
                continue
            with self.subTest(folha=rel):
                bloco = bloco_sem_movimento(css)
                self.assertIsNotNone(bloco, "sem @media (prefers-reduced-motion: reduce)")
                for regra in SEM_MOVIMENTO:
                    self.assertIn(regra, bloco)

    def test_o_brilho_do_splash_movido_por_javascript_sai(self):
        # O sweep() mexe no #cshine pelo JavaScript; com as transições a 0,01 ms ficaria parado a meio.
        bloco = bloco_sem_movimento(folhas_de_estilo()["arranque/splash.html"])
        self.assertIn("#cshine { display: none !important; }", bloco)

    def test_o_bloco_fica_no_fim_para_ganhar_as_regras_de_cima(self):
        for rel, css in folhas_de_estilo().items():
            with self.subTest(folha=rel):
                self.assertEqual(css.count("@media (prefers-reduced-motion"), 1)
                self.assertNotRegex(bloco_sem_movimento(css), r"\}\s*\}\s*\S", "há regras depois do bloco")


class Algarismos(unittest.TestCase):

    def test_cada_pagina_usa_algarismos_de_largura_fixa(self):
        for rel, css in folhas_de_estilo().items():
            with self.subTest(folha=rel):
                self.assertIn("font-variant-numeric: tabular-nums", css)


if __name__ == "__main__":
    unittest.main()
