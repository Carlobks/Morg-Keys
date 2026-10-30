"""Nenhum dado pessoal no repositório público (regra "Nunca" do Morg Laws; ADR 0002).

Três verificações sobre os ficheiros de texto do repositório (os guardados e os novos ainda por guardar):
- caminhos de uma pasta pessoal do Windows (`C:\\Users\\<conta>`) com uma conta que não seja um dos nomes de
  exemplo de CONTAS_DE_EXEMPLO; marcadores como `<conta>`, `{{HOME}}` ou `%USERPROFILE%` são aceites;
- endereços de e-mail que não sejam o noreply do GitHub ou da Anthropic, ou um domínio de exemplo (uma versão
  npm como `pacote@1.2.3` não conta);
- os termos da lista negra, que fica FORA do repositório (os nomes não podem estar aqui):
  `git config morg.listaNegra <ficheiro>`, um termo por linha, `#` para comentários. Sem lista, só correm as
  duas primeiras.

Os testes e exemplos usam um nome fictício. Correr: py -I -m unittest discover -s tests -p test_dados_pessoais.py -v
"""

import re
import subprocess
import unittest
from pathlib import Path

RAIZ_REPOSITORIO = Path(__file__).resolve().parent.parent
EXTENSOES_BINARIAS = (".ttf", ".png", ".bmp", ".ico", ".exe", ".jpg", ".woff2")
CAMINHOS_EXCLUIDOS = ("vendor/", "package-lock.json")
# Contas fictícias usadas nos exemplos e nos testes (o nome fictício da saudação é "Ana").
# ("a" vem de `a\\.b`, a mesma conta escrita como expressão regular.)
CONTAS_DE_EXEMPLO = ("nome", "joao", "u", "a", "a.b", "ana", "public", "default")
CONTA_EM_CAMINHO = re.compile(r"[A-Za-z]:[\\/]+Users[\\/]+([^\s\\/<{%$`'\"();,:]+)", re.IGNORECASE)
EMAIL = re.compile(r"[\w.+-]+@[\w-]+(?:\.[\w-]+)*\.[A-Za-z]{2,}\b")
EMAILS_ACEITES = re.compile(r"@(?:users\.noreply\.github\.com|anthropic\.com|example\.(?:com|org|net))$", re.IGNORECASE)


def ficheiros_do_repositorio():
    """Caminhos (relativos) dos ficheiros de texto guardados e dos novos que o .gitignore não esconde."""
    saida = subprocess.run(["git", "ls-files", "--cached", "--others", "--exclude-standard"], cwd=RAIZ_REPOSITORIO,
                           capture_output=True, text=True, encoding="utf-8", check=True).stdout
    return [caminho for caminho in dict.fromkeys(saida.splitlines())
            if (RAIZ_REPOSITORIO / caminho).is_file()
            and not caminho.endswith(EXTENSOES_BINARIAS)
            and not any(excluido in caminho for excluido in CAMINHOS_EXCLUIDOS)]


def termos_da_lista_negra():
    """Termos do ficheiro em `git config morg.listaNegra`; lista vazia se não houver."""
    saida = subprocess.run(["git", "config", "--get", "morg.listaNegra"], cwd=RAIZ_REPOSITORIO,
                           capture_output=True, text=True, encoding="utf-8", check=False).stdout.strip()
    if not saida:
        return []
    linhas = Path(saida).expanduser().read_text(encoding="utf-8-sig").splitlines()
    return [linha.strip() for linha in linhas if linha.strip() and not linha.lstrip().startswith("#")]


def achados(padrao, aceite=lambda achado: False):
    """{ficheiro: [linhas]} onde o padrão aparece (menos os achados que `aceite` deixa passar)."""
    resultado = {}
    for caminho in ficheiros_do_repositorio():
        texto = (RAIZ_REPOSITORIO / caminho).read_text(encoding="utf-8-sig", errors="replace")
        for numero, linha in enumerate(texto.splitlines(), 1):
            if any(not aceite(achado) for achado in padrao.finditer(linha)):
                resultado.setdefault(caminho, []).append(numero)
    return resultado


def conta_de_exemplo(achado):
    """True se o caminho `C:\\Users\\<conta>` usa uma das contas fictícias."""
    return achado.group(1).lower() in CONTAS_DE_EXEMPLO


def email_aceite(achado):
    """True se o e-mail é o noreply do GitHub/Anthropic ou de um domínio de exemplo."""
    return bool(EMAILS_ACEITES.search(achado.group(0)))


class SemDadosPessoais(unittest.TestCase):

    def test_ha_ficheiros_para_verificar(self):
        self.assertGreater(len(ficheiros_do_repositorio()), 20)

    def test_sem_caminhos_de_pastas_pessoais(self):
        self.assertEqual(achados(CONTA_EM_CAMINHO, conta_de_exemplo), {},
                         "use <pasta do repositório>, %USERPROFILE%, {{HOME}} ou uma conta de exemplo")

    def test_sem_emails_pessoais(self):
        self.assertEqual(achados(EMAIL, email_aceite), {}, "só o noreply do GitHub/Anthropic ou example.com")

    def test_sem_termos_da_lista_negra(self):
        for numero, termo in enumerate(termos_da_lista_negra(), 1):
            padrao = re.compile(r"(?<!\w)" + re.escape(termo) + r"(?!\w)", re.IGNORECASE)
            with self.subTest(termo=f"termo n.º {numero} da lista negra"):
                self.assertEqual(achados(padrao), {}, "dado pessoal: troque pelo nome fictício ou por um papel")


if __name__ == "__main__":
    unittest.main()
