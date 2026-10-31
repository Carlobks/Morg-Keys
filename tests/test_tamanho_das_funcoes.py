"""Funções Python até 35 linhas (regras FICHEIROS PEQUENOS e NÃO PIORAR do CLAUDE.md; auditoria Q3).

As funções que já passavam em 2026-10-31 ficam em LONGAS_ANTIGAS com o tamanho de então: só podem encolher, e saem
da lista quando cabem no limite. Uma função nova acima de 35 linhas falha. No JS a mesma regra é a
noExcessiveLinesPerFunction do Biome (biome.jsonc); no PowerShell verifica-a o scripts/testar.ps1.
"""

import ast
import subprocess
import unittest

from carregar_por_caminho import RAIZ

LIMITE = 35
# "ficheiro:função" -> linhas em 2026-10-31. Só desce.
LONGAS_ANTIGAS = {
    "2-configuracao/claude/statusline.py:main": 43,
    "2-configuracao/glzr/zebar/omarchy-catppuccin/morg_cortina.py:_run": 57,
    "tests/test_arranque.py:__enter__": 46,
    "tests/test_arranque.py:test_sequencia_normal": 44,
}


def tamanhos(fonte, caminho):
    """{"ficheiro:função": linhas} de todas as funções de um código Python."""
    return {f"{caminho}:{no.name}": no.end_lineno - no.lineno + 1 for no in ast.walk(ast.parse(fonte))
            if isinstance(no, (ast.FunctionDef, ast.AsyncFunctionDef))}


def funcoes_do_repositorio():
    caminhos = subprocess.run(["git", "ls-files", "*.py"], cwd=RAIZ, capture_output=True, text=True,
                              encoding="utf-8", check=True).stdout.splitlines()
    resultado = {}
    for caminho in caminhos:
        resultado.update(tamanhos((RAIZ / caminho).read_text(encoding="utf-8-sig"), caminho))
    return resultado


class TamanhoDasFuncoes(unittest.TestCase):

    def test_o_medidor_apanha_uma_funcao_de_36_linhas(self):
        fonte = "def longa():\n" + "    x = 1\n" * 35
        self.assertEqual(tamanhos(fonte, "a.py"), {"a.py:longa": 36})

    def test_nenhuma_funcao_nova_passa_o_limite_e_as_antigas_nao_crescem(self):
        for nome, linhas in funcoes_do_repositorio().items():
            if linhas > LIMITE:
                with self.subTest(funcao=nome):
                    self.assertLessEqual(linhas, LONGAS_ANTIGAS.get(nome, LIMITE), "divida-a por responsabilidade")

    def test_lista_das_antigas_esta_atualizada(self):
        atuais = funcoes_do_repositorio()
        for nome, linhas in LONGAS_ANTIGAS.items():
            with self.subTest(funcao=nome):
                self.assertGreater(atuais.get(nome, 0), LIMITE, "já cabe no limite (ou mudou de nome): tire-a da lista")
                self.assertLessEqual(atuais[nome], linhas)


if __name__ == "__main__":
    unittest.main()
