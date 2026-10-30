"""Portão do git (pre-commit): a identidade de cada commit é pública.

O e-mail tem de ser o noreply do GitHub e o nome do autor não pode ter termos da lista negra.
Uso: py -I scripts/portoes/identidade.py   Sai com 1 se recusar e com 0 se aceitar.
"""

import subprocess
import sys
from pathlib import Path

# Com `py -I` a pasta do script não entra no sys.path: sem isto o import seguinte falhava.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lista_negra

SUFIXO_NOREPLY = "@users.noreply.github.com"


def ler_config(chave, correr=None):
    """Valor de `git config <chave>` (texto vazio se não houver)."""
    return (correr or subprocess.run)(["git", "config", "--get", chave], capture_output=True, text=True,
                                      encoding="utf-8", check=False).stdout.strip()


def erros(email, nome, caminho_lista):
    """Lista dos motivos para recusar (vazia se a identidade estiver certa)."""
    motivos = []
    if not email.endswith(SUFIXO_NOREPLY):
        motivos.append(f"ERRO: user.email é '{email}'. Use o e-mail noreply do GitHub: "
                       f"git config user.email <id>+<conta>{SUFIXO_NOREPLY}")
    codigo, mensagem = lista_negra.verificar(nome, "o nome do autor (user.name)", caminho_lista)
    if codigo:
        motivos.append(mensagem)
    return motivos


def main():
    motivos = erros(ler_config("user.email"), ler_config("user.name"), lista_negra.caminho_da_lista())
    for motivo in motivos:
        lista_negra.escrever_erro(motivo)
    return 1 if motivos else 0


if __name__ == "__main__":
    sys.exit(main())
