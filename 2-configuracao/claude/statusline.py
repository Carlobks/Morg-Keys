"""statusLine do Claude Code (tema Catppuccin Mocha).

Mostra modelo, contexto e limites do plano, e guarda `rate_limits` em
~/.claude/rate_limits.json para a barra do Zebar ler.
"""

import json
import os
import sys
import tempfile
import time
from pathlib import Path

RATE_FILE = Path.home() / ".claude" / "rate_limits.json"

MAUVE, BLUE, GREEN, YELLOW, RED, DIM, RESET = (
    "\033[38;2;203;166;247m",
    "\033[38;2;137;180;250m",
    "\033[38;2;166;227;161m",
    "\033[38;2;249;226;175m",
    "\033[38;2;243;139;168m",
    "\033[38;2;108;112;134m",
    "\033[0m",
)


def color_for(pct):
    return RED if pct >= 80 else YELLOW if pct >= 50 else GREEN


def main():
    try:
        # utf-8-sig: tolera o BOM que o PowerShell acrescenta em pipes.
        data = json.loads(sys.stdin.buffer.read().decode("utf-8-sig") or "{}")
    except ValueError:
        data = {}
    if not isinstance(data, dict):
        data = {}

    limits = data.get("rate_limits")
    limits = limits if isinstance(limits, dict) else {}
    if limits:
        # Ficheiro temporário único: duas sessões ao mesmo tempo não se pisam.
        tmp_name = None
        try:
            with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=RATE_FILE.parent,
                                             prefix="rate_limits.", suffix=".tmp",
                                             delete=False) as tmp:
                tmp_name = tmp.name
                json.dump({"captured_at": int(time.time()), "rate_limits": limits}, tmp)
            os.replace(tmp_name, RATE_FILE)
        except OSError:
            # Outra sessão a escrever ao mesmo tempo: fica a versão dela.
            if tmp_name:
                try:
                    os.unlink(tmp_name)
                except OSError:
                    pass

    model = data.get("model")
    name = model.get("display_name", "Claude") if isinstance(model, dict) else "Claude"
    parts = [f"{MAUVE}{name}{RESET}"]
    ctx_win = data.get("context_window")
    ctx = ctx_win.get("used_percentage") if isinstance(ctx_win, dict) else None
    if isinstance(ctx, (int, float)):
        parts.append(f"{BLUE}ctx {round(ctx)}%{RESET}")
    for key, label in (("five_hour", "5h"), ("seven_day", "7d")):
        win = limits.get(key)
        pct = win.get("used_percentage") if isinstance(win, dict) else None
        if isinstance(pct, (int, float)):
            parts.append(f"{color_for(pct)}{label} {round(pct)}%{RESET}")
    sys.stdout.reconfigure(encoding="utf-8")
    print(f" {DIM}·{RESET} ".join(parts))


if __name__ == "__main__":
    main()
