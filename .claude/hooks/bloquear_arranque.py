"""Hook PreToolUse (Bash/PowerShell): recusa arrancar o ambiente a partir do agente (armadilha A2).

Os processos lançados daqui herdam CLAUDECODE, CLAUDE_CODE_* e ANTHROPIC_BASE_URL; o Claude Code aberto
depois pelos atalhos passaria a cobrar pela API. Seguro e permitido: `glazewm command …`, `glazewm query …`
e `Start-ScheduledTask "GlazeWM (arranque)"` (corre com ambiente limpo).
Sai com 2 (bloqueia) e explica no stderr; sai com 0 nos outros casos.
"""

import json
import re
import sys

# Sítio onde começa um comando: início, separadores, ou depois de um lançador.
_POSICAO = r"""(?:^|[;&|(\n]|\bStart-Process\s+(?:-FilePath\s+)?|\bstart\s+(?:""\s+)?|\bcmd(?:\.exe)?\s+/[ck]\s+)"""
_PROGRAMA = re.compile(
    # Caminho opcional antes do programa: entre aspas (pode ter espaços, ex. "C:\Program Files\…") ou sem aspas.
    _POSICAO + r"""\s*&?\s*(?:"[^"]*[\\/]|'[^']*[\\/]|[^\s"';&|]*[\\/]|["'])?(glazewm|zebar)(?:\.exe)?["']?"""
    r"""(?=\s|$|[;&|)])(\s+\S+)?""",
    re.IGNORECASE,
)
_AJUDANTE = re.compile(
    r"""\b(?:py|pyw|python|pythonw)(?:\.exe)?["']?\s+(?:-\w+\s+)*["']?[^"'\s]*bar_helper\.py["']?\s+"""
    r"""(boot|layout-restore|animacao)\b""",
    re.IGNORECASE,
)
_SUBCOMANDOS_SEGUROS = {"command", "query"}


def motivo_para_bloquear(comando):
    """Devolve o motivo (texto) se o comando arrancar o ambiente; None se for seguro."""
    for achado in _PROGRAMA.finditer(comando):
        programa = achado.group(1).lower()
        seguinte = (achado.group(2) or "").strip().lower()
        if programa == "glazewm" and seguinte in _SUBCOMANDOS_SEGUROS:
            continue
        return f"arranca o {programa} a partir do agente"
    achado = _AJUDANTE.search(comando)
    if achado:
        return f"corre `bar_helper.py {achado.group(1)}` a partir do agente"
    return None


def main():
    # Bytes em UTF-8: no Windows o stdin de texto usaria a página de código local e estragaria os acentos.
    pedido = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    comando = (pedido.get("tool_input") or {}).get("command") or ""
    motivo = motivo_para_bloquear(comando)
    if motivo:
        sys.stderr.reconfigure(encoding="utf-8")
        sys.stderr.write(
            f"Bloqueado (armadilha A2, docs/armadilhas.md): o comando {motivo}. "
            'Peça ao utilizador, ou use Start-ScheduledTask "GlazeWM (arranque)". '
            "Seguro daqui: glazewm command … / glazewm query ….\n"
        )
        sys.exit(2)


if __name__ == "__main__":
    main()
