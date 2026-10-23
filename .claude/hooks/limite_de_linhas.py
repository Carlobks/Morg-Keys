"""Hook PreToolUse (Write/Edit): recusa que um ficheiro de código do projeto fique acima de 500 linhas.

Só bloqueia se o ficheiro passar o limite **e crescer**: encolher um ficheiro antigo grande (refatoração)
é sempre permitido. As edições feitas pela shell escapam a este hook; apanha-as o teste
tests/test_ficheiros_texto.py (limite de linhas em todos os ficheiros).
Sai com 2 (bloqueia) e explica no stderr; sai com 0 nos outros casos.
"""

import json
import sys
from pathlib import Path

LIMITE = 500
EXTENSOES = {".py", ".ps1", ".psm1", ".js", ".mjs", ".html", ".css", ".cmd", ".bat", ".yaml", ".md"}
_RAIZ = Path(__file__).resolve().parents[2]


def contar_linhas(texto):
    """Número de linhas como o editor as mostra (a última sem quebra também conta)."""
    return len(texto.splitlines())


def texto_depois(ferramenta, entrada, texto_antes):
    """Texto que o ficheiro terá depois do Write/Edit pedido; None se não der para saber."""
    if ferramenta == "Write":
        return entrada.get("content", "")
    antigo, novo = entrada.get("old_string"), entrada.get("new_string")
    if antigo is None or novo is None or antigo not in texto_antes:
        return None
    if entrada.get("replace_all"):
        return texto_antes.replace(antigo, novo)
    return texto_antes.replace(antigo, novo, 1)


def motivo_para_bloquear(caminho, linhas_antes, linhas_depois):
    """Devolve o motivo (texto) se a alteração deve ser recusada; None se puder seguir."""
    if caminho.suffix.lower() not in EXTENSOES:
        return None
    if linhas_depois > LIMITE and linhas_depois > linhas_antes:
        return (
            f"{caminho.name} ficaria com {linhas_depois} linhas (limite {LIMITE}; antes {linhas_antes}). "
            "Divida-o por responsabilidade antes de acrescentar."
        )
    return None


def dentro_do_projeto(caminho):
    """True se o caminho estiver dentro do repositório (fora dele o limite não se aplica)."""
    try:
        caminho.resolve().relative_to(_RAIZ)
    except ValueError:
        return False
    return True


def main():
    # Bytes em UTF-8: no Windows o stdin de texto usaria a página de código local e estragaria os acentos.
    pedido = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    ferramenta = pedido.get("tool_name", "")
    entrada = pedido.get("tool_input") or {}
    caminho = Path(entrada.get("file_path") or "")
    if not entrada.get("file_path") or not dentro_do_projeto(caminho):
        return
    try:
        texto_antes = caminho.read_text(encoding="utf-8-sig")
    except (OSError, UnicodeDecodeError):
        texto_antes = ""
    depois = texto_depois(ferramenta, entrada, texto_antes)
    if depois is None:
        return
    motivo = motivo_para_bloquear(caminho, contar_linhas(texto_antes), contar_linhas(depois))
    if motivo:
        sys.stderr.reconfigure(encoding="utf-8")
        sys.stderr.write(f"Bloqueado (regra das 500 linhas, CLAUDE.md): {motivo}\n")
        sys.exit(2)


if __name__ == "__main__":
    main()
