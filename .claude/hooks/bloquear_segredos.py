"""Hook PreToolUse (Bash/PowerShell): o agente não lê segredos pela shell nem corre um download numa shell.

(Morg Laws, regra SEM SEGREDOS do CLAUDE.md; Akita #81.) Achados M2 e M3 da 2.ª verificação: o deny do
settings.json só cobre a ferramenta Read, por isso um `cat .env` pelo terminal passava; e um `curl … | sh`
corria sem pergunta. Recusa:
- um comando que nomeia um segredo: `.env` e `.env.*` (menos `.env.example`/`.env.sample`), `*.pem`, `*.key`,
  a pasta `.ssh`, as credenciais do Claude Code e a lista negra (`.config/morg-keys`);
- um download que vai direto para uma shell (`curl|wget|iwr|irm … | sh|bash|iex|powershell|python`, e
  `iex (irm …)` ou `DownloadString`).
Reconhece os comandos pelo texto (limites como na A32). Sai com 2 e o motivo no stderr; sai com 0 nos outros casos.
"""

import json
import re
import sys

_PALAVRA = re.compile(r"""[^\s"'`;|&<>()=,]+""")
_ENV = re.compile(r"\.env(?:\.(?!example$|sample$)[\w.-]+)?", re.IGNORECASE)
_CHAVE = re.compile(r".+\.(?:pem|key)", re.IGNORECASE)
_PASTAS = re.compile(r"(?:^|[/\\])(?:\.ssh(?:[/\\]|$)|\.claude[/\\]\.credentials|\.config[/\\]morg-keys)",
                     re.IGNORECASE)
_DOWNLOAD = r"(?:curl|wget|iwr|irm|Invoke-WebRequest|Invoke-RestMethod)"
_SHELL = r"(?:sh|bash|zsh|iex|Invoke-Expression|powershell|pwsh|python3?|py)"
_PARA_SHELL = [
    re.compile(rf"\b{_DOWNLOAD}\b[^|]*\|\s*(?:sudo\s+)?{_SHELL}\b", re.IGNORECASE),
    re.compile(rf"\b(?:iex|Invoke-Expression)\b.*(?:\b{_DOWNLOAD}\b|DownloadString)", re.IGNORECASE),
]


def nomeia_um_segredo(palavra):
    """True se a palavra do comando for (ou apontar para) um segredo."""
    nome = re.split(r"[/\\]", palavra)[-1]
    return bool(_ENV.fullmatch(nome) or _CHAVE.fullmatch(nome) or _PASTAS.search(palavra))


def motivo_para_bloquear(comando):
    """Devolve o motivo (texto) se o comando ler um segredo ou correr um download; None nos outros casos."""
    if any(padrao.search(comando) for padrao in _PARA_SHELL):
        return "um download a correr direto numa shell (curl | sh) executa código que ninguém leu."
    if any(nomeia_um_segredo(palavra) for palavra in _PALAVRA.findall(comando)):
        return "o comando nomeia um segredo (.env, chave, .ssh, credenciais ou a lista negra)."
    return None


def main():
    # Bytes em UTF-8: no Windows o stdin de texto usaria a página de código local e estragaria os acentos.
    pedido = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    motivo = motivo_para_bloquear((pedido.get("tool_input") or {}).get("command") or "")
    if motivo:
        sys.stderr.reconfigure(encoding="utf-8")
        sys.stderr.write(f"Bloqueado (segredos, Morg Laws): {motivo} Se for mesmo preciso, peça ao dono.\n")
        sys.exit(2)


if __name__ == "__main__":
    main()
