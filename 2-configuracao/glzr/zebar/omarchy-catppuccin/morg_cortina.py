"""Cortina nativa (Win32, sem navegador) no início do arranque: o ambiente de trabalho escurece aos poucos."""

import ctypes
from ctypes import wintypes

from morg_win32 import HWND, kernel32, user32

COVER_TITLE = "Morg Keys arranque"
ESCURECER_MS = 1200  # do ambiente de trabalho ao preto


def _alfa(ms, duracao=ESCURECER_MS):
    """Opacidade da cortina (0 = transparente, 255 = preto) `ms` depois de aparecer: começa depressa e
    abranda no fim (ease-out cúbico), como o escurecer de um ecrã."""
    p = min(1.0, max(0.0, ms / duracao))
    return round(255 * (1 - (1 - p) ** 3))


class _BlackCover:
    """Cortina nativa por cima de tudo desde o início do arranque: nasce transparente e escurece até ao
    preto em ESCURECER_MS (janela em camadas, SetLayeredWindowAttributes). O WebView2 do ecrã de arranque
    chega a demorar segundos a pintar; até lá a cortina tapa o ambiente de trabalho. Fecha-se quando o ecrã
    de boas-vindas (também em fundo preto) está desenhado por cima dela."""

    def __init__(self):
        import threading
        self.hwnd = None
        self._ready = threading.Event()
        threading.Thread(target=self._run, daemon=True).start()
        self._ready.wait(2)

    def _run(self):  # pragma: no cover — cola Win32: janela em camadas e laço de mensagens (validacao-manual)
        WNDPROC = ctypes.WINFUNCTYPE(ctypes.c_ssize_t, HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM)
        user32.DefWindowProcW.argtypes = [HWND, wintypes.UINT, wintypes.WPARAM, wintypes.LPARAM]
        user32.DefWindowProcW.restype = ctypes.c_ssize_t
        user32.SetLayeredWindowAttributes.argtypes = [HWND, wintypes.DWORD, wintypes.BYTE, wintypes.DWORD]
        user32.SetTimer.argtypes = [HWND, ctypes.c_size_t, wintypes.UINT, ctypes.c_void_p]
        user32.KillTimer.argtypes = [HWND, ctypes.c_size_t]
        # Esta thread em px físicos (perceção de DPI por monitor, v2): a cortina cobre o ecrã exato.
        user32.SetThreadDpiAwarenessContext.restype = ctypes.c_void_p
        user32.SetThreadDpiAwarenessContext.argtypes = [ctypes.c_void_p]
        user32.SetThreadDpiAwarenessContext(ctypes.c_void_p(-4))  # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2
        LWA_ALPHA, WM_TIMER, WM_DESTROY = 0x2, 0x0113, 0x0002
        inicio = kernel32.GetTickCount64()

        def proc(hwnd, msg, wp, lp):
            if msg == WM_TIMER:  # escurecer: um passo a cada ~16 ms até ao preto
                alfa = _alfa(kernel32.GetTickCount64() - inicio)
                user32.SetLayeredWindowAttributes(hwnd, 0, alfa, LWA_ALPHA)
                if alfa >= 255:
                    user32.KillTimer(hwnd, 1)
                return 0
            if msg == WM_DESTROY:
                user32.PostQuitMessage(0)
                return 0
            return user32.DefWindowProcW(hwnd, msg, wp, lp)

        self._proc = WNDPROC(proc)  # manter vivo enquanto a janela existir

        class WNDCLASSW(ctypes.Structure):
            _fields_ = [("style", wintypes.UINT), ("lpfnWndProc", WNDPROC), ("cbClsExtra", ctypes.c_int),
                        ("cbWndExtra", ctypes.c_int), ("hInstance", wintypes.HINSTANCE), ("hIcon", wintypes.HICON),
                        ("hCursor", wintypes.HANDLE), ("hbrBackground", wintypes.HBRUSH),
                        ("lpszMenuName", wintypes.LPCWSTR), ("lpszClassName", wintypes.LPCWSTR)]

        gdi32 = ctypes.WinDLL("gdi32")
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
        ex = 0x00000008 | 0x00000080 | 0x08000000 | 0x00080000  # TOPMOST | TOOLWINDOW | NOACTIVATE | LAYERED
        self.hwnd = user32.CreateWindowExW(ex, "MorgBlackCover", COVER_TITLE, 0x80000000,  # POPUP (escondida)
                                           0, 0, w, h, None, None, hinst, None)
        user32.SetLayeredWindowAttributes(self.hwnd, 0, 0, LWA_ALPHA)  # nasce transparente…
        user32.ShowWindow(self.hwnd, 4)  # SW_SHOWNOACTIVATE
        user32.SetTimer(self.hwnd, 1, 16, None)  # …e escurece (WM_TIMER)
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
