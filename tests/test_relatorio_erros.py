"""Relatório de erros (morg_relatorio_erros.py, P3): o que leva e o que fica de fora.

Pesquisa em docs/pesquisa/relatorio-de-erros.md: o resumo; quando e onde (hora ISO 8601, versões); o que estava a
fazer; a exceção como o OpenTelemetry (tipo, mensagem, stack trace, gravidade); o registo do arranque; e os campos
que quem envia preenche. A limpeza (RFC 9457, RGPD) troca a pasta pessoal por ~ e os nomes por <utilizador>, e os
dados do painel em base64 não entram. A conta falsa é a "Ana".
"""

import importlib.util
import json
import tempfile
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path

from sistema_falso import PASTA_PACK

_especificacao = importlib.util.spec_from_file_location("morg_relatorio_erros", PASTA_PACK / "morg_relatorio_erros.py")
relatorio = importlib.util.module_from_spec(_especificacao)
_especificacao.loader.exec_module(relatorio)

CASA = r"C:\Users\Ana"
AGORA = datetime(2026, 10, 31, 20, 15, 3, tzinfo=timezone(timedelta(0)))


def rebentar():
    try:
        Path(CASA + r"\.glzr\layout.json").read_text(encoding="utf-8")  # a Ana não existe: rebenta de propósito
    except OSError as erro:
        return erro
    raise AssertionError("devia ter rebentado")


class Limpeza(unittest.TestCase):

    def test_pasta_pessoal_e_nomes_saem(self):
        texto = r"C:\Users\Ana\.glzr\x.py; c:/users/ana/y; olá Ana Silva; Anabela fica"
        self.assertEqual(relatorio.limpar(texto, CASA, ["Ana", "Ana Silva", ""]),
                         r"~\.glzr\x.py; ~/y; olá <utilizador>; Anabela fica")

    def test_dados_do_painel_em_base64_nao_entram(self):
        self.assertEqual(relatorio.argumentos_visiveis(["panel", "do", "eyJvcCI6ImtleSIsImtleSI6ImFsdCt4In0"]),
                         ["panel", "do", "<dados do painel>"])
        self.assertEqual(relatorio.argumentos_visiveis(["awake", "toggle"]), ["awake", "toggle"])


class Versao(unittest.TestCase):

    def test_le_a_versao_e_a_data_da_instalacao(self):
        with tempfile.TemporaryDirectory() as pasta:
            ficheiro = Path(pasta) / "instalacao.json"
            ficheiro.write_text(json.dumps({"versao": "exp/a 861c371", "instalado_em": "2026-10-31 07:18"}),
                                encoding="utf-8-sig")
            self.assertEqual(relatorio.versao_instalada(ficheiro), "exp/a 861c371, instalado em 2026-10-31 07:18")
            ficheiro.write_text(json.dumps({"instalado_em": "2026-10-31 07:18"}), encoding="utf-8")
            self.assertEqual(relatorio.versao_instalada(ficheiro), "desconhecida, instalado em 2026-10-31 07:18")
            ficheiro.write_text("não é json", encoding="utf-8")
            self.assertEqual(relatorio.versao_instalada(ficheiro), "desconhecida")
            self.assertEqual(relatorio.versao_instalada(Path(pasta) / "nao-existe.json"), "desconhecida")


class Registo(unittest.TestCase):

    def test_ultimas_linhas_ou_vazio(self):
        with tempfile.TemporaryDirectory() as pasta:
            ficheiro = Path(pasta) / ".layout-restore.log"
            ficheiro.write_text("\n".join(f"linha {n}" for n in range(30)), encoding="utf-8")
            self.assertEqual(relatorio.ultimas_linhas(ficheiro, 3), "linha 27\nlinha 28\nlinha 29")
            self.assertEqual(relatorio.ultimas_linhas(Path(pasta) / "nada.log"), "")


class Montar(unittest.TestCase):

    def setUp(self):
        self.texto = relatorio.montar_relatorio(
            rebentar(), ["bar_helper.py", "panel", "do", "eyJvcCI6ImtleSIsImtleSI6ImFsdCt4In0"], AGORA,
            versao="exp/a 861c371", registo=r"12:00 abri C:\Users\Ana\app.exe", casa=CASA, nomes=["Ana"])

    def test_tem_as_seccoes_da_pesquisa_por_ordem(self):
        seccoes = ["# Relatório de erro do Morg Keys", "**Resumo:** `panel do: FileNotFoundError`",
                   "## Quando e onde", "## O que estava a fazer", "## A exceção", "## Registo do arranque",
                   "## Para preencher por quem envia"]
        posicoes = [self.texto.index(s) for s in seccoes]
        self.assertEqual(posicoes, sorted(posicoes))

    def test_leva_o_que_e_preciso_para_corrigir(self):
        for pedaco in ("2026-10-31T20:15:03+00:00", "Morg Keys: exp/a 861c371", "Windows:", "Python:",
                       "`bar_helper.py panel do <dados do painel>`", "- Tipo: `FileNotFoundError`",
                       "- Gravidade: ERROR", "Traceback (most recent call last):", "in rebentar",
                       "- Passos para reproduzir:", "- O que esperava:", "- O que aconteceu:"):
            with self.subTest(pedaco=pedaco):
                self.assertIn(pedaco, self.texto)

    def test_nada_de_pessoal(self):
        self.assertNotIn("Ana", self.texto)
        self.assertNotIn("eyJvcCI6", self.texto)
        self.assertIn(r"~\\.glzr\\layout.json", self.texto)  # na mensagem do OSError as barras vêm a dobrar
        self.assertIn(r"12:00 abri ~\app.exe", self.texto)

    def test_sem_subcomando_e_sem_registo(self):
        texto = relatorio.montar_relatorio(ValueError("x"), ["bar_helper.py"], AGORA, versao="v", registo="",
                                           casa=CASA, nomes=[])
        self.assertIn("**Resumo:** `(sem subcomando): ValueError`", texto)
        self.assertIn("(vazio)", texto)


class PopupECopias(unittest.TestCase):
    """O popup liga-se por omissão e desliga-se com "erros = esconder"; a cópia fica sempre (os últimos 10)."""

    def test_popup_ligado_por_omissao_e_desligavel(self):
        with tempfile.TemporaryDirectory() as pasta:
            arranque = Path(pasta) / "arranque.txt"
            self.assertTrue(relatorio.popup_ligado(arranque))  # sem ficheiro
            for texto, ligado in (("animacao = cafe\n", True), ("erros = mostrar\n", True),
                                  ("ERROS = Esconder\n", False), ("erros = não\n", False),
                                  ("# erros = esconder\nerros = mostrar\n", True), ("erros\n", True)):
                with self.subTest(texto=texto):
                    arranque.write_text(texto, encoding="utf-8-sig")
                    self.assertEqual(relatorio.popup_ligado(arranque), ligado)

    def test_guarda_uma_copia_e_so_os_ultimos(self):
        with tempfile.TemporaryDirectory() as pasta:
            erros = Path(pasta) / "erros"
            for segundo in range(12):
                ultimo = relatorio.guardar_copia(f"relatório {segundo}", AGORA + timedelta(seconds=segundo), erros,
                                                 maximo=10)
            nomes = sorted(p.name for p in erros.iterdir())
            self.assertEqual(len(nomes), 10)
            self.assertEqual(nomes[0], "erro-20261031-201505.md")  # os 2 mais antigos saíram
            self.assertEqual(ultimo.read_text(encoding="utf-8"), "relatório 11")


if __name__ == "__main__":
    unittest.main()
