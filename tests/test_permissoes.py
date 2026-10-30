"""Permissões do agente em três colunas (Morg Laws; livro do Akita, #40, #51, #76, #79, #81).

- **deny** (nunca): ler segredos (`.env`, chaves, credenciais, a lista negra fora do repositório);
- **ask** (pergunta antes): push, instalar pacotes ou programas, mexer nas próprias regras de segurança;
- **allow** (sem perguntar): só leitura e o comando de testes.
As regras vivem em .claude/settings.json (vai no repositório, vale para quem o clonar). As de cada máquina ficam
em .claude/settings.local.json, que só pode apertar.
"""

import json
import re
import unittest

from carregar_por_caminho import RAIZ

NUNCA = {"Read(**/.env)", "Read(**/.env.*)", "Read(**/*.pem)", "Read(**/*.key)", "Read(~/.ssh/**)",
         "Read(~/.claude/.credentials.json)", "Read(~/.config/morg-keys/**)"}
PERGUNTA = {"Bash(git push)", "Bash(git push *)", "PowerShell(git push)", "PowerShell(git push *)",
            "Bash(npm install *)", "Bash(npm i *)", "Bash(npm ci*)", "Bash(npx *)", "Bash(pip install *)",
            "Bash(winget install *)", "PowerShell(winget install *)", "PowerShell(Install-Module *)",
            "Edit(.claude/settings.json)", "Edit(.claude/hooks/**)", "Edit(.githooks/**)"}
# O que nunca pode estar em "allow": publica (push, PR), instala, apaga, salta os portões ou abre tudo.
PERIGOSO = re.compile(r"push|install|\bnpx\b|\brm\b|Remove-Item|--no-verify|reset --hard|^\w+\(\*\)$|\bgh pr \*"
                      r"|\bpy(?:thon)?(?:\.exe)? (?:-\w+ )*-\)"  # Python lido do stdin: corre qualquer código

                      r"|\bgh pr (?:create|merge|close|edit|comment|review|ready)", re.IGNORECASE)


def permissoes(nome):
    caminho = RAIZ / ".claude" / nome
    if not caminho.is_file():
        return {}
    return json.loads(caminho.read_text(encoding="utf-8")).get("permissions", {})


class TresColunas(unittest.TestCase):

    def test_nunca_le_segredos(self):
        self.assertEqual(NUNCA - set(permissoes("settings.json").get("deny", [])), set())

    def test_pergunta_antes_do_que_nao_tem_volta(self):
        self.assertEqual(PERGUNTA - set(permissoes("settings.json").get("ask", [])), set())

    def test_allow_so_tem_leituras_e_testes(self):
        for nome in ("settings.json", "settings.local.json"):
            for regra in permissoes(nome).get("allow", []):
                with self.subTest(ficheiro=nome, regra=regra):
                    self.assertIsNone(PERIGOSO.search(regra), "isto pertence à coluna ask ou deny")

    def test_o_local_nao_desfaz_o_deny_nem_o_ask(self):
        projeto = permissoes("settings.json")
        local_allow = set(permissoes("settings.local.json").get("allow", []))
        self.assertEqual(local_allow & (set(projeto.get("deny", [])) | set(projeto.get("ask", []))), set())

    def test_segredos_tambem_fora_do_git(self):
        ignorados = (RAIZ / ".gitignore").read_text(encoding="utf-8").splitlines()
        for padrao in (".env", ".env.*", "*.pem", "*.key"):
            with self.subTest(padrao=padrao):
                self.assertIn(padrao, ignorados)


if __name__ == "__main__":
    unittest.main()
