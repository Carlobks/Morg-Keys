"""Limites do plano Claude para a barra do Zebar (imprime JSON no stdout).

Fonte única: ~/.claude/rate_limits.json, escrito pelo ~/.claude/statusline.py
sempre que uma sessão do Claude Code no terminal recebe `rate_limits` (as
percentagens oficiais de 5 h e semanal). A aplicação de ambiente de trabalho
não corre a statusLine, por isso os valores podem estar desatualizados: o
campo `captured_at` diz de quando são, e a barra mostra essa idade. Os valores postos à mão no modal dos
limites (clique no ✻, morg_limites.py) vêm com "origem": "manual", e a dica da barra diz isso.
Uma janela cujo reset já passou não some: vem com "expirado": true (a semanal com o reset avançado de 7 em 7
dias) e a barra mostra o último valor esbatido.
Não se lê o token da conta nem se usa o endpoint não documentado do uso
(regras da Anthropic: docs/pesquisa/quota-claude.md).

`claude = esconder` no arranque.txt (Documentos\\Guia de Atalhos) dá "mostrar": false
e a barra tira o indicador (vale na leitura seguinte, até 30 s).
"""

import json
import sys
import time
from pathlib import Path

RATE_FILE = Path.home() / ".claude" / "rate_limits.json"
ARRANQUE_FILE = Path(__file__).resolve().parent / "guia" / "arranque.txt"
ESCONDER = {"esconder", "ocultar", "nao", "não", "off"}
CICLO_S = {"seven_day": 7 * 86400}  # só a semanal repõe num ciclo fixo


def _mostrar():
    """False se o arranque.txt tiver `claude = esconder` (ou ocultar/não/off)."""
    try:
        lines = ARRANQUE_FILE.read_text(encoding="utf-8-sig").splitlines()
    except OSError:
        return True
    for raw in lines:
        key, sep, value = raw.strip().partition("=")
        if sep and not key.startswith("#") and key.strip().lower() == "claude":
            return value.strip().lower() not in ESCONDER
    return True


def _epoch(value):
    """Segundos Unix a partir de número (s ou ms); None se o formato for outro."""
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return None
    return int(value / 1000) if value > 1e12 else int(value)


def janela_com_reposicao(win, now, ciclo_s=None):
    """{"pct", "resets_at"} de uma janela do ficheiro; None se não tiver % e reset válidos.

    Já reposta (resets_at no passado): o último valor não some, vem com "expirado": True e a barra mostra-o
    esbatido. `ciclo_s` (a semanal, ciclo fixo de 7 dias) leva o resets_at para o próximo ciclo no futuro; a
    das 5 h não tem ciclo fixo, por isso o resets_at fica no passado. Também usada pelo morg_limites.py.
    """
    if not isinstance(win, dict):
        return None
    pct, reset = win.get("used_percentage"), _epoch(win.get("resets_at"))
    if isinstance(pct, bool) or not isinstance(pct, (int, float)) or not reset:
        return None
    janela = {"pct": round(float(pct), 1), "resets_at": reset}
    if reset <= now:
        janela["expirado"] = True
        if ciclo_s:
            janela["resets_at"] = reset + ((now - reset) // ciclo_s + 1) * ciclo_s
    return janela


def main():
    now = int(time.time())
    result = {"now": now, "mostrar": _mostrar(), "captured_at": None, "origem": None, "five_hour": None,
              "seven_day": None}
    try:
        data = json.loads(RATE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        data = {}
    if not isinstance(data, dict):
        data = {}
    result["captured_at"] = _epoch(data.get("captured_at"))
    result["origem"] = data["origem"] if isinstance(data.get("origem"), str) else None
    limits = data.get("rate_limits")
    limits = limits if isinstance(limits, dict) else {}
    for name in ("five_hour", "seven_day"):
        result[name] = janela_com_reposicao(limits.get(name), now, CICLO_S.get(name))
    sys.stdout.write(json.dumps(result))


if __name__ == "__main__":
    main()
