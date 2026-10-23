"""Atalhos das apps: apps.txt (Documentos\\Guia de Atalhos) convertido em atalhos do config.yaml."""

import json
import os
import subprocess
import time
from pathlib import Path

from morg_glaze import _glaze
from morg_processos import CREATE_NO_WINDOW, HERE
from morg_win32 import user32

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


START_CACHE = HERE / ".start-apps.json"  # última lista do menu Iniciar (o painel lê-a; apps-apply usa-a se pedido)


def _start_items(use_cache=False):
    """[{"Name", "AppID"}] do menu Iniciar via Get-StartApps (lento: ~1-2 s).
    use_cache: aceita a lista guardada há menos de 6 h. A lista nova fica sempre em cache."""
    if use_cache:
        try:
            cached = json.loads(START_CACHE.read_text(encoding="utf-8"))
            if time.time() - cached.get("saved_at", 0) < 6 * 3600 and cached.get("items"):
                return cached["items"]
        except (OSError, ValueError):
            pass
    out = subprocess.run(
        ["powershell", "-NoProfile", "-Command",
         "[Console]::OutputEncoding=[Text.Encoding]::UTF8; Get-StartApps | ConvertTo-Json -Compress"],
        capture_output=True, text=True, encoding="utf-8", errors="replace",
        timeout=30, creationflags=CREATE_NO_WINDOW)
    try:
        items = json.loads(out.stdout or "[]")
    except ValueError:
        return []
    items = [items] if isinstance(items, dict) else items
    items = [{"Name": i["Name"].strip(), "AppID": i["AppID"]} for i in items if i.get("Name") and i.get("AppID")]
    try:
        tmp = START_CACHE.with_suffix(".tmp")
        tmp.write_text(json.dumps({"saved_at": int(time.time()), "items": items}), encoding="utf-8")
        os.replace(tmp, START_CACHE)
    except OSError:
        pass
    return items


def _start_apps(use_cache=False):
    """{nome no menu Iniciar (minúsculas): AppID}."""
    return {i["Name"].lower(): i["AppID"] for i in _start_items(use_cache)}


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
    errors = _apps_apply_core(skip_missing)
    if errors:
        user32.MessageBoxW(None, "Os atalhos das apps NÃO foram alterados:\n\n" + "\n".join(errors),
                           "Atalhos das apps (apps.txt)", 0x30 | 0x40000 | 0x10000)
        _glaze("command", "wm-reload-config")
        return
    user32.MessageBeep(0)


def _apps_apply_core(skip_missing=False, use_cache=False):
    """Valida apps.txt e, se estiver tudo bem, escreve o bloco das apps no
    config.yaml e recarrega o GlazeWM. Devolve a lista de erros ([] = aplicado;
    com erros não muda nada). use_cache: lista do menu Iniciar em cache (painel)."""
    try:
        lines = APPS_FILE.read_text(encoding="utf-8-sig").splitlines()
        config = GLAZE_CONFIG.read_text(encoding="utf-8")
    except OSError as err:
        return [f"Não consegui ler os ficheiros: {err}"]

    errors, entries, skipped = _apps_validar(lines, config, skip_missing, use_cache)
    if skipped:
        APPS_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")
    if errors:
        return errors
    _apps_escrever_bloco(config, entries)
    _glaze("command", "wm-reload-config")
    return []


def _apps_validar(lines, config, skip_missing, use_cache):
    """Lê as linhas do apps.txt: (erros, [(tecla, app, comando)], houve linhas comentadas).
    Com skip_missing, comenta em `lines` as apps que não existem neste PC."""
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
            start_apps = _start_apps(use_cache)
        command = _resolve_app(right, start_apps or {})
        if not command and use_cache and start_apps is not None:
            start_apps = _start_apps()  # app instalada depois da cache: lista nova
            use_cache = False
            command = _resolve_app(right, start_apps)
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
    return errors, entries, skipped


def _apps_escrever_bloco(config, entries):
    """Escreve o bloco gerado (entre APPS_BEGIN e APPS_END) no config.yaml, se mudar."""
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


def apps_edit():
    """Abre apps.txt no editor de texto predefinido."""
    os.startfile(str(APPS_FILE))



def _key_text(key):
    """"alt+shift+b" -> "Alt+Shift+B" (a forma escrita no apps.txt)."""
    return "+".join({"alt": "Alt", "shift": "Shift", "enter": "Enter", "space": "Space"}.get(p, p.upper())
                    for p in key.split("+"))


def _apps_entries(lines):
    """[(índice da linha, tecla normalizada, app)] das linhas válidas do apps.txt."""
    out = []
    for i, raw in enumerate(lines):
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        left, right = line.split("=", 1)
        key = _parse_key(left)
        if key:
            out.append((i, key, right.strip()))
    return out
