"""Alarmes silenciados só com motivo, e nunca mais do que hoje (regras SEM SILENCIAR ALARME e NÃO PIORAR).

Conta os `noqa`, `pragma: no cover`, `node:coverage disable`, `biome-ignore`, `eslint-disable` e `SuppressMessage`
no código (testes e docs de fora: lá são exemplos). Cada um tem o motivo na mesma linha, depois de "—", ou num
comentário na linha de cima. A contagem por tipo não pode subir: quem tira um, baixa o número no mesmo commit.
Um `noqa` só pode citar regras que o ruff tem ligadas (pergunta-se ao próprio ruff): o de uma regra desligada é
ruído. A auditoria Q5 achou que `SIM115` e `BLE001` estavam desligadas; medido em 2026-10-31, o ruff 0.17 liga-as
por omissão (cerca de 400 regras), e o `RUF100` do ruff.toml confirma que os 4 `noqa` silenciam algo.
"""

import re
import subprocess
import sys
import unittest

from carregar_por_caminho import RAIZ

# Só a diretiva verdadeira (um comentário que fala dela, como os do testar.ps1, não conta).
ALARMES = {
    "noqa": re.compile(r"^\s*[^#\s].*#\s*noqa\b"),
    "pragma: no cover": re.compile(r"^\s*[^#\s].*#\s*pragma:\s*no cover"),
    "node:coverage disable": re.compile(r"^\s*/\*\s*node:coverage (?:disable|ignore)"),
    "biome-ignore": re.compile(r"^\s*//\s*biome-ignore"),
    "eslint-disable": re.compile(r"(?://|/\*)\s*eslint-disable"),
    "SuppressMessage": re.compile(r"\[\s*(?:System\.)?Diagnostics\.CodeAnalysis\.SuppressMessage"),
}
# Linha de base de 2026-10-31 (ML9). Só desce.
MAXIMO_POR_TIPO = {"noqa": 4, "pragma: no cover": 1, "node:coverage disable": 2}
EXTENSOES_DE_CODIGO = (".py", ".mjs", ".js", ".ps1", ".psm1", ".html")
COMENTARIO = re.compile(r"^\s*(?:#|//|/\*|<!--)")


def ficheiros_de_codigo():
    saida = subprocess.run(["git", "ls-files"], cwd=RAIZ, capture_output=True, text=True, encoding="utf-8",
                           check=True).stdout.splitlines()
    return [caminho for caminho in saida if caminho.endswith(EXTENSOES_DE_CODIGO)
            and not caminho.startswith("tests/") and "/vendor/" not in caminho]


def regras_ligadas_no_ruff():
    """Códigos das regras que o ruff corre neste repositório (ruff check --show-settings)."""
    saida = subprocess.run([sys.executable, "-m", "ruff", "check", "--show-settings", "scripts/estragos.py"], cwd=RAIZ,
                           capture_output=True, text=True, encoding="utf-8", check=True).stdout
    bloco = saida.split("linter.rules.enabled = [", 1)[1].split("]", 1)[0]
    return set(re.findall(r"\(([A-Z]+\d+)\)", bloco))


def alarmes():
    """[(tipo, caminho, número da linha, linha, linha de cima)] de todos os alarmes silenciados."""
    resultado = []
    for caminho in ficheiros_de_codigo():
        linhas = (RAIZ / caminho).read_text(encoding="utf-8-sig").splitlines()
        for numero, linha in enumerate(linhas, 1):
            for tipo, padrao in ALARMES.items():
                if padrao.search(linha):
                    resultado.append((tipo, caminho, numero, linha, linhas[numero - 2] if numero > 1 else ""))
    return resultado


class AlarmesComMotivo(unittest.TestCase):

    def test_cada_alarme_tem_motivo(self):
        for tipo, caminho, numero, linha, de_cima in alarmes():
            with self.subTest(alarme=f"{caminho}:{numero} {tipo}"):
                self.assertTrue(" — " in linha or COMENTARIO.match(de_cima), "falta o motivo (depois de — ou na linha de cima)")

    def test_a_contagem_nao_sobe(self):
        contagem = {}
        for tipo, *_ in alarmes():
            contagem[tipo] = contagem.get(tipo, 0) + 1
        for tipo, quantos in contagem.items():
            with self.subTest(tipo=tipo):
                self.assertLessEqual(quantos, MAXIMO_POR_TIPO.get(tipo, 0), "corrija o apontado em vez de silenciar")

    def test_noqa_so_de_regras_ligadas(self):
        ligadas = regras_ligadas_no_ruff()
        self.assertIn("BLE001", ligadas)  # o leitor das definições funciona (a regra está ligada por omissão)
        for tipo, caminho, numero, linha, _ in alarmes():
            if tipo != "noqa":
                continue
            codigos = re.search(r"noqa:\s*([\w, ]+?)(?:\s+—|$)", linha).group(1).replace(" ", "").split(",")
            for codigo in codigos:
                with self.subTest(alarme=f"{caminho}:{numero} {codigo}"):
                    self.assertIn(codigo, ligadas, "regra que o ruff não corre: o noqa é ruído")


if __name__ == "__main__":
    unittest.main()
