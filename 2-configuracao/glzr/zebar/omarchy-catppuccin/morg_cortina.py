"""Cortina preta nativa (Win32, sem navegador) por cima de tudo no início do arranque."""

import ctypes
from ctypes import wintypes

from morg_config_arranque import ANIM_CY, ANIMACOES, SPLASH_DIR
from morg_win32 import ENUM_PROC, HWND, kernel32, user32

COVER_TITLE = "Morg Keys arranque"


def _fechar_ecra_preto():  # pragma: no cover — cola Win32: janelas e processos reais (validacao-manual)
    """Fecha o protetor de ecrã "Em branco" (scrnsave.scr) que a tarefa "Morg Keys (ecrã preto)" lança ao
    entrar na sessão (instalar.ps1, RegistarEcraPreto), depois de a cortina estar visível por cima dele.
    A classe da janela vem traduzida: procura-se pelo programa do processo. Devolve quantas fechou."""
    kernel32.QueryFullProcessImageNameW.argtypes = [wintypes.HANDLE, wintypes.DWORD, wintypes.LPWSTR,
                                                    ctypes.POINTER(wintypes.DWORD)]
    user32.EnumWindows.argtypes = [ENUM_PROC, wintypes.LPARAM]
    alvos = []

    def ver(hwnd, _):
        pid = wintypes.DWORD()
        user32.GetWindowThreadProcessId(hwnd, ctypes.byref(pid))
        h = kernel32.OpenProcess(0x1000, False, pid.value)  # PROCESS_QUERY_LIMITED_INFORMATION
        if h:
            nome, n = ctypes.create_unicode_buffer(260), wintypes.DWORD(260)
            if kernel32.QueryFullProcessImageNameW(h, 0, nome, ctypes.byref(n)) \
                    and nome.value.lower().endswith("\\scrnsave.scr"):
                alvos.append(hwnd)
            kernel32.CloseHandle(h)
        return True

    user32.EnumWindows(ENUM_PROC(ver), 0)
    for hwnd in alvos:
        user32.PostMessageW(hwnd, 0x0010, 0, 0)  # WM_CLOSE
    return len(alvos)


def _rect_cortina(sw, sh, dpi, img_w, img_h):
    """Onde e com que tamanho (px físicos) a cortina desenha o 1.º quadro: o mesmo sítio e tamanho do
    splash.html (centro horizontal, centro a ANIM_CY da altura; img_w×img_h em px CSS, escalados pelo DPI).
    Devolve (x, y, largura, altura). A 125 % num ecrã 1920×1080: (785, 235, 350, 350), como o SVG (A21)."""
    w, h = round(img_w * dpi / 96), round(img_h * dpi / 96)
    return (sw - w) // 2, round(sh * ANIM_CY) - h // 2, w, h



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

    def _run(self):  # pragma: no cover — cola Win32: janela, laço de mensagens e pintura GDI (validacao-manual)
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
        gdi32.StretchBlt.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                     wintypes.HDC, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int,
                                     wintypes.DWORD]
        gdi32.SetStretchBltMode.argtypes = [wintypes.HDC, ctypes.c_int]
        gdi32.SetBrushOrgEx.argtypes = [wintypes.HDC, ctypes.c_int, ctypes.c_int, ctypes.c_void_p]
        gdi32.GetObjectW.argtypes = [wintypes.HANDLE, ctypes.c_int, ctypes.c_void_p]
        user32.GetDpiForWindow.argtypes = [HWND]

        class BITMAP(ctypes.Structure):
            _fields_ = [("bmType", wintypes.LONG), ("bmWidth", wintypes.LONG), ("bmHeight", wintypes.LONG),
                        ("bmWidthBytes", wintypes.LONG), ("bmPlanes", wintypes.WORD),
                        ("bmBitsPixel", wintypes.WORD), ("bmBits", ctypes.c_void_p)]

        # Esta thread em px físicos (perceção de DPI por monitor, v2): sem isto o Windows esticava a janela
        # a 125 % e o café saía desfocado, e na passagem para o SVG nítido via-se um salto.
        user32.SetThreadDpiAwarenessContext.restype = ctypes.c_void_p
        user32.SetThreadDpiAwarenessContext.argtypes = [ctypes.c_void_p]
        user32.SetThreadDpiAwarenessContext(ctypes.c_void_p(-4))  # DPI_AWARENESS_CONTEXT_PER_MONITOR_AWARE_V2
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
        img_w, img_h = self.img_w, self.img_h  # tamanho no ecrã em px CSS (o BMP é maior: 2×, reduz-se)
        fonte = BITMAP()
        if logo:
            gdi32.GetObjectW(logo, ctypes.sizeof(BITMAP), ctypes.byref(fonte))

        def proc(hwnd, msg, wp, lp):
            if msg == 0x000F and logo:  # WM_PAINT
                ps = PAINTSTRUCT()
                hdc = user32.BeginPaint(hwnd, ctypes.byref(ps))
                mem = gdi32.CreateCompatibleDC(hdc)
                old = gdi32.SelectObject(mem, logo)
                x, y, w, h = _rect_cortina(user32.GetSystemMetrics(0), user32.GetSystemMetrics(1),
                                           user32.GetDpiForWindow(hwnd) or 96, img_w, img_h)
                gdi32.SetStretchBltMode(hdc, 4)  # HALFTONE: reduzir sem serrilhado
                gdi32.SetBrushOrgEx(hdc, 0, 0, None)
                gdi32.StretchBlt(hdc, x, y, w, h, mem, 0, 0, fonte.bmWidth, fonte.bmHeight, 0x00CC0020)  # SRCCOPY
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
