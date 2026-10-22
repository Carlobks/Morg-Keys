"""Ações da barra do Zebar e dos atalhos do GlazeWM que precisam do Windows.

  awake status    -> imprime "on" ou "off"
  awake toggle    -> liga/desliga o "não suspender" e imprime o novo estado
  awake off       -> desliga (usado ao fechar o GlazeWM)
  awake-hold      -> (interno) processo que mantém o PC acordado
  quick           -> carrega Win+A (Definições Rápidas: volume, Wi-Fi, Bluetooth)
  guide           -> Alt+K: mostra o guia de atalhos; se estiver visível, fecha-o
  guide-hide      -> esconde o guia (usado pela página: Esc, ✕, clicar fora)
  guide-ensure-hidden -> arranque: garante que o guia pré-carregado fica escondido
  bar toggle      -> Alt+Shift+Espaço: esconde/mostra a barra do Zebar
  restore-min     -> Alt+Shift+M: restaura a janela minimizada mais recente
  layout-save     -> grava em que workspace está cada janela (camada Alt+Esc, G)
  layout-restore  -> no arranque do GlazeWM: abre as apps e repõe o arranjo
  boot            -> arranque do PC: ecrã de arranque + barra + GlazeWM + apps + programas
                     .bat de arranque.txt (tarefa agendada)
  splash-ready    -> (interno) a página do ecrã de arranque avisa que já está desenhada
  animacao tap    -> Alt+Esc, E: tocar passa à animação seguinte (sem mostrar);
                     segurar mostra a escolhida ao largar a tecla
  animacao next   -> passa à animação seguinte (cafe -> ...) e mostra-a
  animacao <nome> -> escolhe essa animação (cafe, ...) e mostra-a
  animacao preview-> mostra a animação atual uns segundos
  apps-apply      -> Alt+Shift+R: aplica apps.txt (atalhos das apps) e recarrega
                     (--skip-missing: na instalação, comenta as apps que não existem)
  apps-edit       -> abre apps.txt no editor de texto (Alt+Esc, C)
  layer-show      -> mostra o painel de letras da camada Alt+Esc
  layer-hide      -> esconde esse painel
  on-exit         -> saída do GlazeWM: lança "after-exit" fora do job e sai
  after-exit      -> (interno) espera o GlazeWM terminar, desliga o "não
                     suspender" e volta a mostrar janelas escondidas
  lock            -> bloqueia o PC
  power reboot    -> pede confirmação e reinicia
  power shutdown  -> pede confirmação e desliga

Chamado por C:/Windows/pyw.exe (atalhos) ou C:/Windows/py.exe (barra), o
lançador oficial do Python: escolhe a versão instalada, por isso atualizar o
Python não parte nada.
"""

import ctypes
import hashlib
import json
import os
import subprocess
import sys
import time
from ctypes import wintypes
from pathlib import Path

HERE = Path(__file__).resolve().parent
PYTHONW = Path(sys.executable).with_name("pythonw.exe")
PROGRAM_FILES = Path(os.environ.get("ProgramFiles", r"C:\Program Files"))
ZEBAR = PROGRAM_FILES / "glzr.io" / "Zebar" / "zebar.exe"
GLAZE_CLI = PROGRAM_FILES / "glzr.io" / "GlazeWM" / "cli" / "glazewm.exe"
CREATE_NO_WINDOW = 0x08000000

kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
user32 = ctypes.WinDLL("user32", use_last_error=True)
dwmapi = ctypes.WinDLL("dwmapi")

# Tipos explícitos: sem isto o ctypes trata HWND/HANDLE como int de 32 bits.
HWND, HANDLE = wintypes.HWND, wintypes.HANDLE
user32.FindWindowW.restype = HWND
user32.FindWindowW.argtypes = [wintypes.LPCWSTR, wintypes.LPCWSTR]
user32.GetForegroundWindow.restype = HWND
user32.SetForegroundWindow.argtypes = [HWND]
user32.BringWindowToTop.argtypes = [HWND]
user32.ShowWindow.argtypes = [HWND, ctypes.c_int]
user32.IsWindowVisible.argtypes = [HWND]
user32.IsWindow.argtypes = [HWND]
user32.SetFocus.argtypes = [HWND]
user32.GetWindowThreadProcessId.argtypes = [HWND, ctypes.c_void_p]
user32.GetClassNameW.argtypes = [HWND, wintypes.LPWSTR, ctypes.c_int]
user32.GetWindowTextW.argtypes = [HWND, wintypes.LPWSTR, ctypes.c_int]
user32.MessageBoxW.argtypes = [HWND, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.UINT]
ENUM_PROC = ctypes.WINFUNCTYPE(wintypes.BOOL, HWND, wintypes.LPARAM)
user32.EnumChildWindows.argtypes = [HWND, ENUM_PROC, wintypes.LPARAM]
kernel32.CreateMutexW.restype = HANDLE
kernel32.CreateMutexW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.LPCWSTR]
kernel32.OpenMutexW.restype = HANDLE
kernel32.OpenMutexW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
kernel32.CreateEventW.restype = HANDLE
kernel32.CreateEventW.argtypes = [ctypes.c_void_p, wintypes.BOOL, wintypes.BOOL, wintypes.LPCWSTR]
kernel32.OpenEventW.restype = HANDLE
kernel32.OpenEventW.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.LPCWSTR]
kernel32.SetEvent.argtypes = [HANDLE]
kernel32.WaitForSingleObject.argtypes = [HANDLE, wintypes.DWORD]
kernel32.ReleaseMutex.argtypes = [HANDLE]
kernel32.CloseHandle.argtypes = [HANDLE]
kernel32.GetTickCount64.restype = ctypes.c_ulonglong
kernel32.SetThreadExecutionState.restype = wintypes.DWORD
kernel32.SetThreadExecutionState.argtypes = [wintypes.DWORD]

WAIT_OBJECT_0, WAIT_ABANDONED, INFINITE = 0x0, 0x80, 0xFFFFFFFF
SYNCHRONIZE, EVENT_MODIFY_STATE = 0x00100000, 0x0002
ERROR_ALREADY_EXISTS = 183


class _NamedMutex:
    """`with _NamedMutex("Local\\x"):` — só entra se obtiver mesmo o mutex."""

    def __init__(self, name, timeout_ms=2000):
        self.name, self.timeout_ms, self.handle, self.owned = name, timeout_ms, None, False

    def __enter__(self):
        self.handle = kernel32.CreateMutexW(None, False, self.name)
        if self.handle:
            self.owned = kernel32.WaitForSingleObject(self.handle, self.timeout_ms) in (
                WAIT_OBJECT_0, WAIT_ABANDONED)
        return self.owned

    def __exit__(self, *exc):
        if self.handle:
            if self.owned:
                kernel32.ReleaseMutex(self.handle)
            kernel32.CloseHandle(self.handle)


# --- Não suspender (chávena) ---------------------------------------------------
# O processo "awake-hold" é dono do mutex AWAKE_ALIVE enquanto está vivo: é a
# prova de que está ligado (sem ficheiros de PID que sobrevivam a um reinício).
# Para o desligar, sinaliza-se o evento AWAKE_STOP e ele sai sozinho.
AWAKE_ALIVE = "Local\\OmarchyAwakeAlive"
AWAKE_STOP = "Local\\OmarchyAwakeStop"
AWAKE_TOGGLE = "Local\\OmarchyAwakeToggle"


def awake_status():
    handle = kernel32.OpenMutexW(SYNCHRONIZE, False, AWAKE_ALIVE)
    if handle:
        kernel32.CloseHandle(handle)
        return "on"
    return "off"


def _awake_stop():
    handle = kernel32.OpenEventW(EVENT_MODIFY_STATE, False, AWAKE_STOP)
    if handle:
        kernel32.SetEvent(handle)
        kernel32.CloseHandle(handle)
    for _ in range(40):  # até 2 s para o processo sair
        if awake_status() == "off":
            break
        time.sleep(0.05)


def awake_toggle():
    with _NamedMutex(AWAKE_TOGGLE) as owned:  # dois cliques rápidos não criam dois processos
        if not owned:
            return awake_status()
        if awake_status() == "on":
            _awake_stop()
            return awake_status()

        # Processo independente: sobrevive ao fecho do Zebar e não abre janela.
        flags = 0x00000008 | 0x00000200  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
        args = [str(PYTHONW), "-I", str(Path(__file__).resolve()), "awake-hold"]
        try:
            subprocess.Popen(args, creationflags=flags | 0x01000000, close_fds=True)  # + BREAKAWAY_FROM_JOB
        except OSError:
            subprocess.Popen(args, creationflags=flags, close_fds=True)
        for _ in range(60):  # confirma que arrancou (até 3 s)
            if awake_status() == "on":
                break
            time.sleep(0.05)
        return awake_status()


def awake_off():
    with _NamedMutex(AWAKE_TOGGLE):
        _awake_stop()
    return awake_status()


def awake_hold():
    alive = kernel32.CreateMutexW(None, True, AWAKE_ALIVE)
    if not alive or ctypes.get_last_error() == ERROR_ALREADY_EXISTS:
        return  # já há outro a manter o PC acordado
    stop = kernel32.CreateEventW(None, True, False, AWAKE_STOP)
    ES_CONTINUOUS, ES_SYSTEM_REQUIRED, ES_DISPLAY_REQUIRED = 0x80000000, 0x1, 0x2
    # Sistema e ecrã acordados, como o "Stay Awake" do Omarchy (sem proteção
    # de ecrã nem bloqueio). 0 = o Windows recusou: sai para a chávena não mentir.
    if not kernel32.SetThreadExecutionState(ES_CONTINUOUS | ES_SYSTEM_REQUIRED | ES_DISPLAY_REQUIRED):
        return
    kernel32.WaitForSingleObject(stop, INFINITE)  # o estado vale enquanto esta thread existir
    kernel32.SetThreadExecutionState(ES_CONTINUOUS)


# --- Definições Rápidas (Win+A) -------------------------------------------------
def quick_settings():
    """Envia Win+A com SendInput (o mesmo que carregar nas teclas)."""
    VK_LWIN, VK_A, KEYUP = 0x5B, 0x41, 0x0002

    class KEYBDINPUT(ctypes.Structure):
        _fields_ = [("wVk", wintypes.WORD), ("wScan", wintypes.WORD), ("dwFlags", wintypes.DWORD),
                    ("time", wintypes.DWORD), ("dwExtraInfo", ctypes.c_size_t)]

    class INPUT(ctypes.Structure):
        class _U(ctypes.Union):
            _fields_ = [("ki", KEYBDINPUT), ("_pad", ctypes.c_byte * 32)]
        _anonymous_ = ("u",)
        _fields_ = [("type", wintypes.DWORD), ("u", _U)]

    def key(vk, up=False):
        i = INPUT(type=1)
        i.ki = KEYBDINPUT(vk, 0, KEYUP if up else 0, 0, 0)
        return i

    seq = (INPUT * 4)(key(VK_LWIN), key(VK_A), key(VK_A, True), key(VK_LWIN, True))
    user32.SendInput(4, seq, ctypes.sizeof(INPUT))


# --- Janelas: foco e visibilidade ------------------------------------------------
GUIDE_TITLE = "Zebar - omarchy-catppuccin / guia"
BAR_TITLE = "Zebar - omarchy-catppuccin / bar"


def _is_cloaked(hwnd):
    """Janelas de outros workspaces estão "cloaked" (escondidas pelo GlazeWM),
    mas IsWindowVisible continua a dizer que sim."""
    value = ctypes.c_int(0)
    dwmapi.DwmGetWindowAttribute(HWND(hwnd), 14, ctypes.byref(value), ctypes.sizeof(value))
    return bool(value.value)


def _bring_to_front(hwnd):
    """Mostra e ativa `hwnd` contornando a regra anti-roubo de foco.

    Liga-se temporariamente à fila de entrada da janela que tem o foco: o
    Windows passa a tratar este pedido como vindo dela. (Simular um toque em
    Alt também funciona, mas ativa o "modo menu" e tira o foco à página.)
    """
    fg_thread = user32.GetWindowThreadProcessId(user32.GetForegroundWindow(), None)
    me = kernel32.GetCurrentThreadId()
    attached = fg_thread and fg_thread != me and user32.AttachThreadInput(me, fg_thread, True)
    try:
        user32.ShowWindow(hwnd, 5)  # SW_SHOW
        user32.BringWindowToTop(hwnd)
        user32.SetForegroundWindow(hwnd)
    finally:
        if attached:
            user32.AttachThreadInput(me, fg_thread, False)


def _focus_webview(hwnd):
    """Dá o foco do teclado à página (o controlo do WebView2 dentro da janela).

    Pôr a janela em primeiro plano não chega: sem isto o Esc e a pesquisa não
    recebem teclas. O controlo vive noutro processo, por isso liga-se a fila de
    entrada desta thread à dele antes do SetFocus.
    """
    found = []

    def visit(child, _):
        buf = ctypes.create_unicode_buffer(64)
        user32.GetClassNameW(child, buf, 64)
        if buf.value == "Chrome_RenderWidgetHostHWND":
            found.append(child)
            return False
        return True

    user32.EnumChildWindows(hwnd, ENUM_PROC(visit), 0)
    if not found:
        return
    target = user32.GetWindowThreadProcessId(found[0], None)
    me = kernel32.GetCurrentThreadId()
    if user32.AttachThreadInput(me, target, True):
        user32.SetFocus(found[0])
        user32.AttachThreadInput(me, target, False)


# --- Guia de atalhos (Alt+K) ----------------------------------------------------
LAST_KEY_FILE = HERE / ".guide-last"
PREV_FILE = HERE / ".guide-prev"


def _is_key_repeat():
    """True se esta chamada vier da repetição automática de Alt+K segurado.

    Cada repetição volta a disparar o atalho. Regra: qualquer chamada a menos
    de (atraso de repetição do teclado + 200 ms) da anterior é repetição; como
    as repetições chegam a ~30/s, enquanto a tecla estiver segurada todas caem
    dentro da janela. O relógio é o GetTickCount64 (comum a todos os processos
    e imune a acertos de hora); um mutex serializa os processos em rajada.
    """
    try:
        import winreg
        with winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Control Panel\Keyboard") as k:
            delay_ms = (int(winreg.QueryValueEx(k, "KeyboardDelay")[0]) + 1) * 250
    except (OSError, ValueError):
        delay_ms = 500

    with _NamedMutex("Local\\GuiaAtalhosAltK", 1000) as owned:
        if not owned:
            return True  # outra chamada da mesma rajada está a tratar disto
        now = kernel32.GetTickCount64()
        try:
            last = int(LAST_KEY_FILE.read_text())
        except (OSError, ValueError):
            last = 0
        LAST_KEY_FILE.write_text(str(now))
        return 0 <= now - last < delay_ms + 200


def _hide_when_unfocused(hwnd):
    """Rede de segurança do "clicar fora".

    Normalmente é a própria página que deteta a perda de foco, anima o fecho
    (encolhe para a chávena) e pede para se esconder. Se isso falhar, este
    processo esconde a janela quando outra estiver ativa há mais de 0,7 s —
    tempo suficiente para a animação da página terminar primeiro.
    """
    for _ in range(20):  # até 1 s para o guia ficar ativo
        if user32.GetForegroundWindow() == hwnd:
            break
        time.sleep(0.05)
    away_since = None
    while user32.IsWindowVisible(hwnd):
        if user32.GetForegroundWindow() != hwnd:
            away_since = away_since or time.monotonic()
            if time.monotonic() - away_since > 0.7:
                user32.ShowWindow(hwnd, 0)  # SW_HIDE
                return
        else:
            away_since = None
        time.sleep(0.1)


def _restore_previous(hwnd):
    """Fecho pelo Alt+K: devolve o foco à janela de antes. A página nota a
    perda de foco e encolhe para a chávena antes de se esconder. Se a janela
    de antes estiver noutro workspace (cloaked), esconde só o guia."""
    try:
        prev = int(PREV_FILE.read_text())
    except (OSError, ValueError):
        prev = 0
    if (prev and prev != hwnd and user32.IsWindow(prev)
            and user32.IsWindowVisible(prev) and not _is_cloaked(prev)):
        _bring_to_front(prev)
    else:
        user32.ShowWindow(hwnd, 0)  # SW_HIDE


def _start_widget(pack, widget):
    if not ZEBAR.exists():
        return False
    try:
        subprocess.Popen(
            [str(ZEBAR), "start-widget-preset", "--pack", pack, "--widget-name", widget,
             "--preset", "default"],
            creationflags=CREATE_NO_WINDOW, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        )
        return True
    except OSError:
        return False


def guide():
    """Alt+K: mostra o guia (já carregado pelo Zebar) ou esconde-o se estiver visível."""
    if _is_key_repeat():
        return
    hwnd = user32.FindWindowW(None, GUIDE_TITLE)
    if hwnd and user32.IsWindowVisible(hwnd):
        _restore_previous(hwnd)
        return

    if not hwnd:  # Zebar arrancado sem o guia: abre-o (só desta vez é lento)
        if not _start_widget("omarchy-catppuccin", "guia"):
            return
        for _ in range(80):  # até 8 s: a página carrega e esconde-se sozinha
            time.sleep(0.1)
            hwnd = user32.FindWindowW(None, GUIDE_TITLE)
            if hwnd and not user32.IsWindowVisible(hwnd):
                break
        if not hwnd:
            return

    fg = user32.GetForegroundWindow()
    if fg and fg != hwnd:
        PREV_FILE.write_text(str(fg))
    _bring_to_front(hwnd)
    _focus_webview(hwnd)
    _hide_when_unfocused(hwnd)


def guide_hide():
    """Chamado pela própria página (Esc, ✕, clicar fora). Esconder sempre por
    aqui, e nunca pelo Tauri, mantém um único dono do estado visível/escondido."""
    hwnd = user32.FindWindowW(None, GUIDE_TITLE)
    if hwnd:
        user32.ShowWindow(hwnd, 0)  # SW_HIDE


def guide_ensure_hidden():
    """Arranque do GlazeWM: se a página do guia não se esconder sozinha (ex.:
    erro ao carregar), esconde-a ao fim de 15 s — nunca fica uma janela
    transparente por cima do ecrã a apanhar cliques."""
    # O mesmo para o painel da camada Alt+Esc (pré-carregado da mesma forma).
    deadline = time.monotonic() + 60
    while time.monotonic() < deadline:
        if user32.FindWindowW(None, GUIDE_TITLE):
            time.sleep(15)
            for title in (GUIDE_TITLE, "Zebar - omarchy-catppuccin / sistema"):
                hwnd = user32.FindWindowW(None, title)
                if hwnd and user32.IsWindowVisible(hwnd) and user32.GetForegroundWindow() != hwnd:
                    user32.ShowWindow(hwnd, 0)  # SW_HIDE
            _refocus_if_zebar_stole()
            return
        time.sleep(1)


def _refocus_if_zebar_stole():
    """Ao arrancar, o Zebar pode deixar em primeiro plano uma janela sua
    invisível ("Tauri App"): o teclado escreveria para o nada. Devolve o foco
    à janela que o GlazeWM tem como focada."""
    buf = ctypes.create_unicode_buffer(64)
    user32.GetWindowTextW(user32.GetForegroundWindow(), buf, 64)
    if buf.value != "Tauri App":
        return
    focused = _glaze("query", "focused").get("data", {}).get("focused", {})
    if focused.get("type") == "window":
        _glaze("command", "focus", "--container-id", focused["id"])


def bar_toggle():
    """Alt+Shift+Espaço: esconde/mostra a barra (como Super+Shift+Espaço no
    Omarchy). Só esconde a janela: o Zebar e o guia continuam a correr. O espaço
    de 40 px no topo fica, porque o GlazeWM não muda margens por comando."""
    hwnd = user32.FindWindowW(None, BAR_TITLE)
    if not hwnd:
        _start_widget("omarchy-catppuccin", "bar")
    elif user32.IsWindowVisible(hwnd):
        user32.ShowWindow(hwnd, 0)  # SW_HIDE
    else:
        user32.ShowWindow(hwnd, 8)  # SW_SHOWNA: mostra sem roubar o foco


# --- GlazeWM: minimizadas e arranjo dos workspaces --------------------------------
def _glaze(*args):
    """Chama a CLI do GlazeWM e devolve o JSON; {} se não estiver a correr."""
    try:
        out = subprocess.run([str(GLAZE_CLI), *args], capture_output=True, text=True,
                             encoding="utf-8", errors="replace", timeout=10,
                             creationflags=CREATE_NO_WINDOW)
        return json.loads(out.stdout or "{}")
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return {}


def _workspaces():
    reply = _glaze("query", "workspaces")
    return reply.get("data", {}).get("workspaces", []) if reply.get("success") else None


def restore_minimized():
    """Alt+Shift+M: restaura a janela minimizada mais recente do workspace atual.

    "Mais recente" = a primeira minimizada pela ordem de foco do GlazeWM
    (childFocusOrder), percorrendo também os contentores de divisão.
    """
    ws = next((w for w in _workspaces() or [] if w.get("hasFocus")), None)
    if not ws:
        return

    def by_focus(container):
        children = {c["id"]: c for c in container.get("children", [])}
        order = [children[i] for i in container.get("childFocusOrder", []) if i in children]
        return order + [c for c in children.values() if c not in order]

    def first_minimized(container):
        for child in by_focus(container):
            if child.get("type") == "window" and child.get("state", {}).get("type") == "minimized":
                return child["id"]
            found = first_minimized(child)
            if found:
                return found
        return None

    target = first_minimized(ws)
    if target:
        _glaze("command", "--id", target, "toggle-minimized")
        _glaze("command", "focus", "--container-id", target)


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


def _windows_by_workspace(workspaces):
    """[(nome_do_workspace, janela)] pela ordem em que aparecem na árvore."""
    out = []

    def walk(container, ws_name):
        for child in container.get("children", []):
            if child.get("type") == "window":
                out.append((ws_name, child))
            else:
                walk(child, ws_name)

    for ws in workspaces:
        walk(ws, ws["name"])
    return out


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
    focused = next((w["name"] for w in workspaces if w.get("hasFocus")), None)
    tmp = LAYOUT_FILE.with_suffix(".tmp")
    tmp.write_text(json.dumps({"saved_at": int(time.time()), "focused": focused, "windows": windows},
                              indent=2), encoding="utf-8")
    os.replace(tmp, LAYOUT_FILE)
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
                         encoding="utf-8", errors="replace", creationflags=CREATE_NO_WINDOW)
    names = set()
    for line in out.stdout.splitlines():
        if line.startswith('"'):
            names.add(line.split('","', 1)[0].strip('"').lower().removesuffix(".exe"))
    return names


def _restore(layout, log, on_launched=None, on_placed=None, wait_s=10, poll=0.25):
    """Abre as apps gravadas que faltem e põe cada janela no seu workspace,
    uma só vez por janela. Devolve as entradas que ficaram por colocar.

    - Uma app só é aberta se o PROCESSO não existir (não basta não ter janela
      ainda: abriria em duplicado uma app que está a arrancar sozinha).
    - Primeiro procura a janela com o mesmo título gravado; só no último terço
      do prazo (ou quando já há tantas janelas da app como entradas) aceita
      "qualquer janela da app".
    """
    entries = list(layout.get("windows", []))
    running = _running_images()
    have_windows = {w["processName"] for _, w in _windows_by_workspace(_workspaces() or [])}
    launched = False
    for process in dict.fromkeys(e["process"] for e in entries):
        if process in have_windows or process.lower() in running or process not in LAUNCH:
            continue
        try:
            os.startfile(LAUNCH[process])
            launched = True
            log(f"abri {process}")
            if on_launched:
                on_launched(process)
        except OSError as err:
            log(f"não consegui abrir {process}: {err}")

    pending, placed = list(entries), set()
    start = time.monotonic()
    wait = max(wait_s, 40 if launched else 0)
    while pending and time.monotonic() - start < wait:
        late = time.monotonic() - start > wait * 2 / 3
        current = [(ws, w) for ws, w in _windows_by_workspace(_workspaces() or []) if w["id"] not in placed]
        for exact_only in (True, False):
            for entry in list(pending):
                same_app = [(ws, w) for ws, w in current if w["processName"] == entry["process"]]
                wanted = sum(1 for e in pending if e["process"] == entry["process"])
                match = next(((ws, w) for ws, w in same_app
                              if _title_hash(w.get("title")) == entry["title_hash"]), None)
                if not match and not exact_only and same_app and (late or len(same_app) >= wanted):
                    match = same_app[0]
                if not match:
                    continue
                ws, win = match
                if ws != entry["workspace"]:
                    _glaze("command", "--id", win["id"], "move", "--workspace", entry["workspace"])
                    log(f"movi {entry['process']} do {ws} para o {entry['workspace']}")
                placed.add(win["id"])
                current.remove(match)
                pending.remove(entry)
                if on_placed:
                    on_placed(entry)
        if pending:
            time.sleep(poll)
    return pending


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


# --- Atalhos das apps (apps.txt) ---------------------------------------------------
# O utilizador edita Documentos\Guia de Atalhos\apps.txt ("Alt+Shift+B = Google
# Chrome"); "apps-apply" (Alt+Shift+R) converte isso em atalhos do GlazeWM,
# escritos entre os marcadores APPS_BEGIN/APPS_END do config.yaml, e recarrega.
APPS_FILE = HERE / "guia" / "apps.txt"
GLAZE_CONFIG = Path.home() / ".glzr" / "glazewm" / "config.yaml"
APPS_BEGIN = "  # >>> apps: gerado a partir de apps.txt (Alt+Shift+R) — não editar aqui >>>"
APPS_END = "  # <<< apps <<<"
WT = "%LOCALAPPDATA%/Microsoft/WindowsApps/wt.exe"
SPECIAL_APPS = {
    "terminal": f"shell-exec {WT}",
    "claude-code": f"shell-exec {WT} -w new -d %USERPROFILE% %USERPROFILE%/.local/bin/claude.exe",
    "explorador": "shell-exec explorer",
    "explorer": "shell-exec explorer",
}
KEY_NAMES = {"enter": "enter", "espaço": "space", "espaco": "space", "space": "space"}


def _start_apps():
    """{nome no menu Iniciar (minúsculas): AppID} via Get-StartApps."""
    out = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "[Console]::OutputEncoding=[Text.Encoding]::UTF8; Get-StartApps | ConvertTo-Json -Compress"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=30, creationflags=CREATE_NO_WINDOW)
    try:
        items = json.loads(out.stdout or "[]")
    except ValueError:
        return {}
    items = [items] if isinstance(items, dict) else items
    return {i["Name"].strip().lower(): i["AppID"] for i in items if i.get("Name") and i.get("AppID")}


def _parse_key(text):
    """"Alt+Shift+B" -> "alt+shift+b"; None se não for válido."""
    parts = [p.strip().lower() for p in text.split("+") if p.strip()]
    if not parts or parts[0] != "alt":
        return None
    mods, key = parts[:-1], KEY_NAMES.get(parts[-1], parts[-1])
    if "ctrl" in mods or any(m not in ("alt", "shift") for m in mods):
        return None
    if not (len(key) == 1 and key.isalnum()) and key not in ("enter", "space"):
        return None
    return "+".join(mods + [key])


def _resolve_app(value, start_apps):
    """Texto da direita de apps.txt -> comando do GlazeWM (ou None)."""
    v = value.strip()
    low = v.lower()
    if low in SPECIAL_APPS:
        return SPECIAL_APPS[low]
    if low.startswith("web:"):
        url = v[4:].strip()
        return f"shell-exec chrome --app={url}" if url.startswith(("http://", "https://")) else None
    if low.endswith(".exe") and Path(v).exists():
        return f"shell-exec {v.replace(chr(92), '/')}"
    app_id = start_apps.get(low)
    if not app_id:  # nome parcial, desde que só haja uma app com esse nome
        found = [aid for name, aid in start_apps.items() if low in name]
        app_id = found[0] if len(found) == 1 else None
    # Aspas no argumento (não no programa): AppIDs de apps clássicas podem ter espaços.
    return f'shell-exec explorer "shell:AppsFolder\\{app_id}"' if app_id else None


def _special_available(value):
    """Para as palavras especiais e web:, confirma que o programa existe neste PC."""
    low = value.strip().lower()
    if low == "claude-code":
        return (Path.home() / ".local" / "bin" / "claude.exe").exists()
    if low.startswith("web:"):
        import winreg
        try:
            winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE,
                           r"SOFTWARE\Microsoft\Windows\CurrentVersion\App Paths\chrome.exe").Close()
            return True
        except OSError:
            return False
    return True


def _fixed_bindings(config_text):
    """Atalhos globais do config.yaml fora do bloco gerado (não podem ser usados)."""
    text = config_text
    if APPS_BEGIN in text and APPS_END in text:
        text = text.split(APPS_BEGIN)[0] + text.split(APPS_END, 1)[1]
    top = text.split("\nkeybindings:", 1)[-1]
    found = set()
    for line in top.splitlines():
        if line.strip().startswith("bindings:"):
            found.update(k.strip().strip("'\"") for k in line.split("[", 1)[1].rstrip("]").split(","))
    return found


def apps_apply(skip_missing=False):
    """Alt+Shift+R: aplica apps.txt ao config do GlazeWM e recarrega-o.

    skip_missing (instalação noutro PC): em vez de dar erro, as linhas cujas
    apps não existem neste PC ficam comentadas no apps.txt com uma nota."""
    def reload_and_exit():
        _glaze("command", "wm-reload-config")

    try:
        lines = APPS_FILE.read_text(encoding="utf-8-sig").splitlines()
        config = GLAZE_CONFIG.read_text(encoding="utf-8")
    except OSError as err:
        user32.MessageBoxW(None, f"Não consegui ler os ficheiros:\n{err}", "Atalhos das apps", 0x10 | 0x40000)
        return reload_and_exit()

    fixed = _fixed_bindings(config)
    start_apps = None
    errors, entries, used = [], [], {}
    skipped = False
    for n, raw in enumerate(lines, 1):
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if "=" not in line:
            errors.append(f"linha {n}: falta o '=' ({line})")
            continue
        left, right = line.split("=", 1)
        key = _parse_key(left)
        if not key:
            errors.append(f"linha {n}: tecla inválida '{left.strip()}' (use Alt+Shift+letra, sem Ctrl)")
            continue
        if key in fixed:
            errors.append(f"linha {n}: {left.strip()} já é usado por outro atalho do sistema")
            continue
        if key in used:
            errors.append(f"linha {n}: {left.strip()} repetido (linha {used[key]})")
            continue
        if start_apps is None and right.strip().lower() not in SPECIAL_APPS \
                and not right.strip().lower().startswith("web:"):
            start_apps = _start_apps()
        command = _resolve_app(right, start_apps or {})
        if command and skip_missing and not _special_available(right):
            command = None
        if not command:
            if skip_missing:
                lines[n - 1] = f"# (não encontrada neste PC) {raw.strip()}"
                skipped = True
                continue
            errors.append(f"linha {n}: não encontrei a app '{right.strip()}' no menu Iniciar")
            continue
        used[key] = n
        entries.append((key, right.strip(), command))

    if skipped:
        APPS_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if errors:
        user32.MessageBoxW(None, "Os atalhos das apps NÃO foram alterados:\n\n" + "\n".join(errors),
                           "Atalhos das apps (apps.txt)", 0x30 | 0x40000 | 0x10000)
        return reload_and_exit()

    block = [APPS_BEGIN]
    for key, label, command in entries:
        block.append(f"  # {label}")
        block.append("  - commands: ['{}']".format(command.replace("'", "''")))
        block.append(f"    bindings: ['{key}']")
    block.append(APPS_END)
    if APPS_BEGIN in config and APPS_END in config:
        before = config.split(APPS_BEGIN)[0]
        after = config.split(APPS_END, 1)[1]
        new_config = before + "\n".join(block) + after
    else:
        new_config = config.replace("\nkeybindings:\n", "\nkeybindings:\n" + "\n".join(block) + "\n", 1)
    if new_config != config:
        tmp = GLAZE_CONFIG.with_suffix(".tmp")
        tmp.write_text(new_config, encoding="utf-8")
        os.replace(tmp, GLAZE_CONFIG)
    reload_and_exit()
    user32.MessageBeep(0)


def apps_edit():
    """Abre apps.txt no editor de texto predefinido."""
    os.startfile(str(APPS_FILE))


# --- Painel da camada Alt+Esc ----------------------------------------------------
LAYER_TITLE = "Zebar - omarchy-catppuccin / sistema"


def layer_show():
    """Mostra o painel com as letras da camada, sem lhe dar o foco (as teclas
    continuam a ser apanhadas pelo GlazeWM)."""
    hwnd = user32.FindWindowW(None, LAYER_TITLE)
    if not hwnd:
        _start_widget("omarchy-catppuccin", "sistema")
        return
    user32.ShowWindow(hwnd, 8)  # SW_SHOWNA


def layer_hide():
    hwnd = user32.FindWindowW(None, LAYER_TITLE)
    if hwnd:
        user32.ShowWindow(hwnd, 0)  # SW_HIDE


# --- Saída do GlazeWM -----------------------------------------------------------
# Os processos que o GlazeWM lança ficam no mesmo "job" do Windows e morrem
# quando ele termina — por isso os shutdown_commands não podem fazer trabalho
# demorado. "on-exit" só lança um processo independente (fora do job) e sai;
# esse processo ("after-exit") espera que o GlazeWM termine e então desliga o
# "não suspender" e volta a mostrar janelas que tenham ficado escondidas.
UNCLOAK_PS1 = HERE / "uncloak.ps1"


def _spawn_detached(*args):
    flags = 0x00000008 | 0x00000200  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    cmd = [str(PYTHONW), "-I", str(Path(__file__).resolve()), *args]
    try:
        subprocess.Popen(cmd, creationflags=flags | 0x01000000, close_fds=True)  # + BREAKAWAY_FROM_JOB
    except OSError:
        subprocess.Popen(cmd, creationflags=flags, close_fds=True)


def on_exit():
    _spawn_detached("after-exit")


def after_exit():
    def glaze_running():
        out = subprocess.run(["tasklist", "/FI", "IMAGENAME eq glazewm.exe", "/NH"],
                             capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
        return "glazewm.exe" in out.stdout.lower()

    deadline = time.monotonic() + 20
    while glaze_running() and time.monotonic() < deadline:
        time.sleep(0.5)
    awake_off()
    if UNCLOAK_PS1.exists():
        subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass",
                        "-File", str(UNCLOAK_PS1), "-WaitForGlazeExit"],
                       creationflags=CREATE_NO_WINDOW)


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
SPLASH_DIR = HERE / "arranque"
PROGRESS_FILE = SPLASH_DIR / "progress.json"
SPLASH_TITLE = "Zebar - omarchy-catppuccin / splash"
GLAZEWM_EXE = PROGRAM_FILES / "glzr.io" / "GlazeWM" / "glazewm.exe"
BOOT_QUIET_S = 3     # sai quando nada muda (janelas/títulos) durante 3 s seguidos
BOOT_CAP_S = 60      # limite de segurança: o ecrã nunca fica mais do que isto

# Configuração do arranque, editável pelo utilizador (Documentos\Guia de Atalhos\arranque.txt):
#   animacao = cafe
#   bat = C:\caminho\programa.bat | http://localhost:3000 | Nome   (endereço e nome opcionais)
ARRANQUE_FILE = HERE / "guia" / "arranque.txt"
# Animações do ecrã de arranque: nome -> (rótulo, imagem da cortina nativa, largura, altura).
# A imagem é o 1.º quadro da animação, no mesmo tamanho e sítio (centro a ANIM_CY da altura)
# em que o splash.html a desenha: assim a passagem cortina -> animação não se nota.
# Nova animação: entrada aqui + bloco data-anim no splash.html + BMP (ver COMO-FOI-FEITO.md).
ANIMACOES = {
    "cafe": ("Café", "cafe.bmp", 280, 280),
}
ANIM_CY = 0.38
BAT_TRAY = HERE / "bat_tray.py"  # corre cada .bat escondido, com ícone na área de notificação


def _arranque_cfg():
    """Lê arranque.txt: {"animacao": nome, "bats": [{"path", "url", "name"}]}."""
    cfg = {"animacao": "cafe", "bats": []}
    try:
        lines = ARRANQUE_FILE.read_text(encoding="utf-8-sig").splitlines()
    except OSError:
        return cfg
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = (p.strip() for p in line.split("=", 1))
        key = key.lower()
        if key in ("animacao", "animação"):
            name = value.lower().replace("é", "e")
            if name in ANIMACOES:
                cfg["animacao"] = name
        elif key == "bat" and value:
            parts = [p.strip().strip('"') for p in value.split("|")] + ["", ""]
            if parts[0]:
                cfg["bats"].append({"path": parts[0], "url": parts[1], "name": parts[2] or Path(parts[0]).stem})
    return cfg


def _set_animacao(name):
    """Grava "animacao = name" em arranque.txt, mantendo o resto do ficheiro."""
    try:
        lines = ARRANQUE_FILE.read_text(encoding="utf-8-sig").splitlines()
    except OSError:
        lines = []
    for i, raw in enumerate(lines):
        s = raw.strip()
        if not s.startswith("#") and "=" in s and s.split("=", 1)[0].strip().lower() in ("animacao", "animação"):
            lines[i] = f"animacao = {name}"
            break
    else:
        lines.append(f"animacao = {name}")
    tmp = ARRANQUE_FILE.with_suffix(".tmp")
    tmp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    os.replace(tmp, ARRANQUE_FILE)

kernel32.GetCurrentProcess.restype = HANDLE
kernel32.SetPriorityClass.argtypes = [HANDLE, wintypes.DWORD]
user32.SetWindowPos.argtypes = [HWND, HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.UINT]
user32.PostMessageW.argtypes = [HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]


class _Progress:
    """progress.json escrito de forma atómica (tmp + replace, com novas tentativas)."""

    def __init__(self, animacao="cafe", preview=False):
        self.data = {"boot_id": str(time.time_ns()), "started": time.time(), "animacao": animacao,
                     "preview": preview, "steps": [], "fim": False}
        self.save()

    def save(self):
        tmp = PROGRESS_FILE.with_suffix(".tmp")
        tmp.write_text(json.dumps(self.data, ensure_ascii=False), encoding="utf-8")
        for _ in range(10):
            try:
                os.replace(tmp, PROGRESS_FILE)
                return
            except PermissionError:  # o Zebar pode estar a ler neste instante
                time.sleep(0.02)

    def step(self, sid, label, state="a_carregar"):
        for s in self.data["steps"]:
            if s["id"] == sid:
                s["state"] = state
                break
        else:
            self.data["steps"].append({"id": sid, "label": label, "state": state})
        self.save()

    def finish(self):
        self.data["fim"] = True
        self.save()


def _popen_detached(cmd, **kw):
    """Lança fora do job da tarefa agendada (sobrevive ao fim da tarefa)."""
    flags = 0x00000008 | 0x00000200  # DETACHED_PROCESS | CREATE_NEW_PROCESS_GROUP
    try:
        return subprocess.Popen(cmd, creationflags=flags | 0x01000000, close_fds=True, **kw)  # + BREAKAWAY
    except OSError:
        return subprocess.Popen(cmd, creationflags=flags, close_fds=True, **kw)


def _wait_for(predicate, timeout, poll=0.1):
    end = time.monotonic() + timeout
    while time.monotonic() < end:
        result = predicate()
        if result:
            return result
        time.sleep(poll)
    return None


def _splash_to_top():
    """O guia e o painel (também top_most) nascem depois do splash e ficariam
    por cima dele: volta a pô-lo no topo, sem o ativar."""
    hwnd = user32.FindWindowW(None, SPLASH_TITLE)
    if hwnd:
        HWND_TOPMOST, SWP_NOSIZE, SWP_NOMOVE, SWP_NOACTIVATE = HWND(-1), 0x1, 0x2, 0x10
        user32.SetWindowPos(hwnd, HWND_TOPMOST, 0, 0, 0, 0, SWP_NOSIZE | SWP_NOMOVE | SWP_NOACTIVATE)


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


SPLASH_READY = "Local\\MorgSplashReady"
COVER_TITLE = "Morg Keys arranque"


class _BlackCover:
    """Cortina preta nativa (Win32, sem navegador) por cima de tudo, desde o
    primeiro instante do arranque: o WebView2 do ecrã de arranque chega a demorar ~8 s
    a pintar com o disco a frio, e sem isto via-se o ambiente de trabalho.
    Fica até a animação estar pronta (também em fundo preto) e então fecha-se."""

    def __init__(self, animacao="cafe"):
        import threading
        _, self.image, self.img_w, self.img_h = ANIMACOES.get(animacao, ANIMACOES["cafe"])
        self.hwnd = None
        self._ready = threading.Event()
        threading.Thread(target=self._run, daemon=True).start()
        self._ready.wait(2)

    def _run(self):
        WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
        user32.DefWindowProcW.argtypes = [HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
        user32.DefWindowProcW.restype = ctypes.c_ssize_t

        class PAINTSTRUCT(ctypes.Structure):
            _fields_ = [("hdc", wintypes.HDC), ("fErase", wintypes.BOOL), ("rcPaint", wintypes.RECT),
                        ("fRestore", wintypes.BOOL), ("fIncUpdate", wintypes.BOOL), ("rgbReserved", ctypes.c_byte * 32)]

        gdi32 = ctypes.WinDLL("gdi32")
        gdi32.CreateCompatibleDC.restype = wintypes.HDC
        gdi32.CreateCompatibleDC.argtypes = [wintypes.HDC]
        gdi32.SelectObject.restype = wintypes.HGDIOBJ
        gdi32.SelectObject.argtypes = [wintypes.HDC, wintypes.HGDIOBJ]
        gdi32.BitBlt.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                 wintypes.HDC, ctypes.c_int, ctypes.c_int, wintypes.DWORD]
        gdi32.DeleteDC.argtypes = [wintypes.HDC]
        user32.BeginPaint.restype = wintypes.HDC
        user32.BeginPaint.argtypes = [HWND, ctypes.c_void_p]
        user32.EndPaint.argtypes = [HWND, ctypes.c_void_p]
        user32.LoadImageW.restype = wintypes.HANDLE
        user32.LoadImageW.argtypes = [wintypes.HINSTANCE, wintypes.LPCWSTR, wintypes.UINT,
                                      ctypes.c_int, ctypes.c_int, wintypes.UINT]
        # 1.º quadro da animação escolhida, no MESMO sítio e tamanho em que o
        # splash.html o desenha (centro horizontal, centro a ANIM_CY da altura):
        # quando a animação assume o lugar, não há salto.
        logo = user32.LoadImageW(None, str(SPLASH_DIR / self.image), 0, 0, 0, 0x10)  # IMAGE_BITMAP, LR_LOADFROMFILE
        img_w, img_h = self.img_w, self.img_h

        def proc(hwnd, msg, wp, lp):
            if msg == 0x000F and logo:  # WM_PAINT
                ps = PAINTSTRUCT()
                hdc = user32.BeginPaint(hwnd, ctypes.byref(ps))
                mem = gdi32.CreateCompatibleDC(hdc)
                old = gdi32.SelectObject(mem, logo)
                sw, sh = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
                gdi32.BitBlt(hdc, (sw - img_w) // 2, round(sh * ANIM_CY) - img_h // 2,
                             img_w, img_h, mem, 0, 0, 0x00CC0020)  # SRCCOPY
                gdi32.SelectObject(mem, old)
                gdi32.DeleteDC(mem)
                user32.EndPaint(hwnd, ctypes.byref(ps))
                return 0
            if msg == 0x0002:  # WM_DESTROY
                user32.PostQuitMessage(0)
                return 0
            return user32.DefWindowProcW(hwnd, msg, wp, lp)

        self._proc = WNDPROC(proc)  # manter vivo enquanto a janela existir

        class WNDCLASSW(ctypes.Structure):
            _fields_ = [("style", wintypes.UINT), ("lpfnWndProc", WNDPROC), ("cbClsExtra", ctypes.c_int),
                        ("cbWndExtra", ctypes.c_int), ("hInstance", wintypes.HINSTANCE), ("hIcon", wintypes.HICON),
                        ("hCursor", wintypes.HANDLE), ("hbrBackground", wintypes.HBRUSH),
                        ("lpszMenuName", wintypes.LPCWSTR), ("lpszClassName", wintypes.LPCWSTR)]

        gdi32.GetStockObject.restype = wintypes.HGDIOBJ
        hinst = kernel32.GetModuleHandleW(None)
        wc = WNDCLASSW(lpfnWndProc=self._proc, hInstance=hinst, lpszClassName="MorgBlackCover",
                       hbrBackground=gdi32.GetStockObject(4))  # BLACK_BRUSH
        user32.RegisterClassW(ctypes.byref(wc))
        user32.CreateWindowExW.restype = HWND
        user32.CreateWindowExW.argtypes = [wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD,
                                           ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                           HWND, wintypes.HMENU, wintypes.HINSTANCE, wintypes.LPVOID]
        w, h = user32.GetSystemMetrics(0), user32.GetSystemMetrics(1)
        ex = 0x00000008 | 0x00000080 | 0x08000000  # TOPMOST | TOOLWINDOW | NOACTIVATE
        self.hwnd = user32.CreateWindowExW(ex, "MorgBlackCover", COVER_TITLE, 0x80000000 | 0x10000000,  # POPUP|VISIBLE
                                           0, 0, w, h, None, None, hinst, None)
        user32.ShowCursor(False)
        self._ready.set()
        msg = wintypes.MSG()
        while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
            user32.TranslateMessage(ctypes.byref(msg))
            user32.DispatchMessageW(ctypes.byref(msg))

    def close(self):
        if self.hwnd:
            user32.ShowCursor(True)
            user32.PostMessageW(self.hwnd, 0x0010, 0, 0)  # WM_CLOSE
            self.hwnd = None


def _window_signature():
    """Janelas geridas e respetivos títulos: enquanto as apps abrem janelas ou
    as páginas carregam, isto muda. Quando fica igual uns segundos, assentou."""
    return tuple(sorted((w["id"], w.get("title", "")) for _, w in _windows_by_workspace(_workspaces() or [])))


def splash_ready():
    """Chamado pela página do splash quando já está desenhada por cima de tudo."""
    handle = kernel32.OpenEventW(EVENT_MODIFY_STATE, False, SPLASH_READY)
    if handle:
        kernel32.SetEvent(handle)
        kernel32.CloseHandle(handle)


def boot():
    kernel32.SetPriorityClass(kernel32.GetCurrentProcess(), 0x20)  # NORMAL_PRIORITY_CLASS
    cfg = _arranque_cfg()
    # Primeiro de tudo: preto (com o 1.º quadro da animação) por cima do ambiente de trabalho.
    cover = _BlackCover(cfg["animacao"])
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
        procs = list(dict.fromkeys(e["process"] for e in layout.get("windows", [])))
        for p in procs:
            progress.step(f"app:{p}", APP_LABELS.get(p, p))
        left = {p: sum(1 for e in layout["windows"] if e["process"] == p) for p in procs}

        def placed(entry):
            left[entry["process"]] -= 1
            if left[entry["process"]] == 0:
                progress.step(f"app:{entry['process']}", APP_LABELS.get(entry["process"], entry["process"]), "feito")

        pending = _restore(layout, log, on_placed=placed, wait_s=10)
        for entry in pending:
            progress.step(f"app:{entry['process']}", APP_LABELS.get(entry["process"], entry["process"]), "falhou")
            log(f"não encontrei janela para {entry['process']} (ws {entry['workspace']})")
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
    kernel32.ReleaseMutex(boot_mutex)
    kernel32.CloseHandle(boot_mutex)
    kernel32.CloseHandle(ready)

def animacao_preview(name=None):
    """Mostra o ecrã de arranque uns segundos, com etapas de exemplo."""
    name = name if name in ANIMACOES else _arranque_cfg()["animacao"]
    handle = kernel32.OpenMutexW(SYNCHRONIZE, False, BOOT_MUTEX)
    if handle:  # arranque a decorrer: não mexe no ecrã dele
        kernel32.CloseHandle(handle)
        return
    if user32.FindWindowW(None, SPLASH_TITLE) or not ZEBAR.exists():
        return
    progress = _Progress(name, preview=True)
    _popen_detached([str(ZEBAR), "start-widget-preset", "--pack", "omarchy-catppuccin",
                     "--widget-name", "splash", "--preset", "default"])
    time.sleep(0.8)
    for sid, label in (("anim", f"Animação: {ANIMACOES[name][0]}"), ("barra", "Barra"),
                       ("glazewm", "Gestor de janelas"), ("apps", "Apps")):
        progress.step(sid, label)
        time.sleep(0.9)
        progress.step(sid, label, "feito")
    time.sleep(1.2)
    progress.finish()


ANIM_TAP_FILE = HERE / ".anim-tap"
# Conteúdo: "<tick> <antes deste toque> <tap|hold> <antes do toque anterior>"
ANIM_REPEAT_MS = 150   # teclas mais próximas do que isto = tecla segurada (repetição automática)


def animacao_tap():
    """Alt+Esc, E (na camada; o painel continua aberto):
    - tocar  -> passa à animação seguinte (o painel mostra qual ficou);
    - segurar -> ao largar, mostra a animação escolhida.
    Segurar uma tecla faz o Windows repeti-la: a 1.ª repetição vem ~0,25-1 s
    depois de carregar (parece um 2.º toque), as seguintes a cada ~33 ms. Cada
    uma corre isto outra vez; duas chamadas a menos de ANIM_REPEAT_MS = segurar.
    Nessa altura já houve duas trocas (a pressão e a 1.ª repetição): volta-se à
    animação de antes da pressão, guardada no 4.º campo."""
    now = kernel32.GetTickCount64()
    with _NamedMutex("Local\\MorgAnimTap", 1000) as owned:
        if not owned:
            return
        try:
            last, prev, state, before = ANIM_TAP_FILE.read_text(encoding="utf-8").split()
            last = int(last)
        except (OSError, ValueError):
            last, prev, state, before = 0, "-", "tap", "-"
        if now - last >= ANIM_REPEAT_MS:  # toque novo (ou 1.ª repetição)
            names = list(ANIMACOES)
            current = _arranque_cfg()["animacao"]
            _set_animacao(names[(names.index(current) + 1) % len(names)])
            ANIM_TAP_FILE.write_text(f"{now} {current} tap {prev}", encoding="utf-8")
            return
        ANIM_TAP_FILE.write_text(f"{now} {prev} hold {before}", encoding="utf-8")
        if state == "hold":  # esta pressão já tem quem trate dela
            return
    # Segurar detetado: repõe a animação de antes da pressão e espera que a
    # tecla seja largada (as repetições deixam de atualizar o ficheiro). Só
    # então sai da camada: com a camada ativa as repetições não chegam à app.
    prev = before if before in ANIMACOES else prev
    if prev in ANIMACOES:
        _set_animacao(prev)
    deadline = time.monotonic() + 15
    while time.monotonic() < deadline:
        time.sleep(0.05)
        try:
            last = int(ANIM_TAP_FILE.read_text(encoding="utf-8").split()[0])
        except (OSError, ValueError, IndexError):
            break
        if kernel32.GetTickCount64() - last > 250:
            break
    _glaze("command", "wm-disable-binding-mode", "--name", "sistema")
    layer_hide()
    animacao_preview(prev if prev in ANIMACOES else None)


def animacao_set(name=None):
    """Alt+Esc, E: passa à animação seguinte (ou à indicada), grava e mostra-a."""
    names = list(ANIMACOES)
    if name not in ANIMACOES:
        current = _arranque_cfg()["animacao"]
        name = names[(names.index(current) + 1) % len(names)]
    _set_animacao(name)
    animacao_preview(name)


# --- Sistema --------------------------------------------------------------------
def lock():
    user32.LockWorkStation()


def power(action):
    """Reiniciar/desligar só depois de confirmar (o botão por omissão é "Não")."""
    texts = {"reboot": ("Reiniciar o computador agora?", "/r"),
             "shutdown": ("Desligar o computador agora?", "/s")}
    question, flag = texts[action]
    MB_YESNO, MB_ICONQUESTION, MB_DEFBUTTON2 = 0x4, 0x20, 0x100
    MB_SETFOREGROUND, MB_TOPMOST, IDYES = 0x10000, 0x40000, 6
    answer = user32.MessageBoxW(None, question, "Sistema",
                                MB_YESNO | MB_ICONQUESTION | MB_DEFBUTTON2 | MB_SETFOREGROUND | MB_TOPMOST)
    if answer == IDYES:
        subprocess.run(["shutdown", flag, "/t", "0"], creationflags=CREATE_NO_WINDOW)


def main(argv):
    cmd = argv[1:] or [""]
    if cmd == ["awake", "status"]:
        print(awake_status())
    elif cmd == ["awake", "toggle"]:
        print(awake_toggle())
    elif cmd == ["awake", "off"]:
        print(awake_off())
    elif cmd == ["awake-hold"]:
        awake_hold()
    elif cmd == ["quick"]:
        quick_settings()
    elif cmd == ["guide"]:
        guide()
    elif cmd == ["guide-hide"]:
        guide_hide()
    elif cmd == ["guide-ensure-hidden"]:
        guide_ensure_hidden()
    elif cmd == ["bar", "toggle"]:
        bar_toggle()
    elif cmd == ["restore-min"]:
        restore_minimized()
    elif cmd == ["layout-save"]:
        layout_save()
    elif cmd == ["layout-restore"]:
        layout_restore()
    elif cmd == ["boot"]:
        boot()
    elif cmd == ["splash-ready"]:
        splash_ready()
    elif cmd[0] == "animacao" and len(cmd) <= 2:
        if len(cmd) == 2 and cmd[1] == "preview":
            animacao_preview()
        elif len(cmd) == 2 and cmd[1] == "tap":
            animacao_tap()
        else:
            animacao_set(cmd[1] if len(cmd) == 2 and cmd[1] != "next" else None)
    elif cmd == ["apps-apply"]:
        apps_apply()
    elif cmd == ["apps-apply", "--skip-missing"]:
        apps_apply(skip_missing=True)
    elif cmd == ["apps-edit"]:
        apps_edit()
    elif cmd == ["layer-show"]:
        layer_show()
    elif cmd == ["layer-hide"]:
        layer_hide()
    elif cmd == ["on-exit"]:
        on_exit()
    elif cmd == ["after-exit"]:
        after_exit()
    elif cmd == ["lock"]:
        lock()
    elif len(cmd) == 2 and cmd[0] == "power" and cmd[1] in ("reboot", "shutdown"):
        power(cmd[1])
    else:
        print(__doc__)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
