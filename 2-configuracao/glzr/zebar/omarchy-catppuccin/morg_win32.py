"""Ligação ao Windows (ctypes): bibliotecas, tipos, mutex com nome e foco/visibilidade das janelas."""

import ctypes
import time
from ctypes import wintypes

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


shell32 = ctypes.WinDLL("shell32")
shell32.ShellExecuteW.restype = ctypes.c_void_p
shell32.ShellExecuteW.argtypes = [HWND, wintypes.LPCWSTR, wintypes.LPCWSTR, wintypes.LPCWSTR,
                                  wintypes.LPCWSTR, ctypes.c_int]


kernel32.GetCurrentProcess.restype = HANDLE
kernel32.SetPriorityClass.argtypes = [HANDLE, wintypes.DWORD]
user32.SetWindowPos.argtypes = [HWND, HWND, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int, wintypes.UINT]
user32.PostMessageW.argtypes = [HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
kernel32.OpenProcess.restype = HANDLE
kernel32.OpenProcess.argtypes = [wintypes.DWORD, wintypes.BOOL, wintypes.DWORD]
kernel32.GetProcessTimes.argtypes = [HANDLE] + [ctypes.POINTER(wintypes.FILETIME)] * 4


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
    """Dá o foco do teclado à página (o WebView2 dentro da janela do Zebar).

    O foco vai para a JANELA DE TOPO: o wry (WebView2 do Tauri) reage ao
    WM_SETFOCUS dela com ICoreWebView2Controller.MoveFocus, que é o caminho
    suportado. Pôr o foco na janela interna Chrome_RenderWidgetHostHWND (como
    se fazia) deixa a página "sem foco": aparece, mas não recebe teclas.
    O WM_SETFOCUS vai também à mão, porque o SetFocus não o repete se a janela
    já tinha o foco Win32 (ex.: escondida enquanto ativa).
    """
    tid = user32.GetWindowThreadProcessId(hwnd, None)
    me = kernel32.GetCurrentThreadId()
    attached = tid and tid != me and user32.AttachThreadInput(me, tid, True)
    try:
        user32.SetFocus(hwnd)
    finally:
        if attached:
            user32.AttachThreadInput(me, tid, False)
    user32.PostMessageW(hwnd, 0x0007, 0, 0)  # WM_SETFOCUS


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
