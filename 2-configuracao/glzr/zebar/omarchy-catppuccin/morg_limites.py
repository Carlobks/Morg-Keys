"""Modal dos limites do Claude (clique no ✻ da barra; limites/limites.html).

A aplicação de ambiente de trabalho não corre a statusLine, por isso o dono põe à mão o % das 5 h, o % da semana e
as horas de reset. Grava-se no mesmo ~/.claude/rate_limits.json que o claude_usage.py lê, com "origem": "manual";
quando a statusLine voltar a correr no terminal, grava o ficheiro inteiro e os valores oficiais passam por cima.
Pesquisa: docs/pesquisa/modal-limites.md. A página não escreve ficheiros: pede ao bar_helper.py (JSON em ASCII).
  limites            -> mostra o modal com foco (ou esconde-o, se já estiver visível)
  limites-hide       -> esconde-o (Esc, Fechar, clicar fora, depois de gravar)
  limites state      -> {"now", "captured_at", "origem", "five_hour", "seven_day"}
  limites set <b64>  -> grava os campos do modal (JSON em base64url); erros por campo
"""

import json
import os
import re
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path

from morg_painel import _panel_release, _show_with_focus
from morg_processos import HERE
from morg_win32 import user32

LIMITES_TITLE = "Zebar - omarchy-catppuccin / limites"
LIMITES_PREV = HERE / ".limites-prev"  # janela que tinha o foco antes de abrir o modal
RATE_FILE = Path.home() / ".claude" / "rate_limits.json"
JANELAS = {"five": ("five_hour", 5 * 3600), "week": ("seven_day", 7 * 86400)}
FOLGA_S = 60  # "5h" escrito a meio de um minuto não passa da janela

ERRO_PCT = "Use um número inteiro de 0 a 100."
ERRO_RESET = "Use 14:30, 2h15, 45m ou qui 16:00."
PASSA = {5 * 3600: "Passa das 5 h: confira o valor.", 7 * 86400: "Passa dos 7 dias: confira o valor."}
DIAS = {"seg": 0, "ter": 1, "qua": 2, "qui": 3, "sex": 4, "sab": 5, "sáb": 5, "dom": 6}
TEMPO = re.compile(r"(?:(\d+)d)?(?:(\d+)h)?(?:(\d+)(m)?)?")
HORA = re.compile(r"(?:([a-zá]{3})[a-zá]*\.?)?(\d{1,2}):(\d{2})")


def limites_show():
    _show_with_focus(LIMITES_TITLE, "limites", LIMITES_PREV)


def limites_hide():
    hwnd = user32.FindWindowW(None, LIMITES_TITLE)
    if hwnd:
        _panel_release(hwnd, LIMITES_PREV)


def ler_percentagem(texto):
    """"40", "7 %" -> inteiro de 0 a 100; o resto dá ValueError com a mensagem para o dono."""
    m = re.fullmatch(r"(\d{1,3})\s*%?", texto.strip())
    if not m or int(m.group(1)) > 100:
        raise ValueError(ERRO_PCT)
    return int(m.group(1))


def ler_reset(texto, agora, maximo):
    """Hora do reset em segundos Unix; None se vazio. Aceita o tempo que falta (2h15, 45m, 1d5h), a hora
    (14:30: hoje, ou amanhã se já passou) e o dia e a hora (qui 16:00: o próximo). Hora local do PC."""
    s = texto.strip().lower().replace(" ", "")
    if not s:
        return None
    reset = _ler_tempo(s, agora) or _ler_hora(s, agora)
    if reset is None:
        raise ValueError(ERRO_RESET)
    if reset - agora > maximo + FOLGA_S:
        raise ValueError(PASSA[maximo])
    return reset


def _ler_tempo(s, agora):
    m = TEMPO.fullmatch(s)
    if not m:
        return None
    dias, horas, minutos, sufixo = m.groups()
    # Minutos soltos só depois de horas ("2h15"); sozinhos levam o "m" ("45m"), como o fmtUntil da barra.
    if minutos and not sufixo and not horas:
        return None
    total = int(dias or 0) * 86400 + int(horas or 0) * 3600 + int(minutos or 0) * 60
    return agora + total if total else None


def _ler_hora(s, agora):
    m = HORA.fullmatch(s)
    if not m or int(m.group(2)) > 23 or int(m.group(3)) > 59:
        return None
    dia, hora, minuto = m.group(1), int(m.group(2)), int(m.group(3))
    if dia is not None and dia not in DIAS:
        return None
    base = datetime.fromtimestamp(agora)
    alvo = base.replace(hour=hora, minute=minuto, second=0, microsecond=0)
    if dia is None:
        return int((alvo if alvo > base else alvo + timedelta(days=1)).timestamp())
    alvo += timedelta(days=(DIAS[dia] - base.weekday()) % 7)
    return int((alvo if alvo > base else alvo + timedelta(days=7)).timestamp())


def _epoch(valor):
    """Segundos Unix a partir de número (s ou ms); None se o formato for outro (como no claude_usage.py)."""
    if isinstance(valor, bool) or not isinstance(valor, (int, float)):
        return None
    return int(valor / 1000) if valor > 1e12 else int(valor)


def _ler_ficheiro():
    try:
        dados = json.loads(RATE_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return {}
    return dados if isinstance(dados, dict) else {}


def _janela_valida(dados, nome, agora):
    """{"pct", "resets_at"} da janela, só se ainda não repôs; senão None."""
    limites = dados.get("rate_limits")
    janela = limites.get(nome) if isinstance(limites, dict) else None
    if not isinstance(janela, dict):
        return None
    pct, reset = janela.get("used_percentage"), _epoch(janela.get("resets_at"))
    if isinstance(pct, bool) or not isinstance(pct, (int, float)) or not reset or reset <= agora:
        return None
    return {"pct": pct, "resets_at": reset}


def _limites_state(agora):
    dados = _ler_ficheiro()
    estado = {"now": agora, "captured_at": _epoch(dados.get("captured_at")), "origem": dados.get("origem")}
    for nome, _ in JANELAS.values():
        estado[nome] = _janela_valida(dados, nome, agora)
    return estado


def _ler_campo(campos, chave, ler, erros):
    """Lê um campo do modal; vazio dá None; um erro fica em `erros[chave]`."""
    try:
        texto = str(campos.get(chave) or "")
        return ler(texto) if texto.strip() else None
    except ValueError as erro:
        erros[chave] = str(erro)
        return None


def _novas_janelas(campos, agora):
    """(janelas a gravar {nome: {...}}, erros por campo). Um campo vazio mantém o valor anterior válido."""
    dados, novas, erros = _ler_ficheiro(), {}, {}
    for prefixo, (nome, maximo) in JANELAS.items():
        pct = _ler_campo(campos, prefixo + "_pct", ler_percentagem, erros)
        reset = _ler_campo(campos, prefixo + "_reset", lambda t, m=maximo: ler_reset(t, agora, m), erros)
        anterior = _janela_valida(dados, nome, agora) or {}
        pct = anterior.get("pct") if pct is None else pct
        reset = anterior.get("resets_at") if reset is None else reset
        if pct is None and reset is None:
            continue  # janela toda vazia e sem valor anterior: fica como estava
        if pct is None:
            erros.setdefault(prefixo + "_pct", "Falta o %.")
        if reset is None:
            erros.setdefault(prefixo + "_reset", "Falta a hora do reset.")
        novas[nome] = {"used_percentage": pct, "resets_at": reset}
    return novas, erros


def _gravar(novas, agora):
    """Junta as janelas novas ao ficheiro (o resto fica) e troca-o de forma atómica, como a statusLine."""
    dados = _ler_ficheiro()
    limites = dados.get("rate_limits") if isinstance(dados.get("rate_limits"), dict) else {}
    for nome, janela in novas.items():
        limites[nome] = {**(limites.get(nome) if isinstance(limites.get(nome), dict) else {}), **janela}
    dados.update({"captured_at": agora, "origem": "manual", "rate_limits": limites})
    RATE_FILE.parent.mkdir(parents=True, exist_ok=True)
    fd, temporario = tempfile.mkstemp(dir=RATE_FILE.parent, prefix="rate_limits.", suffix=".tmp")
    with os.fdopen(fd, "w", encoding="utf-8") as ficheiro:
        json.dump(dados, ficheiro)
    os.replace(temporario, RATE_FILE)


def _limites_set(b64, agora):
    import base64
    raw = b64 + "=" * (-len(b64) % 4)
    campos = json.loads(base64.urlsafe_b64decode(raw).decode("utf-8"))
    if not isinstance(campos, dict):
        return {"ok": False, "error": "Pedido estragado."}
    novas, erros = _novas_janelas(campos, agora)
    if erros:
        return {"ok": False, "errors": erros, "state": _limites_state(agora)}
    _gravar(novas, agora)
    return {"ok": True, "state": _limites_state(agora)}


def limites_cli(args):
    """Ramo "limites …" chamado pela página: imprime sempre um JSON (ASCII)."""
    agora = int(time.time())
    try:
        if args == ["state"]:
            out = {"ok": True, "state": _limites_state(agora)}
        elif len(args) == 2 and args[0] == "set":
            out = _limites_set(args[1], agora)
        else:
            out = {"ok": False, "error": "Pedido desconhecido."}
    except (ValueError, OSError) as err:  # base64/JSON estragados, disco: a página mostra a mensagem
        out = {"ok": False, "error": f"{type(err).__name__}: {err}"}
    print(json.dumps(out, ensure_ascii=True))
