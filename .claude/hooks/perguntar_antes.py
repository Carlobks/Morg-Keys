"""Hook PreToolUse: push, instalações e mudanças às regras do agente pedem sempre o "sim" do dono.

(Morg Laws; Akita #51, #79, #81.) As regras "ask" do settings.json não chegaram: em 2026-10-30 um
`git push --dry-run` correu sem pergunta, e a escrita de um hook também (modo automático). Este hook devolve ao
Claude Code a decisão "ask", que pergunta seja qual for o modo. Pergunta antes de:
- Bash/PowerShell: `git push`; `gh pr create|merge` e `gh release create`; instalar pacotes (npm install/i/ci/add, npx, pip install) ou programas (winget,
  choco, scoop, Install-Module/Install-Package);
- Write/Edit: `.claude/settings*.json`, `.claude/hooks/` e `.githooks/` deste repositório.
Reconhece os comandos pelo texto (uma escrita pela shell não passa no Write/Edit). Sai sempre com 0; com motivo,
escreve o JSON da decisão no stdout.
"""

import json
import re
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
REGRAS_DO_AGENTE = (".claude/settings.json", ".claude/settings.local.json", ".claude/hooks/", ".githooks/")

_GIT = r"\bgit(?:\.exe)?(?:\s+-[cC]\s+(?:\"[^\"]*\"|'[^']*'|\S+))*\s+"
PERGUNTAS = [
    (re.compile(_GIT + r"push\b", re.IGNORECASE), "git push envia o trabalho para fora desta máquina"),
    (re.compile(r"\bnpm(?:\.cmd)?\s+(?:install|i|ci|add)\b", re.IGNORECASE), "npm instala pacotes"),
    (re.compile(r"\bnpx(?:\.cmd)?\s", re.IGNORECASE), "npx descarrega e corre um pacote"),
    (re.compile(r"\bpip3?(?:\.exe)?\s+install\b", re.IGNORECASE), "pip instala pacotes"),
    (re.compile(r"\b(?:winget|choco|scoop)(?:\.exe)?\s+install\b", re.IGNORECASE), "instala um programa"),
    (re.compile(r"\bInstall-(?:Module|Package)\b", re.IGNORECASE), "instala um módulo do PowerShell"),
    # B2 da 2.ª verificação (ML16): criar ou juntar um PR, ou lançar uma versão, publica como o push.
    (re.compile(r"\bgh(?:\.exe)?\s+(?:pr\s+(?:create|merge)|release\s+create)\b", re.IGNORECASE),
     "publica no GitHub (PR ou versão)"),
]


def motivo_para_perguntar(comando):
    """Devolve o motivo (texto) se o comando precisar do "sim" do dono; None nos outros casos."""
    for padrao, motivo in PERGUNTAS:
        if padrao.search(comando):
            return motivo
    return None


def motivo_para_perguntar_ficheiro(caminho):
    """Devolve o motivo se o ficheiro for uma das regras do agente neste repositório; None nos outros casos."""
    if not caminho:
        return None
    try:
        relativo = Path(caminho).resolve().relative_to(RAIZ).as_posix()
    except ValueError:
        return None
    if any(relativo == regra or relativo.startswith(regra) for regra in REGRAS_DO_AGENTE):
        return f"{relativo} é uma regra de segurança do próprio agente"
    return None


def main():
    # Bytes em UTF-8: no Windows o stdin de texto usaria a página de código local e estragaria os acentos.
    pedido = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    entrada = pedido.get("tool_input") or {}
    if pedido.get("tool_name") in ("Write", "Edit"):
        motivo = motivo_para_perguntar_ficheiro(entrada.get("file_path") or "")
    else:
        motivo = motivo_para_perguntar(entrada.get("command") or "")
    if motivo:
        decisao = {"hookEventName": "PreToolUse", "permissionDecision": "ask",
                   "permissionDecisionReason": f"Morg Laws: {motivo}. Precisa do sim do dono, a cada vez."}
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stdout.write(json.dumps({"hookSpecificOutput": decisao}, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    main()
