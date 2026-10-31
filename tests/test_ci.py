"""O CI do GitHub (ML14): o mesmo scripts/testar.ps1 do pre-commit num Windows limpo, o gitleaks e os estragos.

Lido como texto (o projeto não tem biblioteca de YAML). Cada regra tem o motivo ao lado:
- as actions ficam fixadas por SHA de commit com a versão em comentário: uma tag pode ser mudada por quem a tem;
- o token só lê o repositório (permissions: contents: read) e o checkout não guarda a credencial;
- as ferramentas têm versões fixas, as mesmas da máquina de quem desenvolve, para o CI não ficar verde por sorte;
- o testar.ps1 e os estragos aceitam MORG_PY, porque o Windows do GitHub não garante o C:\\Windows\\py.exe;
- o gitleaks é descarregado com o hash conferido, nunca por um "curl | sh".
"""

import os
import re
import subprocess
import unittest

from carregar_por_caminho import RAIZ

WORKFLOW = RAIZ / ".github" / "workflows" / "ci.yml"
SHA = re.compile(r"^\s*-?\s*uses: [\w.-]+/[\w.-]+@[0-9a-f]{40} # v\d+\.\d+\.\d+$")
VERSOES = ("python-version: \"3.11.9\"", "node-version: \"24.14.1\"", "coverage==7.17.0", "ruff==0.17.2",
           "Pester -RequiredVersion 6.2.0", "PSScriptAnalyzer -RequiredVersion 1.25.0", "npm ci")


def texto(caminho):
    return caminho.read_bytes().decode("utf-8")


def tarefa(nome):
    """Texto da tarefa `nome:` do workflow, até à tarefa seguinte."""
    partes = re.split(r"^  (?=[\w-]+:$)", texto(WORKFLOW).split("\njobs:\n", 1)[1], flags=re.MULTILINE)
    return next(p for p in partes if p.startswith(nome + ":"))


class Workflow(unittest.TestCase):

    def test_cada_action_fixada_por_sha_com_a_versao(self):
        usos = [linha for linha in texto(WORKFLOW).splitlines() if "uses:" in linha]
        self.assertGreaterEqual(len(usos), 3)
        for linha in usos:
            with self.subTest(linha=linha):
                self.assertRegex(linha, SHA)

    def test_o_token_so_le_e_o_checkout_nao_guarda_a_credencial(self):
        conteudo = texto(WORKFLOW)
        self.assertIn("\npermissions:\n  contents: read\n", conteudo)
        self.assertEqual(conteudo.count("actions/checkout@"), conteudo.count("persist-credentials: false"))
        self.assertNotIn("pull_request_target", conteudo)

    def test_a_tarefa_testar_corre_o_testar_ps1_com_as_versoes_fixas(self):
        testar = tarefa("testar")
        self.assertIn("runs-on: windows-latest", testar)
        self.assertIn("MORG_PY: ${{ steps.python.outputs.python-path }}", testar)
        self.assertIn("-File scripts/testar.ps1", testar)
        self.assertIn("fetch-depth: 0", testar)  # os testes dos docs conferem hashes do histórico
        # Os testes da guarda do git exigem os portões ligados, como no README; o checkout não os liga.
        self.assertIn("git config core.hooksPath .githooks", testar)
        for versao in VERSOES:
            with self.subTest(versao=versao):
                self.assertIn(versao, testar)

    def test_o_gitleaks_varre_o_historico_com_o_hash_conferido(self):
        segredos = tarefa("segredos")
        self.assertIn("gitleaks_8.30.1_linux_x64.tar.gz", segredos)
        self.assertRegex(segredos, r'echo "[0-9a-f]{64}  gitleaks\.tar\.gz" \| sha256sum -c -')
        self.assertIn("fetch-depth: 0", segredos)
        self.assertIn("./gitleaks git", segredos)
        self.assertNotRegex(texto(WORKFLOW), r"\| *(ba)?sh\b")

    def test_os_estragos_correm_uma_vez_por_semana(self):
        self.assertRegex(texto(WORKFLOW), r'\n  schedule:\n    - cron: "[\d ]+\* \* 1"')
        estragos = tarefa("estragos")
        self.assertIn("github.event_name == 'schedule'", estragos)
        self.assertIn("scripts/estragos.py", estragos)
        self.assertIn("MORG_PY: ${{ steps.python.outputs.python-path }}", estragos)
        self.assertIn("github.event_name != 'schedule'", tarefa("testar"))


class MorgPy(unittest.TestCase):

    def test_testar_ps1_aceita_morg_py(self):
        self.assertIn("$Py = if ($env:MORG_PY) { $env:MORG_PY } else { 'C:\\Windows\\py.exe' }",
                      texto(RAIZ / "scripts" / "testar.ps1"))

    def test_testar_ps1_falha_fechado_sem_o_python(self):
        # Com um MORG_PY errado, o "& $Py" falhava sem mexer no $LASTEXITCODE e o resultado dizia "OK" (ML14).
        ambiente = {**os.environ, "MORG_PY": r"C:\nao-existe\python.exe"}
        r = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File",
                            str(RAIZ / "scripts" / "testar.ps1")], capture_output=True, env=ambiente, timeout=300,
                           check=False)
        saida = r.stdout.decode("utf-8", errors="replace")
        self.assertEqual(r.returncode, 1, saida[-500:])
        self.assertIn("FALHOU: Python n", saida)  # o "ã" sai na página de código da consola, que varia

    def test_estragos_aceita_morg_py(self):
        self.assertIn('os.environ.get("MORG_PY", "py")', texto(RAIZ / "scripts" / "estragos.py"))


if __name__ == "__main__":
    unittest.main()
