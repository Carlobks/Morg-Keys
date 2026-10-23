"""Arranque do PC (tarefa agendada "GlazeWM (arranque)"): cortina, splash, barra, GlazeWM, apps, .bat."""

import ctypes
import os
import time
from ctypes import wintypes
from pathlib import Path

from morg_arranjo import (
    BOOT_MUTEX,
    _entry_label,
    _focus_saved_workspace,
    _load_layout,
    _new_log,
    _restore,
)
from morg_config_arranque import _arranque_cfg
from morg_cortina import _BlackCover
from morg_ecra_arranque import SPLASH_READY, SPLASH_TITLE, _Progress, _splash_to_top
from morg_glaze import _glaze, _windows_by_workspace, _workspaces
from morg_janelas_zebar import BAR_TITLE
from morg_processos import (
    HERE,
    PROGRAM_FILES,
    PYTHONW,
    ZEBAR,
    _popen_detached,
    _wait_for,
)
from morg_win32 import WAIT_OBJECT_0, kernel32, user32

# --- Arranque do PC (orquestrador do ecrã de arranque) -----------------------
# Corre pela tarefa agendada "GlazeWM (arranque)" ao iniciar sessão. Mostra o
# ecrã de arranque (widget splash, em arranque/) por cima de tudo enquanto, por trás, arrancam a
# barra, o GlazeWM, as apps e os programas .bat; cada etapa é escrita em
# progress.json, que o ecrã lê. Ordem e cuidados vindos da revisão do plano:
#  - o splash é lançado primeiro com start-widget-preset, o que arranca o Zebar
#    SÓ com esse widget → logo a seguir "zebar startup" abre barra/guia/painel;
#  - o GlazeWM tem uiAccess=true: só arranca por ShellExecute (os.startfile);
#  - prioridade normal (as tarefas agendadas correm abaixo do normal e os
#    filhos herdam isso → animação aos solavancos);
#  - o splash fecha-se a si próprio (close, não hide); aos 18 s fecha-se à força.

GLAZEWM_EXE = PROGRAM_FILES / "glzr.io" / "GlazeWM" / "glazewm.exe"
BOOT_QUIET_S = 3     # sai quando nada muda (janelas/títulos) durante 3 s seguidos
BOOT_CAP_S = 60      # limite de segurança: o ecrã nunca fica mais do que isto


BAT_TRAY = HERE / "bat_tray.py"  # corre cada .bat escondido, com ícone na área de notificação



# --- Medição do arranque: quanto tempo o fundo fica à vista antes da cortina ------
def _process_created(pid=None):
    """Hora (segundos, como time.time()) em que o processo foi criado; None se não der.
    Sem pid: este processo (o pythonw da tarefa agendada)."""
    h = kernel32.GetCurrentProcess() if pid is None else kernel32.OpenProcess(0x1000, False, pid)  # QUERY_LIMITED_INFORMATION
    if not h:
        return None
    times = [wintypes.FILETIME() for _ in range(4)]
    ok = kernel32.GetProcessTimes(h, *(ctypes.byref(t) for t in times))
    if pid is not None:
        kernel32.CloseHandle(h)
    if not ok:
        return None
    ft = (times[0].dwHighDateTime << 32) | times[0].dwLowDateTime  # 100 ns desde 1601
    return ft / 1e7 - 11644473600


def _hms(t):
    return "?" if t is None else time.strftime("%H:%M:%S", time.localtime(t)) + f".{int(t % 1 * 1000):03d}"


def _boot_timing_log(log, t_boot, t_cover):
    """Escreve no registo do arranque as horas que mostram onde se perde tempo."""
    created = _process_created()
    pid = wintypes.DWORD()
    tray = user32.FindWindowW("Shell_TrayWnd", None)
    explorer = _process_created(pid.value) if tray and user32.GetWindowThreadProcessId(tray, ctypes.byref(pid)) else None
    log(f"medição: explorador (fundo à vista) {_hms(explorer)} · pythonw criado {_hms(created)}"
        f" · boot() {_hms(t_boot)} · cortina visível {_hms(t_cover)}")
    if explorer:
        log(f"medição: fundo à vista sem cortina ≈ {t_cover - explorer:.1f} s"
            f" (arranque do pythonw {(t_boot - created) if created else float('nan'):.1f} s)")



def _url_port(url):
    """"http://localhost:3000/x" -> 3000; None se não houver endereço local."""
    from urllib.parse import urlparse
    try:
        u = urlparse(url)
    except ValueError:
        return None
    if not u.hostname or u.hostname not in ("localhost", "127.0.0.1"):
        return None
    return u.port or (443 if u.scheme == "https" else 80)


def _port_open(port):
    import socket
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.3):
            return True
    except OSError:
        return False

def _refocus_after_boot(layout):
    """No fim: workspace gravado e foco numa janela real (não no Zebar)."""
    if layout:
        _focus_saved_workspace(layout)
    focused = _glaze("query", "focused").get("data", {}).get("focused", {})
    if focused.get("type") == "window":
        _glaze("command", "focus", "--container-id", focused["id"])



def _window_signature():
    """Janelas geridas e respetivos títulos: enquanto as apps abrem janelas ou
    as páginas carregam, isto muda. Quando fica igual uns segundos, assentou."""
    return tuple(sorted((w["id"], w.get("title", "")) for _, w in _windows_by_workspace(_workspaces() or [])))



def boot():
    t_boot = time.time()
    kernel32.SetPriorityClass(kernel32.GetCurrentProcess(), 0x20)  # NORMAL_PRIORITY_CLASS
    cfg = _arranque_cfg()
    # Primeiro de tudo: preto (com o 1.º quadro da animação) por cima do ambiente de trabalho.
    cover = _BlackCover(cfg["animacao"])
    t_cover = time.time()
    boot_mutex = kernel32.CreateMutexW(None, True, BOOT_MUTEX)  # o layout-restore do GlazeWM cede a vez
    ready = kernel32.CreateEventW(None, True, False, SPLASH_READY)
    log = _new_log()
    t0 = time.monotonic()
    progress = _Progress(cfg["animacao"])
    layout = _load_layout()
    log(f"cortina preta: {time.monotonic() - t0:.1f} s")

    # 1. Ecrã de arranque (arranca o Zebar só com este widget). Com o disco a frio o
    #    WebView2 demora vários segundos a pintar: a cortina preta tapa até lá.
    #    Quando a animação avisa que está desenhada (fundo preto também), a
    #    cortina sai — preto para preto, sem corte. Se não avisar em 20 s,
    #    segue-se na mesma por baixo da cortina.
    if ZEBAR.exists():
        _popen_detached([str(ZEBAR), "start-widget-preset", "--pack", "omarchy-catppuccin",
                         "--widget-name", "splash", "--preset", "default"])
        if kernel32.WaitForSingleObject(ready, 20000) == WAIT_OBJECT_0:
            cover.close()
            log(f"animação visível: {time.monotonic() - t0:.1f} s")
        else:
            log("a animação não avisou em 20 s; continua com a cortina preta")
        # 2. Barra, guia e painel (startupConfigs) — "startup" funciona com o Zebar já a correr.
        progress.step("barra", "Barra")
        _popen_detached([str(ZEBAR), "startup"])

    # 3. GlazeWM (uiAccess: tem de ser por ShellExecute).
    progress.step("glazewm", "Gestor de janelas")
    try:
        os.startfile(str(GLAZEWM_EXE))
    except OSError as err:
        log(f"não consegui abrir o GlazeWM: {err}")
    ok = _wait_for(lambda: _workspaces() is not None, 30, poll=0.25)
    progress.step("glazewm", "Gestor de janelas", "feito" if ok else "falhou")
    bar = _wait_for(lambda: user32.FindWindowW(None, BAR_TITLE), 15, poll=0.2)
    progress.step("barra", "Barra", "feito" if bar else "falhou")
    _wait_for(lambda: user32.FindWindowW(None, "Zebar - omarchy-catppuccin / sistema"), 5, poll=0.2)
    _splash_to_top()
    log(f"GlazeWM e barra: {time.monotonic() - t0:.1f} s")

    # 4. Apps e arranjo dos workspaces (só depois de a shell estar pronta).
    _wait_for(lambda: user32.FindWindowW("Shell_TrayWnd", None), 10, poll=0.2)
    # Programas .bat de arranque.txt: cada um sem janela, com ícone na área de
    # notificação (bat_tray.py). Os que têm endereço local só contam como prontos
    # quando a porta responde; os outros, logo que arrancam.
    waiting_ports = {}  # step id -> (porta, rótulo)
    for i, bat in enumerate(cfg["bats"]):
        sid = f"bat:{i}"
        if not Path(bat["path"]).exists():
            progress.step(sid, bat["name"], "falhou")
            log(f"não existe: {bat['path']}")
            continue
        progress.step(sid, bat["name"])
        _popen_detached([str(PYTHONW), "-I", str(BAT_TRAY), bat["path"], bat["url"], bat["name"]])
        port = _url_port(bat["url"]) if bat["url"] else None
        if port:
            waiting_ports[sid] = (port, bat["name"])
        else:
            progress.step(sid, bat["name"], "feito")
    pending = []
    if layout:
        # Chave fixa por app (o processo de uma app nova do painel só se sabe ao abrir).
        for e in layout.get("windows", []):
            e["_k"] = e.get("process") or f"?{_entry_label(e)}"
            e["_l"] = _entry_label(e)
        keys = list(dict.fromkeys(e["_k"] for e in layout.get("windows", [])))
        labels = {e["_k"]: e["_l"] for e in layout.get("windows", [])}
        for k in keys:
            progress.step(f"app:{k}", labels[k])
        left = {k: sum(1 for e in layout["windows"] if e["_k"] == k) for k in keys}

        def placed(entry):
            left[entry["_k"]] -= 1
            if left[entry["_k"]] == 0:
                progress.step(f"app:{entry['_k']}", entry["_l"], "feito")

        pending = _restore(layout, log, on_placed=placed, wait_s=10)
        for entry in pending:
            progress.step(f"app:{entry['_k']}", entry["_l"], "falhou")
            log(f"não encontrei janela para {entry['_l']} (ws {entry['workspace']})")
    log(f"janelas arrumadas: {time.monotonic() - t0:.1f} s")

    # 5. Só sai quando tudo assentou: nenhuma janela nova nem título a mudar
    #    (páginas a carregar) durante BOOT_QUIET_S seguidos. Limite: BOOT_CAP_S.
    progress.step("fim", "A finalizar")
    _splash_to_top()
    sig, since = _window_signature(), time.monotonic()
    while time.monotonic() - t0 < BOOT_CAP_S:
        time.sleep(0.5)
        for sid, (port, name) in list(waiting_ports.items()):
            if _port_open(port):
                del waiting_ports[sid]
                progress.step(sid, name, "feito")
                log(f"{name} a responder na porta {port}: {time.monotonic() - t0:.1f} s")
        now = _window_signature()
        if now != sig:
            sig, since = now, time.monotonic()
        elif time.monotonic() - since >= BOOT_QUIET_S and not waiting_ports:
            break
    for sid, (port, name) in waiting_ports.items():
        progress.step(sid, name, "falhou")
    _refocus_after_boot(layout)  # foco certo ainda por baixo do ecrã
    progress.step("fim", "A finalizar", "feito")
    progress.finish()
    log(f"tudo assente, ecrã a sair: {time.monotonic() - t0:.1f} s")

    # 6. O ecrã anima a saída e fecha-se; se não o fizer em 8 s, fecha-se à força.
    _wait_for(lambda: not user32.FindWindowW(None, SPLASH_TITLE), 8, poll=0.2)
    hwnd = user32.FindWindowW(None, SPLASH_TITLE)
    if hwnd:
        user32.PostMessageW(hwnd, 0x0010, 0, 0)  # WM_CLOSE
        log("splash fechado à força")
    cover.close()
    _refocus_after_boot(layout)
    log(f"fim: {time.monotonic() - t0:.1f} s")
    try:  # só medição: nunca pode estragar o arranque
        _boot_timing_log(log, t_boot, t_cover)
    except Exception as err:
        log(f"medição falhou: {err!r}")
    kernel32.ReleaseMutex(boot_mutex)
    kernel32.CloseHandle(boot_mutex)
    kernel32.CloseHandle(ready)
