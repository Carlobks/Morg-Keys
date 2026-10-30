"""Portão do push (scripts/portoes/antes_do_push.py): nada sai desta máquina sem as verificações.

Lista os ficheiros de cada commit a enviar, corre o gitleaks nesses commits (falha fechado sem ele) e só trava
um aviso crítico ou alto do npm audit que não esteja na linha de base. Os comandos externos são simulados.
"""

import io
import json
import runpy
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

from carregar_por_caminho import PASTA_PORTOES, carregar_portao

push = carregar_portao("antes_do_push")
A, B, ZEROS = "a" * 40, "b" * 40, "0" * 40


def relatorio(*avisos):
    """Relatório do npm audit --json com os avisos (source, severity) dados."""
    via = [{"source": fonte, "severity": gravidade, "name": "pacote", "title": "falha"} for fonte, gravidade in avisos]
    return json.dumps({"vulnerabilities": {"pacote": {"via": [*via, "outro-pacote"]}}})


class Intervalos(unittest.TestCase):

    def test_ramo_existente_ramo_novo_e_apagar(self):
        linhas = [f"refs/heads/exp/a {B} refs/heads/exp/a {A}", f"refs/heads/novo {B} refs/heads/novo {ZEROS}",
                  f"(delete) {ZEROS} refs/heads/velho {A}", ""]
        self.assertEqual(push.intervalos(linhas), [("refs/heads/exp/a", [f"{A}..{B}"]),
                                                   ("refs/heads/novo", [B, "--not", "--remotes"])])


class Gitleaks(unittest.TestCase):

    def test_usa_o_do_path_primeiro(self):
        self.assertEqual(push.achar_gitleaks(lambda nome: "C:/x/gitleaks.exe", []), "C:/x/gitleaks.exe")

    def test_procura_na_pasta_do_winget(self):
        self.assertEqual(push.achar_gitleaks(lambda nome: None, [Path("C:/w/gitleaks.exe")]), "C:\\w\\gitleaks.exe")

    def test_por_omissao_procura_a_pasta_do_pacote_do_winget(self):
        with tempfile.TemporaryDirectory() as pasta:
            exe = Path(pasta) / "Gitleaks.Gitleaks_8wekyb3d8bbwe" / "gitleaks.exe"
            exe.parent.mkdir()
            exe.write_bytes(b"")
            with mock.patch.object(push, "PASTA_DO_WINGET", Path(pasta)):
                self.assertEqual(push.achar_gitleaks(lambda nome: None), str(exe))

    def test_sem_gitleaks_nao_ha_caminho(self):
        self.assertIsNone(push.achar_gitleaks(lambda nome: None, []))


class Auditoria(unittest.TestCase):

    def test_so_trava_critico_ou_alto_fora_da_base(self):
        texto = relatorio((1, "critical"), (2, "high"), (3, "moderate"))
        self.assertEqual(push.avisos_novos(texto, {"1"}), ["2 high pacote: falha"])

    def test_relatorio_ilegivel_falha_fechado(self):
        for texto in ("", "não é json", json.dumps({"error": {"code": "ENOTFOUND"}})):
            with self.subTest(texto=texto), self.assertRaises(ValueError):
                push.avisos_novos(texto, set())

    def test_sem_vulnerabilidades_passa(self):
        self.assertEqual(push.avisos_novos(json.dumps({"vulnerabilities": {}}), set()), [])

    def test_le_a_linha_de_base(self):
        with tempfile.TemporaryDirectory() as pasta:
            base = Path(pasta) / "base.txt"
            self.assertEqual(push.ler_base(base), set())
            base.write_text("# comentário\n1096302  # aviso antigo\n\n", encoding="utf-8")
            self.assertEqual(push.ler_base(base), {"1096302"})


class Corrida(unittest.TestCase):
    """main(): o que o hook faz de ponta a ponta, com o git, o gitleaks e o npm simulados."""

    def correr_main(self, gitleaks_sai=0, npm_saida=None, gitleaks="gitleaks.exe", lock=True):
        chamadas = []

        def correr(comando, **_):
            chamadas.append(comando)
            if comando[0] == "git":
                return SimpleNamespace(returncode=0, stdout="b1 commit\nM\tscripts/a.py\n")
            if comando[0] == "gitleaks.exe":
                return SimpleNamespace(returncode=gitleaks_sai, stdout="")
            return SimpleNamespace(returncode=1, stdout=relatorio() if npm_saida is None else npm_saida)

        falso = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
        with tempfile.TemporaryDirectory() as pasta, mock.patch("sys.stderr", falso):
            raiz = Path(pasta)
            if lock:
                (raiz / "package-lock.json").write_text("{}", encoding="utf-8")
            entrada = io.BytesIO(f"refs/heads/exp/a {B} refs/heads/exp/a {A}\n".encode())
            codigo = push.main(entrada, correr, lambda: gitleaks, lambda nome: "npm.cmd", raiz)
        falso.flush()
        return codigo, falso.buffer.getvalue().decode("utf-8"), chamadas

    def test_tudo_limpo_passa_e_mostra_os_ficheiros(self):
        codigo, erro, chamadas = self.correr_main()
        self.assertEqual(codigo, 0)
        self.assertIn("scripts/a.py", erro)
        self.assertIn(["gitleaks.exe", "git", f"--log-opts={A}..{B}", "--redact", "--no-banner"], chamadas)

    def test_segredo_encontrado_trava(self):
        codigo, erro, _ = self.correr_main(gitleaks_sai=1)
        self.assertEqual(codigo, 1)
        self.assertIn("possível segredo", erro)

    def test_sem_gitleaks_trava(self):
        codigo, erro, _ = self.correr_main(gitleaks=None)
        self.assertEqual(codigo, 1)
        self.assertIn("gitleaks não está instalado", erro)

    def test_aviso_novo_trava(self):
        codigo, erro, _ = self.correr_main(npm_saida=relatorio((9, "high")))
        self.assertEqual(codigo, 1)
        self.assertIn("9 high", erro)

    def test_npm_audit_ilegivel_trava(self):
        codigo, erro, _ = self.correr_main(npm_saida="")
        self.assertEqual(codigo, 1)
        self.assertIn("npm audit", erro)

    def test_sem_package_lock_nao_corre_o_npm(self):
        codigo, _, chamadas = self.correr_main(lock=False)
        self.assertEqual(codigo, 0)
        self.assertFalse(any(comando[0] == "npm.cmd" for comando in chamadas))

    def test_corre_como_script(self):
        entrada = io.TextIOWrapper(io.BytesIO(b""), encoding="utf-8")
        resposta = SimpleNamespace(returncode=0, stdout=json.dumps({"vulnerabilities": {}}))
        with mock.patch("sys.stdin", entrada), mock.patch("subprocess.run", return_value=resposta), \
                mock.patch("shutil.which", return_value="C:/x/gitleaks.exe"), \
                mock.patch("sys.stderr", io.TextIOWrapper(io.BytesIO(), encoding="utf-8")), \
                self.assertRaises(SystemExit) as saida:
            runpy.run_path(str(PASTA_PORTOES / "antes_do_push.py"), run_name="__main__")
        self.assertEqual(saida.exception.code, 0)


if __name__ == "__main__":
    unittest.main()
