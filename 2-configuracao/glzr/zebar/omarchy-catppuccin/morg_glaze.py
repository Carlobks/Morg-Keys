"""GlazeWM: a CLI (`glazewm query/command`), a árvore de workspaces e restaurar minimizadas."""

import json
import subprocess

from morg_processos import CREATE_NO_WINDOW, GLAZE_CLI


# --- GlazeWM: minimizadas e arranjo dos workspaces --------------------------------
def _glaze(*args):
    """Chama a CLI do GlazeWM e devolve o JSON; {} se não estiver a correr."""
    try:
        out = subprocess.run([str(GLAZE_CLI), *args], capture_output=True, text=True,
                             encoding="utf-8", errors="replace", timeout=10,
                             creationflags=CREATE_NO_WINDOW, check=False)
        return json.loads(out.stdout or "{}")
    except (OSError, ValueError, subprocess.TimeoutExpired):
        return {}


def _workspaces():
    reply = _glaze("query", "workspaces")
    return reply.get("data", {}).get("workspaces", []) if reply.get("success") else None



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
