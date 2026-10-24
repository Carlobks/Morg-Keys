"""Corre um programa .bat sem janela, com ícone na área de notificação.

Uso:  pyw.exe -I bat_tray.py <caminho.bat> [endereço] [nome]

Lançado no arranque (bar_helper.py boot) para cada linha "bat = ..." de
arranque.txt. O .bat corre na sua própria pasta, sem consola, com a saída em
~/.glzr/arranque/<nome>.log. Menu do ícone (clique esquerdo ou direito):
  [Abrir no navegador] · Ver registo ao vivo · Reiniciar · Parar/Iniciar · Fechar

Com endereço local (ex.: http://localhost:3000), "a correr" = a porta responde.
Assim também se reconhece um servidor arrancado fora daqui, e parar mata quem
está a escutar nessa porta. Sem endereço, "a correr" = o processo que este
ícone lançou ainda está vivo.
"""

import ctypes
import hashlib
import os
import socket
import subprocess
import sys
import time
from ctypes import wintypes
from pathlib import Path
from urllib.parse import urlparse

CREATE_NO_WINDOW = 0x08000000
LOG_DIR = Path.home() / ".glzr" / "arranque"

user32 = ctypes.WinDLL("user32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)
shell32 = ctypes.WinDLL("shell32", use_last_error=True)
HWND = wintypes.HWND

WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
user32.DefWindowProcW.argtypes = [HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.DefWindowProcW.restype = ctypes.c_ssize_t
user32.CreateWindowExW.restype = HWND
user32.CreateWindowExW.argtypes = [wintypes.DWORD, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.DWORD,
                                   ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                   HWND, wintypes.HMENU, wintypes.HINSTANCE, wintypes.LPVOID]
user32.CreatePopupMenu.restype = wintypes.HMENU
user32.AppendMenuW.argtypes = [wintypes.HMENU, wintypes.UINT, ctypes.c_size_t, wintypes.LPCWSTR]
user32.TrackPopupMenu.argtypes = [wintypes.HMENU, wintypes.UINT, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                  HWND, ctypes.c_void_p]
user32.SetForegroundWindow.argtypes = [HWND]
user32.PostMessageW.argtypes = [HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
user32.SetTimer.argtypes = [HWND, ctypes.c_size_t, wintypes.UINT, ctypes.c_void_p]
user32.RegisterWindowMessageW.restype = wintypes.UINT
user32.LoadIconW.restype = wintypes.HICON
shell32.ExtractIconW.restype = wintypes.HICON
shell32.ExtractIconW.argtypes = [wintypes.HINSTANCE, wintypes.LPCWSTR, wintypes.UINT]
kernel32.CreateMutexW.restype = wintypes.HANDLE


class NOTIFYICONDATAW(ctypes.Structure):
    _fields_ = [("cbSize", wintypes.DWORD), ("hWnd", HWND), ("uID", wintypes.UINT), ("uFlags", wintypes.UINT),
                ("uCallbackMessage", wintypes.UINT), ("hIcon", wintypes.HICON), ("szTip", wintypes.WCHAR * 128),
                ("dwState", wintypes.DWORD), ("dwStateMask", wintypes.DWORD), ("szInfo", wintypes.WCHAR * 256),
                ("uVersion", wintypes.UINT), ("szInfoTitle", wintypes.WCHAR * 64), ("dwInfoFlags", wintypes.DWORD),
                ("guidItem", ctypes.c_byte * 16), ("hBalloonIcon", wintypes.HICON)]


NIM_ADD, NIM_MODIFY, NIM_DELETE = 0, 1, 2
NIF_MESSAGE, NIF_ICON, NIF_TIP = 1, 2, 4
WM_TRAY = 0x0400 + 1
ID_OPEN, ID_LOG, ID_RESTART, ID_TOGGLE, ID_QUIT = 1, 2, 3, 4, 5


def _local_port(url):
    try:
        u = urlparse(url)
    except ValueError:
        return None
    if u.hostname not in ("localhost", "127.0.0.1"):
        return None
    return u.port or (443 if u.scheme == "https" else 80)


def _port_open(port):
    try:
        with socket.create_connection(("127.0.0.1", port), timeout=0.3):
            return True
    except OSError:
        return False


def _kill_tree(pid):
    subprocess.run(["taskkill", "/T", "/F", "/PID", str(pid)], creationflags=CREATE_NO_WINDOW,
                   capture_output=True, timeout=30, check=False)


# --- O programa ------------------------------------------------------------------
class Program:
    def __init__(self, bat, url, name):
        self.bat, self.url, self.name = Path(bat), url, name
        self.port = _local_port(url) if url else None
        self.log = LOG_DIR / f"{''.join(c if c.isalnum() or c in '-_' else '_' for c in name)}.log"
        self.proc = None

    def running(self):
        if self.port:
            return _port_open(self.port)
        return self.proc is not None and self.proc.poll() is None

    def start(self):
        if self.running():
            return
        LOG_DIR.mkdir(parents=True, exist_ok=True)
        log = open(self.log, "w", encoding="utf-8", errors="replace")  # noqa: SIM115 — fica aberto enquanto o .bat corre (é o stdout dele)
        log.write(f"--- {time.strftime('%Y-%m-%d %H:%M:%S')} {self.bat} iniciado ---\n")
        log.flush()
        self.proc = subprocess.Popen(["cmd.exe", "/c", str(self.bat)], cwd=str(self.bat.parent), stdout=log,
                                     stderr=subprocess.STDOUT, stdin=subprocess.DEVNULL,
                                     creationflags=CREATE_NO_WINDOW)

    def stop(self):
        """Mata a árvore que este ícone lançou e, com porta, também quem a escuta
        (cobre um servidor arrancado fora daqui)."""
        if self.proc is not None and self.proc.poll() is None:
            _kill_tree(self.proc.pid)
        self.proc = None
        if self.port and _port_open(self.port):
            ps = (f"Get-NetTCPConnection -LocalPort {self.port} -State Listen -ErrorAction SilentlyContinue | "
                  "Select-Object -ExpandProperty OwningProcess -Unique")
            out = subprocess.run(["powershell", "-NoProfile", "-Command", ps], capture_output=True, text=True,
                                 creationflags=CREATE_NO_WINDOW, timeout=30, check=False)
            for pid in out.stdout.split():
                if pid.isdigit() and int(pid) > 4:
                    _kill_tree(pid)
            for _ in range(20):
                if not _port_open(self.port):
                    break
                time.sleep(0.25)


# --- Ícone e menu ------------------------------------------------------------------
class Tray:
    def __init__(self, program):
        self.program = program
        self._proc = WNDPROC(self._wndproc)
        hinst = kernel32.GetModuleHandleW(None)

        class WNDCLASSW(ctypes.Structure):
            _fields_ = [("style", wintypes.UINT), ("lpfnWndProc", WNDPROC), ("cbClsExtra", ctypes.c_int),
                        ("cbWndExtra", ctypes.c_int), ("hInstance", wintypes.HINSTANCE), ("hIcon", wintypes.HICON),
                        ("hCursor", wintypes.HANDLE), ("hbrBackground", wintypes.HBRUSH),
                        ("lpszMenuName", wintypes.LPCWSTR), ("lpszClassName", wintypes.LPCWSTR)]

        wc = WNDCLASSW(lpfnWndProc=self._proc, hInstance=hinst, lpszClassName="MorgBatTray")
        user32.RegisterClassW(ctypes.byref(wc))
        self.hwnd = user32.CreateWindowExW(0, "MorgBatTray", program.name, 0, 0, 0, 0, 0, None, None, hinst, None)
        # Se o Explorador reiniciar, a área de notificação perde os ícones: volta a pôr.
        self.taskbar_created = user32.RegisterWindowMessageW("TaskbarCreated")
        self.icon = self._pick_icon()
        self.running = None
        self._add()
        user32.SetTimer(self.hwnd, 1, 3000, None)
        self.refresh()

    def _pick_icon(self):
        """Ícone do Node.js para projetos npm/node; senão o da linha de comandos."""
        try:
            text = self.program.bat.read_text(encoding="oem", errors="replace").lower()
        except OSError:
            text = ""
        node = Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "nodejs" / "node.exe"
        exe = node if ("npm" in text or "node" in text) and node.exists() else \
            Path(os.environ.get("SystemRoot", r"C:\Windows")) / "System32" / "cmd.exe"
        return shell32.ExtractIconW(None, str(exe), 0) or user32.LoadIconW(None, ctypes.c_void_p(32512))

    def _nid(self):
        nid = NOTIFYICONDATAW(cbSize=ctypes.sizeof(NOTIFYICONDATAW), hWnd=self.hwnd, uID=1,
                              uFlags=NIF_MESSAGE | NIF_ICON | NIF_TIP, uCallbackMessage=WM_TRAY,
                              hIcon=self.icon)
        state = "a correr" if self.running else "parado"
        nid.szTip = f"{self.program.name} — {state}"[:127]
        return nid

    def _add(self):
        shell32.Shell_NotifyIconW(NIM_ADD, ctypes.byref(self._nid()))

    def refresh(self):
        running = self.program.running()
        if running != self.running:
            self.running = running
            shell32.Shell_NotifyIconW(NIM_MODIFY, ctypes.byref(self._nid()))

    def menu(self):
        m = user32.CreatePopupMenu()
        if self.program.url:
            user32.AppendMenuW(m, 0 if self.running else 0x1, ID_OPEN, "Abrir no navegador")  # 0x1 = MF_GRAYED
        user32.AppendMenuW(m, 0, ID_LOG, "Ver registo ao vivo")
        user32.AppendMenuW(m, 0x800, 0, None)  # separador
        user32.AppendMenuW(m, 0, ID_RESTART, "Reiniciar")
        user32.AppendMenuW(m, 0, ID_TOGGLE, "Parar" if self.running else "Iniciar")
        user32.AppendMenuW(m, 0x800, 0, None)
        user32.AppendMenuW(m, 0, ID_QUIT, "Fechar (para o programa)")
        pt = wintypes.POINT()
        user32.GetCursorPos(ctypes.byref(pt))
        user32.SetForegroundWindow(self.hwnd)  # sem isto o menu não fecha ao clicar fora
        cmd = user32.TrackPopupMenu(m, 0x0100 | 0x0002, pt.x, pt.y, 0, self.hwnd, None)  # RETURNCMD|RIGHTBUTTON
        user32.PostMessageW(self.hwnd, 0, 0, 0)
        user32.DestroyMenu(m)
        self.command(cmd)

    def command(self, cmd):
        p = self.program
        if cmd == ID_OPEN:
            os.startfile(p.url)
        elif cmd == ID_LOG:
            wt = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WindowsApps" / "wt.exe"
            tail = f"Get-Content -Path '{p.log}' -Tail 200 -Wait"
            subprocess.Popen([str(wt), "-w", "new", "--title", f"{p.name} (registo)",
                              "powershell", "-NoProfile", "-NoExit", "-Command", tail])
        elif cmd == ID_RESTART:
            p.stop()
            p.start()
        elif cmd == ID_TOGGLE:
            p.stop() if self.running else p.start()
        elif cmd == ID_QUIT:
            p.stop()
            user32.DestroyWindow(self.hwnd)
            return
        self.refresh()

    def _wndproc(self, hwnd, msg, wp, lp):
        if msg == WM_TRAY and (lp & 0xFFFF) in (0x0202, 0x0205):  # LBUTTONUP / RBUTTONUP
            self.menu()
            return 0
        if msg == 0x0113:  # WM_TIMER
            self.refresh()
            return 0
        if msg == self.taskbar_created:
            self._add()
            return 0
        if msg == 0x0002:  # WM_DESTROY
            shell32.Shell_NotifyIconW(NIM_DELETE, ctypes.byref(self._nid()))
            user32.PostQuitMessage(0)
            return 0
        return user32.DefWindowProcW(hwnd, msg, wp, lp)


def main(argv):
    if len(argv) < 2 or not Path(argv[1]).exists():
        return 2
    bat = str(Path(argv[1]).resolve())
    url = argv[2] if len(argv) > 2 else ""
    name = argv[3] if len(argv) > 3 and argv[3] else Path(bat).stem
    # Um ícone por .bat: se já houver um para este ficheiro, não abre outro.
    key = hashlib.sha1(bat.lower().encode("utf-8")).hexdigest()[:12]
    mutex = kernel32.CreateMutexW(None, True, f"Local\\MorgBatTray_{key}")
    if ctypes.get_last_error() == 183:  # ERROR_ALREADY_EXISTS
        return 0
    program = Program(bat, url, name)
    program.start()
    tray = Tray(program)
    msg = wintypes.MSG()
    while user32.GetMessageW(ctypes.byref(msg), None, 0, 0) > 0:
        user32.TranslateMessage(ctypes.byref(msg))
        user32.DispatchMessageW(ctypes.byref(msg))
    kernel32.CloseHandle(mutex)
    del tray
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
