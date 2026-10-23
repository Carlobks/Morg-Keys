"""Animação do ecrã de arranque: Alt+Esc, E (tocar/segurar), escolher e mostrar."""

import time

from morg_arranjo import BOOT_MUTEX
from morg_config_arranque import ANIMACOES, _arranque_cfg, _set_animacao
from morg_ecra_arranque import SPLASH_TITLE, _Progress
from morg_glaze import _glaze
from morg_janelas_zebar import layer_hide
from morg_processos import HERE, ZEBAR, _popen_detached
from morg_win32 import SYNCHRONIZE, _NamedMutex, kernel32, user32


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
