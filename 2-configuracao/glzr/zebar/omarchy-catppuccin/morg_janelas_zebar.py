"""Janelas do Zebar: guia de atalhos (Alt+K), barra (Alt+Shift+Espaço) e camada Alt+Esc."""

import ctypes
import time

from morg_glaze import _glaze
from morg_processos import HERE, _start_widget
from morg_win32 import (
    _bring_to_front,
    _focus_webview,
    _hide_when_unfocused,
    _is_cloaked,
    _NamedMutex,
    kernel32,
    user32,
)

# --- Janelas: foco e visibilidade ------------------------------------------------
GUIDE_TITLE = "Zebar - omarchy-catppuccin / guia"
BAR_TITLE = "Zebar - omarchy-catppuccin / bar"



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
            for title in (GUIDE_TITLE, "Zebar - omarchy-catppuccin / sistema", "Zebar - omarchy-catppuccin / apps"):
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
