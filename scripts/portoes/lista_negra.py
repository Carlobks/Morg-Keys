"""Portão do git: nada da lista negra (nomes, contas, e-mails reais) entra num commit do repositório público.

A lista fica FORA do repositório: `git config morg.listaNegra <ficheiro>`, um termo por linha, `#` para
comentários. Sem lista configurada só avisa; configurada mas em falta, recusa (falhar fechado).
Uso (nos hooks): <texto> | py -I scripts/portoes/lista_negra.py "<o que se verifica>"
Sai com 1 se encontrar um termo e com 0 nos outros casos.
"""

import re
import subprocess
import sys
from pathlib import Path


def escrever_erro(texto):
    """Escreve no stderr em UTF-8: no Windows a página de código local estragaria os acentos (A16)."""
    sys.stderr.flush()
    sys.stderr.buffer.write((texto + "\n").encode("utf-8"))
    sys.stderr.flush()


def caminho_da_lista(correr=None):
    """Ficheiro da lista negra configurado no git; None se não houver."""
    saida = (correr or subprocess.run)(["git", "config", "--get", "morg.listaNegra"], capture_output=True,
                                       text=True, encoding="utf-8", check=False).stdout.strip()
    return Path(saida).expanduser() if saida else None


def ler_termos(caminho):
    """Termos da lista (sem linhas vazias nem comentários)."""
    linhas = caminho.read_text(encoding="utf-8-sig").splitlines()
    return [linha.strip() for linha in linhas if linha.strip() and not linha.lstrip().startswith("#")]


def termos_encontrados(texto, termos):
    """Termos que aparecem no texto como palavra inteira, sem olhar a maiúsculas."""
    return [termo for termo in termos
            if re.search(r"(?<!\w)" + re.escape(termo) + r"(?!\w)", texto, re.IGNORECASE)]


def verificar(texto, rotulo, caminho):
    """(código de saída, mensagem) para o texto; `rotulo` diz o que é (ex.: "a mensagem do commit")."""
    if caminho is None:
        return 0, f"AVISO: sem lista negra (git config morg.listaNegra): {rotulo} não foi verificado."
    if not caminho.is_file():
        return 1, f"ERRO: a lista negra configurada ({caminho}) não existe. Corrija o git config morg.listaNegra."
    achados = termos_encontrados(texto, ler_termos(caminho))
    if achados:
        return 1, f"ERRO: há dados da lista negra ({rotulo}): {', '.join(achados)}. Troque-os por um nome fictício."
    return 0, ""


def main(argv, entrada=None):
    rotulo = argv[1] if len(argv) > 1 else "o texto"
    texto = (entrada or sys.stdin.buffer).read().decode("utf-8", errors="replace")
    codigo, mensagem = verificar(texto, rotulo, caminho_da_lista())
    if mensagem:
        escrever_erro(mensagem)
    return codigo


if __name__ == "__main__":
    sys.exit(main(sys.argv))
