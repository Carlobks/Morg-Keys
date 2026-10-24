"""Arranjo dos workspaces: layout.json, Alt+Esc G (gravar) e restauro das apps no arranque."""

import hashlib
import json
import os
import subprocess
import time
from pathlib import Path

from morg_glaze import _glaze, _windows_by_workspace, _workspaces
from morg_processos import CREATE_NO_WINDOW, HERE, _shell_open
from morg_win32 import SYNCHRONIZE, kernel32, user32

LAYOUT_FILE = Path.home() / ".glzr" / "layout.json"
RESTORE_LOG = HERE / ".layout-restore.log"

# Como abrir cada app no arranque, se ainda não estiver aberta (os.startfile =
# ShellExecute: aceita nomes do registo App Paths e apps da Store via AppsFolder).
LAUNCH = {
    "claude": r"shell:AppsFolder\Claude_pzs8sxrjxfjjc!Claude",
    "Arc": r"shell:AppsFolder\TheBrowserCompany.Arc_ttt1ap7aakyb4!Arc",
    "Obsidian": r"shell:AppsFolder\md.obsidian",
    "chrome": "chrome",
    "msedge": "msedge",
    "explorer": "explorer",
    "WindowsTerminal": str(Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WindowsApps" / "wt.exe"),
}


def _title_hash(title):
    """Impressão digital do título: chega para reconhecer a janela sem guardar
    o título em claro (pode ter nomes de documentos ou assuntos de emails)."""
    return hashlib.sha256((title or "").encode("utf-8")).hexdigest()[:16]



def layout_save():
    """Grava em que workspace está cada janela agora (escrita atómica).

    Se o GlazeWM não responder, não grava nada e dá um som de erro — nunca
    substitui um arranjo bom por um vazio.
    """
    workspaces = _workspaces()
    windows = [
        {"workspace": ws, "process": w["processName"], "title_hash": _title_hash(w.get("title"))}
        for ws, w in _windows_by_workspace(workspaces or [])
    ]
    if not workspaces or not windows:
        user32.MessageBeep(0x10)  # MB_ICONHAND: erro
        return
    # Mantém o "como abrir" e o nome das apps que o painel (Alt+Esc, C) já conhecia.
    known = {}
    for e in (_load_layout() or {}).get("windows", []):
        if e.get("launch") and e.get("process"):
            known.setdefault(e["process"], []).append(e)
    for w in windows:
        prev = known.get(w["process"])
        if prev:  # uma entrada antiga por janela: 2 janelas do Chrome não herdam o mesmo site
            same = [e for e in prev if e.get("title_hash") == w["title_hash"]]
            e = same[0] if same else prev[0]
            prev.remove(e)
            w.update({k: e[k] for k in ("launch", "label", "value") if k in e})
    focused = next((w["name"] for w in workspaces if w.get("hasFocus")), None)
    _save_layout({"saved_at": int(time.time()), "focused": focused, "windows": windows})
    user32.MessageBeep(0)  # confirmação discreta


BOOT_MUTEX = "Local\\MorgBootRunning"
APP_LABELS = {"claude": "Claude", "chrome": "Google Chrome", "Arc": "Arc", "Obsidian": "Obsidian",
              "msedge": "Microsoft Edge", "explorer": "Explorador", "WindowsTerminal": "Terminal"}


def _load_layout():
    try:
        layout = json.loads(LAYOUT_FILE.read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return None
    for e in layout.get("windows", []):  # formato antigo (título em claro)
        if "title_hash" not in e:
            e["title_hash"] = _title_hash(e.get("title"))
    return layout


def _running_images():
    """Nomes (minúsculas, sem .exe) de todos os processos em execução."""
    out = subprocess.run(["tasklist", "/FO", "CSV", "/NH"], capture_output=True, text=True,
                         encoding="utf-8", errors="replace", creationflags=CREATE_NO_WINDOW, check=False)
    names = set()
    for line in out.stdout.splitlines():
        if line.startswith('"'):
            names.add(line.split('","', 1)[0].strip('"').lower().removesuffix(".exe"))
    return names


def _norm(processo):
    """O GlazeWM e o AppID nem sempre usam as mesmas maiúsculas."""
    return (processo or "").lower()


class _Restauro:
    """Estado partilhado pelas fases do restauro: janelas já colocadas e se alguma app foi aberta."""

    def __init__(self, layout, log, on_launched, on_placed):
        self.layout, self.log, self.on_launched, self.on_placed = layout, log, on_launched, on_placed
        self.entries = list(layout.get("windows", []))
        self.placed = set()
        self.launched = False


def _restore(layout, log, on_launched=None, on_placed=None, wait_s=10, poll=0.25):
    """Abre as apps gravadas que faltem e põe cada janela no seu workspace,
    uma só vez por janela. Devolve as entradas que ficaram por colocar.

    - Uma app só é aberta se o PROCESSO não existir (não basta não ter janela
      ainda: abriria em duplicado uma app que está a arrancar sozinha).
    - Primeiro procura a janela com o mesmo título gravado; só no último terço
      do prazo (ou quando já há tantas janelas da app como entradas) aceita
      "qualquer janela da app".
    """
    r = _Restauro(layout, log, on_launched, on_placed)
    _restore_aprender_processos(r, poll)
    running = _running_images()
    windows_now = [(ws, w) for ws, w in _windows_by_workspace(_workspaces() or []) if w["id"] not in r.placed]
    have_windows = {_norm(w["processName"]) for _, w in windows_now}
    legacy = _restore_abrir_antigas(r, running, have_windows)
    _restore_abrir_do_painel(r, legacy, windows_now, running, have_windows)
    pending = [e for e in r.entries if e.get("process") and not e.pop("_placed", False)]
    lost = [e for e in r.entries if not e.get("process")]  # nunca apareceram: ficam por colocar
    return _restore_colocar(r, pending, wait_s, poll) + lost


def _restore_aprender_processos(r, poll):
    # 1.º Apps do painel cujo processo ainda não se sabe: abrem-se ANTES de tudo o
    # resto, uma de cada vez, e ficam com a primeira janela nova que apareça e que
    # não seja de um processo de outra entrada (senão "aprendiam" a janela errada).
    others = {_norm(e.get("process")) for e in r.entries if e.get("process")}
    learned = False
    for entry in [e for e in r.entries if e.get("launch") and not e.get("process")]:
        before = {w["id"] for _, w in _windows_by_workspace(_workspaces() or [])}
        if not _shell_open(entry["launch"], r.log):
            continue
        r.launched = True
        if _restore_esperar_janela_nova(r, entry, before, others, poll):
            learned = True
        else:
            r.log(f"{_entry_label(entry)}: nenhuma janela nova em 12 s")
    if learned:
        _save_layout(r.layout)


def _restore_esperar_janela_nova(r, entry, before, others, poll):
    """Espera (até 12 s) pela 1.ª janela nova que não seja de outra entrada; aprende o processo."""
    deadline = time.monotonic() + 12
    while time.monotonic() < deadline:
        time.sleep(poll)
        new = [(ws, w) for ws, w in _windows_by_workspace(_workspaces() or [])
               if w["id"] not in before and w["id"] not in r.placed and _norm(w["processName"]) not in others]
        if new:
            ws, win = new[0]
            entry["process"] = win["processName"]
            others.add(_norm(win["processName"]))
            if ws != entry["workspace"]:
                _glaze("command", "--id", win["id"], "move", "--workspace", entry["workspace"])
            r.placed.add(win["id"])
            entry["_placed"] = True
            r.log(f"aprendi {_entry_label(entry)} = {entry['process']}; ficou no {entry['workspace']}")
            if r.on_placed:
                r.on_placed(entry)
            return True
    return False


def _restore_abrir_antigas(r, running, have_windows):
    """Devolve as entradas antigas (sem "launch")."""
    # 2.º Entradas gravadas com Alt+Esc, G (sem "launch"): uma abertura por processo, pela tabela LAUNCH.
    legacy = [e for e in r.entries if not e.get("launch") and e.get("process")]
    for process in dict.fromkeys(e["process"] for e in legacy):
        if _norm(process) in have_windows or _norm(process) in running or process not in LAUNCH:
            continue
        try:
            os.startfile(LAUNCH[process])
            r.launched = True
            r.log(f"abri {process}")
            if r.on_launched:
                r.on_launched(process)
        except OSError as err:
            r.log(f"não consegui abrir {process}: {err}")
    return legacy


def _restore_abrir_do_painel(r, legacy, windows_now, running, have_windows):
    # 3.º Entradas do painel com processo conhecido: cada uma é uma janela; abre as que faltam.
    # As janelas que já existem contam primeiro para as entradas antigas do mesmo processo.
    count = {}
    for _, w in windows_now:
        count[_norm(w["processName"])] = count.get(_norm(w["processName"]), 0) + 1
    for e in legacy:
        if count.get(_norm(e["process"]), 0) > 0:
            count[_norm(e["process"])] -= 1
    for entry in [e for e in r.entries if e.get("launch") and e.get("process") and not e.get("_placed")]:
        p = _norm(entry["process"])
        if count.get(p, 0) > 0:
            count[p] -= 1  # já há uma janela desta app para esta entrada
            continue
        if p in running and p not in have_windows and not entry["launch"].get("args"):
            continue  # está a arrancar sozinha (ex.: Arranque do Windows): espera pela janela
        if _shell_open(entry["launch"], r.log):
            r.launched = True
            if r.on_launched:
                r.on_launched(entry["process"])


def _restore_colocar(r, pending, wait_s, poll):
    """Põe cada janela que aparecer no seu workspace; devolve as entradas que ficaram por colocar."""
    start = time.monotonic()
    wait = max(wait_s, 40 if r.launched else 0)
    while pending and time.monotonic() - start < wait:
        late = time.monotonic() - start > wait * 2 / 3
        current = [(ws, w) for ws, w in _windows_by_workspace(_workspaces() or []) if w["id"] not in r.placed]
        for exact_only in (True, False):
            for entry in list(pending):
                match = _restore_janela_para(entry, current, pending, exact_only, late)
                if not match:
                    continue
                ws, win = match
                if ws != entry["workspace"]:
                    _glaze("command", "--id", win["id"], "move", "--workspace", entry["workspace"])
                    r.log(f"movi {entry['process']} do {ws} para o {entry['workspace']}")
                r.placed.add(win["id"])
                current.remove(match)
                pending.remove(entry)
                if r.on_placed:
                    r.on_placed(entry)
        if pending:
            time.sleep(poll)
    return pending


def _restore_janela_para(entry, current, pending, exact_only, late):
    """A janela para esta entrada: a do mesmo título; ou (2.ª volta) qualquer uma da app, se for tarde
    ou já houver tantas janelas da app como entradas por colocar."""
    same_app = [(ws, w) for ws, w in current if _norm(w["processName"]) == _norm(entry["process"])]
    wanted = sum(1 for e in pending if _norm(e["process"]) == _norm(entry["process"]))
    match = next(((ws, w) for ws, w in same_app
                  if _title_hash(w.get("title")) == entry.get("title_hash")), None)
    if not match and not exact_only and same_app and (late or len(same_app) >= wanted):
        match = same_app[0]
    return match


def _entry_label(entry):
    """Nome a mostrar de uma entrada do layout.json."""
    p = entry.get("process")
    return entry.get("label") or APP_LABELS.get(p) or p or "?"


def _save_layout(layout):
    """Grava o layout.json de forma atómica, sem as marcas internas ("_…")."""
    clean = dict(layout)
    clean["windows"] = [{k: v for k, v in e.items() if not k.startswith("_")} for e in layout.get("windows", [])]
    tmp = LAYOUT_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps(clean, indent=2, ensure_ascii=False), encoding="utf-8")
    os.replace(tmp, LAYOUT_FILE)



def _new_log():
    lines = []

    def log(msg):
        lines.append(f"{time.strftime('%H:%M:%S')} {msg}")
        try:
            RESTORE_LOG.write_text("\n".join(lines), encoding="utf-8")
        except OSError:
            pass
    return log


def layout_restore():
    """startup_command do GlazeWM (reinício manual do GlazeWM): repõe o arranjo.
    No arranque do PC quem faz isto é o orquestrador (boot) — aqui cede-lhe a vez."""
    handle = kernel32.OpenMutexW(SYNCHRONIZE, False, BOOT_MUTEX)
    if handle:
        kernel32.CloseHandle(handle)
        return
    layout = _load_layout()
    if not layout:
        return
    log = _new_log()
    for _ in range(30):  # o GlazeWM pode ainda estar a arrancar
        if _workspaces() is not None:
            break
        time.sleep(1)
    else:
        log("GlazeWM não respondeu; nada feito")
        return
    for entry in _restore(layout, log):
        log(f"não encontrei janela para {entry['process']} (ws {entry['workspace']})")
    _focus_saved_workspace(layout)
    log("fim")


def _focus_saved_workspace(layout):
    # Só muda de workspace se ainda não estiver no gravado: com
    # toggle_workspace_on_refocus, "focar o atual" saltaria para o anterior.
    current_ws = next((w["name"] for w in _workspaces() or [] if w.get("hasFocus")), None)
    if layout.get("focused") and current_ws != layout["focused"]:
        _glaze("command", "focus", "--workspace", layout["focused"])
