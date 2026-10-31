"""Relatório de erros (morg_relatorio_erros.py, P3): o que leva e o que fica de fora.

Pesquisa em docs/pesquisa/relatorio-de-erros.md: o resumo; quando e onde (hora ISO 8601, versões); o que estava a
fazer; a exceção como o OpenTelemetry (tipo, mensagem, stack trace, gravidade); o registo do arranque; e os campos
que quem envia preenche. A limpeza (RFC 9457, RGPD) troca a pasta pessoal por ~ e os nomes por <utilizador>, e os
dados do painel em base64 não entram. A conta falsa é a "Ana".
"""

import contextlib
import importlib.util
import json
import sys
import tempfile
import types
import unittest
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest import mock

from sistema_falso import PASTA_PACK

if str(PASTA_PACK) not in sys.path:  # o módulo importa o morg_win32, da mesma pasta
    sys.path.insert(0, str(PASTA_PACK))
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


def registo_do_windows_falso(valores):
    """O winreg com a chave CurrentVersion num dicionário (None: sem acesso); um valor em falta dá OSError."""
    def abrir(raiz, caminho):
        if valores is None:
            raise OSError("sem acesso")
        return contextlib.nullcontext(valores)

    def ler(chave, nome):
        if nome not in chave:
            raise FileNotFoundError(nome)
        return chave[nome], 1

    return types.SimpleNamespace(HKEY_LOCAL_MACHINE="HKLM", OpenKey=abrir, QueryValueEx=ler)


class NomeDoWindows(unittest.TestCase):
    """O Windows 11 diz-se 10.0 (o platform.platform() do Python 3.11 escreve "Windows-10"); só o build o distingue:
    a tabela de lançamentos do Windows 11 começa no 22000 (docs/pesquisa/relatorio-de-erros.md)."""

    def test_windows_11_a_partir_do_build_22000(self):
        self.assertEqual(relatorio.nome_do_windows(26200, 9457, "25H2"), "Windows 11 (build 26200.9457, 25H2)")
        self.assertEqual(relatorio.nome_do_windows(22000, 194, "21H2"), "Windows 11 (build 22000.194, 21H2)")
        self.assertEqual(relatorio.nome_do_windows(21999, 1, ""), "Windows 10 (build 21999.1)")
        self.assertEqual(relatorio.nome_do_windows(19045, 3803, "22H2"), "Windows 10 (build 19045.3803, 22H2)")

    def test_le_o_registo_ou_cai_no_platform(self):
        valores = {"CurrentBuild": "26200", "UBR": 9457, "DisplayVersion": "25H2"}
        self.assertEqual(relatorio.windows_instalado(registo_do_windows_falso(valores)),
                         "Windows 11 (build 26200.9457, 25H2)")
        self.assertEqual(relatorio.windows_instalado(registo_do_windows_falso({"CurrentBuild": "19041"})),
                         "Windows 10 (build 19041)")  # um Windows 10 antigo, sem UBR nem DisplayVersion
        with mock.patch.object(relatorio.platform, "platform", return_value="Windows-10-10.0.26200-SP0"):
            self.assertEqual(relatorio.windows_instalado(registo_do_windows_falso(None)), "Windows-10-10.0.26200-SP0")
            self.assertEqual(relatorio.windows_instalado(registo_do_windows_falso({})), "Windows-10-10.0.26200-SP0")

    def test_o_relatorio_usa_o_nome_certo(self):
        with mock.patch.object(relatorio, "windows_instalado", return_value="Windows 11 (build 26200.9457, 25H2)"):
            texto = relatorio.montar_relatorio(ValueError("x"), ["bar_helper.py"], AGORA, versao="v", registo="",
                                               casa=CASA, nomes=[])
        self.assertIn("- Windows: Windows 11 (build 26200.9457, 25H2)\n", texto)


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

    def test_alternar_o_aviso_pelo_alt_esc_v(self):
        # Alt+Esc, V (P3b): troca "erros = mostrar" <-> "esconder" e mantém o resto do arranque.txt.
        with tempfile.TemporaryDirectory() as pasta:
            arranque = Path(pasta) / "arranque.txt"
            arranque.write_text("# erros = esconder\nnome = Ana\nerros = mostrar\nclaude = mostrar\n", encoding="utf-8-sig")
            self.assertEqual(relatorio.alternar_aviso(arranque), "desligado")
            self.assertEqual(arranque.read_text(encoding="utf-8-sig"),
                             "# erros = esconder\nnome = Ana\nerros = esconder\nclaude = mostrar\n")
            self.assertEqual(relatorio.alternar_aviso(arranque), "ligado")
            self.assertIn("\nerros = mostrar\n", arranque.read_text(encoding="utf-8-sig"))
            arranque.write_text("nome = Ana\n", encoding="utf-8")  # sem a linha: estava ligado, passa a desligado
            self.assertEqual(relatorio.alternar_aviso(arranque), "desligado")
            self.assertEqual(arranque.read_text(encoding="utf-8"), "nome = Ana\nerros = esconder\n")
            arranque.unlink()  # sem ficheiro: cria-o
            self.assertEqual(relatorio.alternar_aviso(arranque), "desligado")
            with mock.patch.object(relatorio, "ARRANQUE", arranque):  # o Alt+Esc, V chama-o sem argumentos
                self.assertEqual(relatorio.alternar_aviso(), "ligado")

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


class TratarErro(unittest.TestCase):
    """O erro que chega ao topo do bar_helper.py: cópia sempre; popup (se ligado); com "Sim", "Guardar como"."""

    def setUp(self):
        pasta = tempfile.TemporaryDirectory()
        self.addCleanup(pasta.cleanup)
        self.pasta = Path(pasta.name)
        self.arranque = self.pasta / "arranque.txt"
        self.arranque.write_text("nome = Ana Silva\n", encoding="utf-8")
        for nome, valor in (("PASTA_DOS_ERROS", self.pasta / "erros"), ("ARRANQUE", self.arranque),
                            ("INSTALACAO", self.pasta / "instalacao.json"),
                            ("REGISTO_DO_ARRANQUE", self.pasta / ".layout-restore.log")):
            trocar = mock.patch.object(relatorio, nome, valor)
            trocar.start()
            self.addCleanup(trocar.stop)
        self.perguntas, self.escolhas = [], []

    def tratar(self, resposta=True, destino=None):
        def perguntar(resumo):
            self.perguntas.append(resumo)
            return resposta

        def escolher(nome, pasta):
            self.escolhas.append((nome, pasta))
            return destino

        with mock.patch.dict("os.environ", {"USERNAME": "Ana"}):
            return relatorio.tratar_erro(ValueError("Ana Silva rebentou"), ["bar_helper.py", "boot"], AGORA,
                                         perguntar=perguntar, escolher=escolher)

    def test_com_sim_guarda_onde_quem_usa_escolheu(self):
        destino = self.pasta / "para-a-issue.md"
        copia = self.tratar(destino=destino)
        self.assertEqual(self.perguntas, ["boot: ValueError"])
        self.assertEqual(self.escolhas, [(copia.name, Path.home() / "Documents")])
        self.assertEqual(destino.read_text(encoding="utf-8"), copia.read_text(encoding="utf-8"))
        self.assertIn("<utilizador> rebentou", copia.read_text(encoding="utf-8"))

    def test_com_nao_ou_cancelar_so_fica_a_copia(self):
        self.tratar(resposta=False)
        self.assertEqual(self.escolhas, [])
        copia = self.tratar(destino=None)  # "Guardar como" cancelado
        self.assertTrue(copia.exists())

    def test_popup_desligado_nao_pergunta_mas_guarda(self):
        self.arranque.write_text("erros = esconder\n", encoding="utf-8")
        copia = self.tratar()
        self.assertEqual(self.perguntas, [])
        self.assertTrue(copia.exists())

    def test_nomes_da_pessoa_vem_da_conta_e_do_arranque(self):
        with mock.patch.dict("os.environ", {"USERNAME": "ana"}):
            self.assertEqual(relatorio.nomes_da_pessoa(), ["ana", "Ana Silva"])
        self.arranque.unlink()
        with mock.patch.dict("os.environ", {}, clear=True):
            self.assertEqual(relatorio.nomes_da_pessoa(), [])


class ColaComOWindows(unittest.TestCase):
    """O popup (MessageBoxW) e o "Guardar como" (GetSaveFileNameW), com o Windows simulado."""

    def test_popup_sim_e_nao(self):
        for resposta, esperado in ((6, True), (7, False)):  # IDYES, IDNO
            janela = mock.Mock(**{"MessageBoxW.return_value": resposta})
            with self.subTest(resposta=resposta), mock.patch.object(relatorio, "user32", janela):
                self.assertEqual(relatorio.perguntar_se_guarda("boot: ValueError"), esperado)
                _, texto, titulo, estilo = janela.MessageBoxW.call_args.args
                self.assertIn("boot: ValueError", texto)
                self.assertEqual(titulo, "Morg Keys: erro")
                self.assertEqual(estilo, 0x4 | 0x10 | 0x40000)  # Sim/Não, ícone de erro, por cima de tudo

    def test_guardar_como_escolhido_ou_cancelado(self):
        for devolve, esperado in ((1, Path("erro-1.md")), (0, None)):
            dialogo = mock.Mock(**{"GetSaveFileNameW.return_value": devolve})
            with self.subTest(devolve=devolve), mock.patch.object(relatorio, "comdlg32", dialogo):
                self.assertEqual(relatorio.pedir_destino("erro-1.md", Path("C:/Docs")), esperado)
                estrutura = dialogo.GetSaveFileNameW.call_args.args[0]._obj
                self.assertEqual(estrutura.lpstrInitialDir, str(Path("C:/Docs")))
                self.assertEqual(estrutura.lpstrDefExt, "md")
                self.assertTrue(estrutura.Flags & 0x2)  # OFN_OVERWRITEPROMPT: pergunta antes de substituir


class Instalar(unittest.TestCase):
    """bar_helper.py instala o gancho: os erros que chegam ao topo viram relatório; os rebentamentos em C vão
    para um ficheiro (faulthandler)."""

    def test_o_registo_dos_rebentamentos_nao_cresce_sem_fim(self):
        # Cada arranque acrescentava linhas ao rebentamentos.log (2026-10-31); acima do limite passa a .antigo.log.
        pasta = tempfile.TemporaryDirectory()
        self.addCleanup(pasta.cleanup)
        registo = Path(pasta.name) / "rebentamentos.log"
        registo.write_bytes(b"x" * (relatorio.LIMITE_DOS_REBENTAMENTOS + 1))
        self.instalar(lambda erro, argv: None, Path(pasta.name))
        self.assertFalse(registo.exists())
        self.assertEqual((Path(pasta.name) / "rebentamentos.antigo.log").stat().st_size,
                         relatorio.LIMITE_DOS_REBENTAMENTOS + 1)
        registo.write_bytes(b"pequeno")
        self.instalar(lambda erro, argv: None, Path(pasta.name))
        self.assertEqual(registo.read_bytes(), b"pequeno")  # abaixo do limite fica

    def instalar(self, tratar, pasta_dos_erros=None):
        ganchos = {}
        pasta = tempfile.TemporaryDirectory()  # antes de simular o os.open, que o tempfile também usa
        self.addCleanup(pasta.cleanup)
        pasta_dos_erros = pasta_dos_erros or Path(pasta.name)
        with mock.patch("sys.excepthook", None), mock.patch.object(relatorio, "faulthandler") as falta, \
                mock.patch.object(relatorio.os, "open", return_value=7), \
                mock.patch.object(relatorio, "PASTA_DOS_ERROS", pasta_dos_erros):
            relatorio.instalar(["bar_helper.py", "boot"], tratar)
            ganchos["gancho"] = __import__("sys").excepthook
            falta.enable.assert_called_once_with(file=7)
        return ganchos["gancho"]

    def test_o_erro_vira_relatorio_e_continua_a_aparecer_no_stderr(self):
        tratados = []
        gancho = self.instalar(lambda erro, argv: tratados.append((type(erro), argv)))
        with mock.patch("sys.__excepthook__") as normal:
            gancho(ValueError, ValueError("x"), None)
            gancho(KeyboardInterrupt, KeyboardInterrupt(), None)  # Ctrl+C não é um erro
        self.assertEqual(tratados, [(ValueError, ["bar_helper.py", "boot"])])
        self.assertEqual(normal.call_count, 2)

    def test_se_o_relatorio_falhar_o_erro_original_aparece_na_mesma(self):
        def falha(erro, argv):
            raise OSError("disco cheio")

        gancho = self.instalar(falha)
        with mock.patch("sys.__excepthook__") as normal:
            gancho(ValueError, ValueError("x"), None)
        normal.assert_called_once()

    def test_erro_de_teste(self):
        with self.assertRaises(RuntimeError):
            relatorio.erro_de_teste()


if __name__ == "__main__":
    unittest.main()
