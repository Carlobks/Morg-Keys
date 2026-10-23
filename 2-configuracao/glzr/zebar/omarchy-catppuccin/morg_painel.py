"""Painel "Apps e arranque" (Alt+Esc, C): mostrar/esconder e os pedidos da página (painel/apps.html)."""

import hashlib
import json
import os
import time
from pathlib import Path

from morg_arranjo import LAYOUT_FILE, _entry_label, _load_layout, _save_layout
from morg_atalhos import (
    APPS_FILE,
    GLAZE_CONFIG,
    _apps_apply_core,
    _apps_entries,
    _fixed_bindings,
    _key_text,
    _parse_key,
    _start_apps,
    _start_items,
)
from morg_janelas_zebar import BAR_TITLE
from morg_processos import HERE, _start_widget
from morg_win32 import (
    _bring_to_front,
    _focus_webview,
    _hide_when_unfocused,
    _is_cloaked,
    _NamedMutex,
    user32,
)

# --- Painel "Apps e arranque" (Alt+Esc, C; painel/apps.html) ------------------------
# A página não escreve ficheiros: pede ao bar_helper.py (py.exe, saída JSON em ASCII).
#   panel            -> mostra o painel e dá-lhe o foco (único dono da visibilidade, A9)
#   panel-hide       -> esconde-o (Esc, ✕, clicar fora)
#   panel state      -> {"keys", "fixed", "workspaces", "undo"}
#   panel apps       -> [{"name", "value"}] do menu Iniciar (fica em cache)
#   panel do <b64>   -> uma mudança (JSON em base64url): grava, aplica, devolve o estado
#   panel undo       -> desfaz a última mudança
PANEL_TITLE = "Zebar - omarchy-catppuccin / apps"
PANEL_UNDO = HERE / ".panel-undo.json"
PANEL_PREV = HERE / ".panel-prev"  # janela que tinha o foco antes de abrir o painel
PANEL_UNDO_MAX = 20
WORKSPACE_NAMES = [str(n) for n in range(1, 11)]


def panel_show():
    """Alt+Esc, C: mostra o painel com foco; se já estiver visível, esconde-o."""
    hwnd = user32.FindWindowW(None, PANEL_TITLE)
    if hwnd and user32.IsWindowVisible(hwnd):
        _panel_release(hwnd)  # a página nota a perda de foco e fica "fechada"
        return
    if not hwnd:  # Zebar arrancado sem o painel: abre-o (só desta vez é lento)
        if not _start_widget("omarchy-catppuccin", "apps"):
            return
        for _ in range(80):  # até 8 s: a página carrega e esconde-se sozinha
            time.sleep(0.1)
            hwnd = user32.FindWindowW(None, PANEL_TITLE)
            if hwnd and not user32.IsWindowVisible(hwnd):
                break
        if not hwnd:
            return
    fg = user32.GetForegroundWindow()
    if fg and fg != hwnd:
        PANEL_PREV.write_text(str(fg))  # para onde volta o foco ao fechar
    _bring_to_front(hwnd)
    _focus_webview(hwnd)
    # Rede de segurança (como o guia): se a página não se esconder ao perder o
    # foco (ex.: erro ao carregar), esconde-a aqui — nunca fica por cima de tudo.
    _hide_when_unfocused(hwnd)


def panel_hide():
    hwnd = user32.FindWindowW(None, PANEL_TITLE)
    if hwnd:
        _panel_release(hwnd)


def _panel_release(hwnd):
    """Esconde o painel e devolve o foco à janela de antes. Uma janela escondida
    que continua ativa fazia a abertura seguinte não ser uma ativação a sério
    (sem WM_SETFOCUS, a página não recebia o teclado)."""
    user32.ShowWindow(hwnd, 0)  # SW_HIDE
    if user32.GetForegroundWindow() != hwnd:
        return
    try:
        prev = int(PANEL_PREV.read_text())
    except (OSError, ValueError):
        prev = 0
    if prev and user32.IsWindow(prev) and user32.IsWindowVisible(prev) and not _is_cloaked(prev):
        _bring_to_front(prev)
    else:
        bar = user32.FindWindowW(None, BAR_TITLE)  # nada a quem voltar: a barra fica ativa
        if bar:
            _bring_to_front(bar)



def _panel_state():
    try:
        lines = APPS_FILE.read_text(encoding="utf-8-sig").splitlines()
    except OSError:
        lines = []
    try:
        fixed = sorted(_fixed_bindings(GLAZE_CONFIG.read_text(encoding="utf-8")))
    except OSError:
        fixed = []
    layout = _load_layout() or {}
    workspaces = [{"index": i, "workspace": e.get("workspace"), "label": _entry_label(e),
                   "process": e.get("process"), "value": e.get("value")}
                  for i, e in enumerate(layout.get("windows", []))]
    try:
        undo = len(json.loads(PANEL_UNDO.read_text(encoding="utf-8")))
    except (OSError, ValueError):
        undo = 0
    return {"keys": [{"key": k, "value": v} for _, k, v in _apps_entries(lines)],
            "fixed": fixed, "workspaces": workspaces, "undo": undo}


def _panel_apps():
    """Apps do menu Iniciar que fazem sentido escolher (sem desinstaladores, ajudas, links)."""
    skip_ext = (".url", ".txt", ".chm", ".pdf", ".html", ".htm", ".hlp", ".rtf")
    skip_name = ("uninstall", "desinstal", "readme", "leia-me", "release notes")
    seen, out = set(), []
    for item in sorted(_start_items(), key=lambda i: i["Name"].lower()):
        name, app_id = item["Name"], item["AppID"]
        low = name.lower()
        if app_id.lower().endswith(skip_ext) or any(s in low for s in skip_name) or low in seen:
            continue
        seen.add(low)
        out.append({"name": name, "value": name})
    return out


def _launch_for(value):
    """App escolhida (nome do menu Iniciar, palavra especial, web:, .exe) ->
    (processo ou None, {"file", "args"}) para abrir no arranque."""
    v = value.strip()
    low = v.lower()
    wt = str(Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WindowsApps" / "wt.exe")
    if low == "terminal":
        return "WindowsTerminal", {"file": wt}
    if low == "claude-code":
        home = str(Path.home())
        return "WindowsTerminal", {"file": wt, "args": f'-w new -d "{home}" "{home}\\.local\\bin\\claude.exe"'}
    if low in ("explorador", "explorer"):
        return "explorer", {"file": "explorer"}
    if low.startswith("web:"):
        url = v[4:].strip()
        if not url.startswith(("http://", "https://")):
            return None, None
        return "chrome", {"file": "chrome", "args": f"--app={url}"}
    if low.endswith(".exe"):
        return Path(v).stem, {"file": v}
    apps = _start_apps(use_cache=True)
    app_id = apps.get(low) or _start_apps().get(low)
    if not app_id:
        return None, None
    # AppID de apps clássicas costuma ser o caminho do .exe: dá logo o processo.
    process = Path(app_id).stem if app_id.lower().endswith(".exe") else None
    return process, {"file": f"shell:AppsFolder\\{app_id}"}


def _panel_push_undo(apps_text, layout_text):
    try:
        stack = json.loads(PANEL_UNDO.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        stack = []
    stack.append({"apps": apps_text, "layout": layout_text})
    PANEL_UNDO.write_text(json.dumps(stack[-PANEL_UNDO_MAX:]), encoding="utf-8")
    _PANEL_PUSHED.append(True)


_PANEL_PUSHED = []  # esta mudança guardou um passo de desfazer (para lhe juntar o "depois")


def _files_hash():
    """Impressão digital de apps.txt + layout.json: o Desfazer só repõe se ninguém
    (Alt+Esc G, Alt+Shift+R, o arranque) mexeu neles depois da mudança do painel."""
    return hashlib.sha256(((_read_or_none(APPS_FILE) or "") + "\0" + (_read_or_none(LAYOUT_FILE) or "")).encode("utf-8")).hexdigest()


def _panel_mark_after():
    try:
        stack = json.loads(PANEL_UNDO.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return
    if stack:
        stack[-1]["after"] = _files_hash()
        PANEL_UNDO.write_text(json.dumps(stack), encoding="utf-8")


def _read_or_none(path):
    try:
        return path.read_text(encoding="utf-8-sig")
    except OSError:
        return None


def _panel_do(op):
    """Aplica uma mudança do painel. Devolve (erro ou None)."""
    kind = op.get("op")
    apps_before, layout_before = _read_or_none(APPS_FILE), _read_or_none(LAYOUT_FILE)
    if kind in ("key", "unkey"):
        return _panel_mudar_tecla(kind, op, apps_before, layout_before)
    if kind in ("ws-add", "ws-del", "ws-move"):
        return _panel_mudar_workspace(kind, op, apps_before, layout_before)
    return "Pedido desconhecido."


def _panel_mudar_tecla(kind, op, apps_before, layout_before):
    """key: põe a app numa tecla (tirando-a da tecla `from`); unkey: tira a tecla. Aplica logo."""
    key = _parse_key(str(op.get("key", "")))
    if not key:
        return "Tecla inválida."
    lines = (apps_before or "").splitlines()
    entries = _apps_entries(lines)
    drop = {i for i, k, _ in entries if k == key}
    if op.get("from"):  # vinha de outra tecla: sai de lá
        src = _parse_key(str(op["from"]))
        drop |= {i for i, k, _ in entries if k == src}
    if kind == "key":
        value = str(op.get("value", "")).strip()
        if not value or "\n" in value or "\r" in value:
            return "App inválida."
    new = [l for i, l in enumerate(lines) if i not in drop]
    if kind == "key":
        new.append(f"{_key_text(key):<16} = {value}")
    _panel_push_undo(apps_before or "", layout_before)
    APPS_FILE.write_text("\n".join(new).rstrip("\n") + "\n", encoding="utf-8", newline="\n")
    errors = _apps_apply_core(use_cache=True)
    if errors:
        APPS_FILE.write_text(apps_before or "", encoding="utf-8", newline="\n")
        _panel_pop_undo()
        # "linha 12: …" só faz sentido no apps.txt; no painel fica a explicação.
        return "Não mudei nada: " + "; ".join(e.split(": ", 1)[-1] if e.startswith("linha ") else e
                                               for e in errors)
    return None


def _panel_mudar_workspace(kind, op, apps_before, layout_before):
    """ws-add: app nova num workspace; ws-del: tira; ws-move: muda de workspace. Grava o layout.json."""
    layout = _load_layout() or {"windows": []}
    windows = layout.setdefault("windows", [])
    if kind == "ws-add":
        erro = _panel_acrescentar_app(op, windows)
        if erro:
            return erro
    else:
        i = op.get("index")
        if not isinstance(i, int) or not 0 <= i < len(windows):
            return "Essa app já não está nesse workspace."
        # O painel diz o que julga estar nesse índice: se não bater (pedidos em
        # fila, Alt+Esc G entretanto), não mexe na entrada errada.
        if "expect_ws" in op and (windows[i].get("workspace") != op["expect_ws"]
                                  or _entry_label(windows[i]) != op.get("expect_label")):
            return "O painel estava desatualizado: veja de novo e repita."
        if kind == "ws-move" and windows[i].get("workspace") == str(op.get("ws", "")):
            return None  # já está nesse workspace: nada a fazer (nem passo de desfazer)
        if kind == "ws-del":
            windows.pop(i)
        else:
            ws = str(op.get("ws", ""))
            if ws not in WORKSPACE_NAMES:
                return "Workspace inválido."
            windows[i]["workspace"] = ws
    _panel_push_undo(apps_before or "", layout_before)
    layout.setdefault("saved_at", int(time.time()))
    _save_layout(layout)
    return None


def _panel_acrescentar_app(op, windows):
    """Acrescenta a `windows` a entrada de uma app nova num workspace; devolve o erro ou None."""
    ws = str(op.get("ws", ""))
    value = str(op.get("value", "")).strip()
    if ws not in WORKSPACE_NAMES or not value:
        return "Workspace ou app inválidos."
    process, launch = _launch_for(value)
    if not launch:
        return f"Não encontrei a app '{value}' neste PC."
    entry = {"workspace": ws, "process": process, "title_hash": "", "label": str(op.get("label") or value),
             "value": value, "launch": launch}
    windows.append({k: v for k, v in entry.items() if v is not None})
    return None


def _panel_pop_undo():
    try:
        stack = json.loads(PANEL_UNDO.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    if not stack:
        return None
    last = stack.pop()
    PANEL_UNDO.write_text(json.dumps(stack), encoding="utf-8")
    return last


def _panel_undo():
    last = _panel_pop_undo()
    if not last:
        return "Nada para desfazer."
    if last.get("after") and last["after"] != _files_hash():
        PANEL_UNDO.write_text("[]", encoding="utf-8")  # o histórico já não corresponde aos ficheiros
        return "Não desfiz: os atalhos ou o arranque mudaram fora do painel depois disso."
    if last["layout"] is None:
        LAYOUT_FILE.unlink(missing_ok=True)
    elif last["layout"] != _read_or_none(LAYOUT_FILE):
        tmp = LAYOUT_FILE.with_suffix(".tmp")
        tmp.write_text(last["layout"], encoding="utf-8", newline="\n")
        os.replace(tmp, LAYOUT_FILE)
    if last["apps"] != (_read_or_none(APPS_FILE) or ""):
        APPS_FILE.write_text(last["apps"], encoding="utf-8", newline="\n")
        errors = _apps_apply_core(use_cache=True)
        if errors:
            return "Desfeito, mas: " + "; ".join(errors)
    return None


def panel_cli(args):
    """Ramo "panel …" chamado pela página: imprime sempre um JSON (ASCII)."""
    import base64
    try:
        if args == ["state"]:
            out = {"ok": True, "state": _panel_state()}
        elif args == ["apps"]:
            out = {"ok": True, "apps": _panel_apps()}
        elif args == ["undo"]:
            with _NamedMutex("Local\\MorgPanel", 10000) as owned:
                err = _panel_undo() if owned else "Ocupado, tente outra vez."
            out = {"ok": not err, "error": err, "state": _panel_state()}
        elif len(args) == 2 and args[0] == "do":
            raw = args[1] + "=" * (-len(args[1]) % 4)
            op = json.loads(base64.urlsafe_b64decode(raw).decode("utf-8"))
            with _NamedMutex("Local\\MorgPanel", 10000) as owned:
                _PANEL_PUSHED.clear()
                err = _panel_do(op) if owned else "Ocupado, tente outra vez."
                if owned and not err and _PANEL_PUSHED:
                    _panel_mark_after()
            out = {"ok": not err, "error": err, "state": _panel_state()}
        else:
            out = {"ok": False, "error": "Pedido desconhecido."}
    except Exception as err:  # a página mostra a mensagem; nunca fica sem resposta
        out = {"ok": False, "error": f"{type(err).__name__}: {err}"}
    print(json.dumps(out, ensure_ascii=True))
