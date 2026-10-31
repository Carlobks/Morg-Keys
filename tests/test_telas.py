"""Regras de tela das páginas do pack (skill desenhando-telas, ML12): movimento, contraste e algarismos.

- Movimento: quem desliga as animações no Windows (prefers-reduced-motion) deixa de ver o movimento, mas o
  estado final e os sinais ficam (0,01 ms em vez de "none", para os eventos de fim continuarem a disparar).
- Contraste (WCAG 2.2, 1.4.3, AA): cada cor de texto com pelo menos 4,5:1 nos fundos da página, calculado
  a partir dos tokens Catppuccin das folhas; as exceções (ícones, componentes inativos) dizem o motivo.
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


FUNDOS = {"base": "#1e1e2e", "mantle": "#181825", "crust": "#11111b"}  # fundos dos painéis e da barra
FUNDOS_DA_FOLHA = {"arranque/splash.html": ["#000000", "#181825", "#11111b"]}  # preto, lista, caixa do estado
MINIMO = 4.5  # WCAG 2.2, 1.4.3 (AA), texto normal: o texto do pack é todo pequeno
# Cores de destaque (--c, --k, --ic) que não são texto ou estão isentas do 1.4.3, com o motivo.
EXCECOES = {
    ("styles.css", ".indicator.off"): "ícone da chávena desligada, esbatido de propósito e só visível no hover",
    ("painel/apps.css", ".key.fixed"): "tecla fixa, inativa (opacity 0.45): componente inativo, isento do 1.4.3",
    ("arranque/splash.html", ".it.fail .st"): "cor do arco do estado (borda), não de texto",
}


def luminancia(cor):
    canais = [int(cor[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    r, g, b = (c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in canais)
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def contraste(a, b):
    """Razão de contraste do WCAG entre duas cores #rrggbb."""
    clara, escura = sorted((luminancia(a), luminancia(b)), reverse=True)
    return (clara + 0.05) / (escura + 0.05)


def mistura(cor, fundo, parte=0.16):
    """color-mix(in srgb, cor 16%, fundo): o fundo dos chips."""
    return "#" + "".join(f"{round(int(cor[i:i + 2], 16) * parte + int(fundo[i:i + 2], 16) * (1 - parte)):02x}"
                         for i in (1, 3, 5))


def paleta(folhas):
    """{token: #cor} de todas as folhas; o mesmo token tem de ter a mesma cor em todas."""
    cores = {}
    for rel, css in folhas.items():
        for nome, cor in re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{6})\b", css):
            if nome in ("c", "k", "ic"):
                continue
            assert cores.setdefault(nome, cor.lower()) == cor.lower(), f"{rel}: --{nome} com outra cor"
    return cores


def resolver(valor, cores):
    """#cor de um valor CSS (var(--token) da paleta ou #rrggbb); None se não for uma cor fixa."""
    token = re.match(r"var\(--([\w-]+)\)?", valor.strip())
    if token:
        return cores.get(token.group(1))
    literal = re.match(r"#[0-9a-fA-F]{6}\b", valor.strip())
    return literal.group(0).lower() if literal else None


def cores_de_texto(css, cores):
    """[(seletor, propriedade, #cor, #fundo da regra ou None)] das declarações color, --c, --k e --ic com cor fixa.

    O fundo da regra conta quando ela própria pinta um fundo sólido (ex.: o × vermelho com o texto escuro).
    """
    achados = []
    for seletor, corpo in re.findall(r"([^{}]+)\{([^{}]*)\}", css):
        seletor = " ".join(re.sub(r"/\*.*?\*/", "", seletor, flags=re.DOTALL).split())
        fundo = re.search(r"(?<![\w-])background(?:-color)?\s*:\s*([^;]+)", corpo)
        fundo = resolver(fundo.group(1), cores) if fundo else None
        for prop, valor in re.findall(r"(?<![\w-])(color|--c|--k|--ic)\s*:\s*([^;]+)", corpo):
            cor = resolver(valor, cores)
            if cor:
                achados.append((seletor, prop, cor, fundo))
    return achados


class Contraste(unittest.TestCase):

    def test_contraste_e_mistura_seguem_o_wcag(self):
        self.assertAlmostEqual(contraste("#ffffff", "#000000"), 21)
        self.assertAlmostEqual(contraste("#6c7086", "#1e1e2e"), 3.36, places=2)  # o overlay0 que saiu
        self.assertEqual(mistura("#ffffff", "#000000", 0.5), "#808080")

    def test_texto_com_pelo_menos_4_5_para_1_em_cada_fundo(self):
        folhas = folhas_de_estilo()
        cores = paleta(folhas)
        for rel, css in folhas.items():
            fundos = FUNDOS_DA_FOLHA.get(rel, list(FUNDOS.values()))
            for seletor, prop, cor, fundo_da_regra in cores_de_texto(css, cores):
                if (rel, seletor) in EXCECOES:
                    continue
                # As cores de destaque também pintam o texto dos chips, sobre a mesma cor a 16 %.
                pares = [fundo_da_regra] if fundo_da_regra else (
                    fundos + ([mistura(cor, f) for f in fundos] if prop != "color" else []))
                for fundo in pares:
                    with self.subTest(folha=rel, seletor=seletor, cor=cor, fundo=fundo):
                        self.assertGreaterEqual(contraste(cor, fundo), MINIMO)

    def test_sobre_o_fundo_surface0_o_texto_apagado_sobe_para_o_subtext0(self):
        # Os campos de filtro e o hover das apps são surface0: aí o overlay2 dá 4,45:1.
        cores = paleta(folhas_de_estilo())
        self.assertLess(contraste(cores["overlay2"], cores["surface0"]), MINIMO)
        self.assertGreaterEqual(contraste(cores["subtext0"], cores["surface0"]), MINIMO)
        apps = folhas_de_estilo()["painel/apps.css"]
        for regra in ("#apps input::placeholder { color: var(--subtext0); }",
                      ".app:hover .used, .app.cursor .used { color: var(--subtext0); }"):
            self.assertIn(regra, apps)
        self.assertIn("header input::placeholder { color: var(--subtext0); }", folhas_de_estilo()["guia/guia.css"])

    def test_as_excecoes_existem(self):
        folhas = folhas_de_estilo()
        for rel, seletor in EXCECOES:
            with self.subTest(folha=rel, seletor=seletor):
                self.assertIn(seletor, [achado[0] for achado in cores_de_texto(folhas[rel], paleta(folhas))])


class Algarismos(unittest.TestCase):

    def test_cada_pagina_usa_algarismos_de_largura_fixa(self):
        for rel, css in folhas_de_estilo().items():
            with self.subTest(folha=rel):
                self.assertIn("font-variant-numeric: tabular-nums", css)


if __name__ == "__main__":
    unittest.main()
