"""Limites do plano Claude para a barra do Zebar (imprime JSON no stdout).

Fonte única: ~/.claude/rate_limits.json, escrito pelo ~/.claude/statusline.py
sempre que uma sessão do Claude Code no terminal recebe `rate_limits` (as
percentagens oficiais de 5 h e semanal). A aplicação de ambiente de trabalho
não corre a statusLine, por isso os valores podem estar desatualizados: o
campo `captured_at` diz de quando são, e a barra mostra essa idade.
"""

import json
import sys
import time
from pathlib import Path

RATE_FILE = Path.home() / ".claude" / "rate_limits.json"


def _epoch(value):
    """Segundos Unix a partir de número (s ou ms); None se o formato for outro."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return int(value / 1000) if value > 1e12 else int(value)


def main():
    now = int(time.time())
    result = {"now": now, "captured_at": None, "five_hour": None, "seven_day": None}
    try:
        data = json.loads(RATE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = {}
    if not isinstance(data, dict):
        data = {}
    result["captured_at"] = _epoch(data.get("captured_at"))
    limits = data.get("rate_limits")
    limits = limits if isinstance(limits, dict) else {}
    for name in ("five_hour", "seven_day"):
        win = limits.get(name)
        win = win if isinstance(win, dict) else {}
        pct, reset = win.get("used_percentage"), _epoch(win.get("resets_at"))
        # Janela já reposta: o valor guardado deixou de valer.
        if isinstance(pct, (int, float)) and reset and reset > now:
            result[name] = {"pct": round(float(pct), 1), "resets_at": reset}
    sys.stdout.write(json.dumps(result))


if __name__ == "__main__":
    main()
