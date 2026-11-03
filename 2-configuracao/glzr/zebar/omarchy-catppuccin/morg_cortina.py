"""Cortina preta nativa (Win32, sem navegador) por cima de tudo no início do arranque."""

import ctypes
import time
from ctypes import wintypes

from morg_config_arranque import ANIM_CY, ANIMACOES, SPLASH_DIR
from morg_win32 import HWND, kernel32, user32

COVER_TITLE = "Morg Keys arranque"

# Arranque do PC: o bar_helper.py abre a cortina ANTES de importar os outros módulos (abrir_cedo) e o
# boot() usa essa. Fora do "boot" ficam None e o boot() abre a sua, como antes.
CORTINA_CEDO = None
INICIO_CEDO = None  # time.time() quando o abrir_cedo começou (medição do arranque)



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
        self.visivel_em = time.time()  # medição do arranque

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


def abrir_cedo(animacao):
    """Arranque do PC: prioridade normal e cortina já, chamado pelo bar_helper.py antes de importar os
    outros módulos. Com o disco a frio cada ficheiro lido é tempo de ambiente de trabalho à vista."""
    global CORTINA_CEDO, INICIO_CEDO
    INICIO_CEDO = time.time()
    kernel32.SetPriorityClass(kernel32.GetCurrentProcess(), 0x20)  # NORMAL_PRIORITY_CLASS
    CORTINA_CEDO = _BlackCover(animacao)
