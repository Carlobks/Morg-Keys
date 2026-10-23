"""Hook PreToolUse (Bash/PowerShell): antes de `git commit`, corre scripts/testar.ps1 e recusa se falhar.

Os testes correm com MORG_A_TESTAR=1; com essa variável o hook não volta a correr os testes. Sem isto,
um teste que lance o hook pode entrar em ciclo (aconteceu: 650 processos — armadilha A30).
Sai com 2 (bloqueia) e mostra o fim da saída dos testes no stderr; sai com 0 nos outros casos.
"""

import json
import os
import re
import subprocess
import sys
from pathlib import Path

_COMMIT = re.compile(r"\bgit\b(?:\s+-C\s+(?:\"[^\"]*\"|'[^']*'|\S+))?(?:\s+-c\s+\S+)*\s+commit\b")
_RAIZ = Path(__file__).resolve().parents[2]
_LINHAS_MOSTRADAS = 30
MARCA_A_TESTAR = "MORG_A_TESTAR"


def e_commit(comando):
    """True se o comando faz `git commit`."""
    return bool(_COMMIT.search(comando))


def deve_correr_testes(comando, ambiente):
    """True se for um commit e não estivermos já dentro de uma corrida de testes (A30)."""
    return e_commit(comando) and not ambiente.get(MARCA_A_TESTAR)


def correr_testes():
    """Corre o comando único de testes; devolve (código de saída, saída de texto)."""
    resultado = subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(_RAIZ / "scripts" / "testar.ps1")],
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        check=False,
        env={**os.environ, MARCA_A_TESTAR: "1"},
    )
    return resultado.returncode, resultado.stdout + resultado.stderr


def main():
    # Bytes em UTF-8: no Windows o stdin de texto usaria a página de código local e estragaria os acentos.
    pedido = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    comando = (pedido.get("tool_input") or {}).get("command") or ""
    if not deve_correr_testes(comando, os.environ):
        return
    codigo, saida = correr_testes()
    if codigo != 0:
        fim = "\n".join(saida.strip().splitlines()[-_LINHAS_MOSTRADAS:])
        sys.stderr.reconfigure(encoding="utf-8")
        sys.stderr.write(f"Commit recusado: scripts/testar.ps1 falhou (saída {codigo}).\n{fim}\n")
        sys.exit(2)


if __name__ == "__main__":
    main()
