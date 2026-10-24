"""Bateria de estragos (testes de mutação feitos à mão): prova que os testes falham quando o código está errado.

Cada estrago troca um texto num .py ou .mjs do pack, corre os testes (unittest ou node --test) e repõe
o ficheiro (também se rebentar). Procura o texto em todos esses ficheiros (o código pode ter mudado de
ficheiro numa refatoração).
Antes de estragar, confirma que os testes passam com o código certo (senão todos dariam "apanhado").
Estrago novo: acrescentar (texto certo, texto estragado) a MUTANTES, depois de cada bug ou função nova.

Uso: py -I scripts\\estragos.py   (de qualquer pasta; ~10 min)
"""

import os
import pathlib
import subprocess

RAIZ = pathlib.Path(__file__).resolve().parent.parent
os.chdir(RAIZ)
PACK = pathlib.Path("2-configuracao/glzr/zebar/omarchy-catppuccin")
MUTANTES = [
    ('if not parts or parts[0] != "alt":', 'if not parts or parts[0] not in ("alt", "shift"):'),
    ('app_id = found[0] if len(found) == 1 else None', 'app_id = found[0] if len(found) >= 1 else None'),
    ('    if APPS_BEGIN in text and APPS_END in text:\n        text = text.split', '    if False:\n        text = text.split'),
    ('    if key in fixed:', '    if False and key in fixed:'),
    ('format(command.replace("\'", "\'\'"))', 'format(command)'),
    ('if "expect_ws" in op and (', 'if False and ('),
    ('if kind == "ws-move" and windows[i].get("workspace") == str(op.get("ws", "")):', 'if False:'),
    ('if last.get("after") and last["after"] != _files_hash():', 'if False:'),
    ('json.dumps(stack[-PANEL_UNDO_MAX:])', 'json.dumps(stack)'),
    (' and _norm(w["processName"]) not in others]', ']'),
    ('late = time.monotonic() - start > wait * 2 / 3', 'late = True'),
    ('if p in running and p not in have_windows and not entry["launch"].get("args"):', 'if False:'),
    ('or _norm(process) in running or', 'or'),
    ('same = [e for e in prev if e.get("title_hash") == w["title_hash"]]', 'same = []'),
    ('            prev.remove(e)\n', '            pass\n'),
    ('wait = max(wait_s, 40 if r.launched else 0)', 'wait = wait_s'),
    ('            count[_norm(e["process"])] -= 1', '            pass'),
    ('drop |= {i for i, k, _ in entries if k == src}', 'pass'),
    ('        _panel_pop_undo()\n        # "linha 12', '        # "linha 12'),
    ('    start = time.monotonic()\n    wait = ', '    start = 0\n    wait = '),
    ('and reset and reset > now:', 'and reset:'),
    ('return int(value / 1000) if value > 1e12 else int(value)', 'return int(value)'),
    ('sys.path.insert(0, str(Path(__file__).resolve().parent))', 'pass'),
    # boot e arranque.txt (fase 2b)
    ('_popen_detached([str(ZEBAR), "startup"])', 'pass'),
    ('        a.cover.close()\n        a.log(f"animação visível', '        a.log(f"animação visível'),
    ('        if not Path(bat["path"]).exists():', '        if False:'),
    ('>= BOOT_QUIET_S and not waiting_ports:', '>= BOOT_QUIET_S:'),
    ('    kernel32.ReleaseMutex(boot_mutex)', '    pass'),
    ('    a.progress.finish()\n    a.log(f"tudo assente', '    a.log(f"tudo assente'),
    ('            left[entry["_k"]] -= 1', '            pass'),
    ('        user32.PostMessageW(hwnd, 0x0010, 0, 0)  # WM_CLOSE\n        a.log("splash', '        a.log("splash'),
    ('name = value.lower().replace("é", "e")', 'name = value.lower()'),
    # tabela de comandos do main (fase 2b)
    ('    ("guide",): guide,', '    ("guide",): guide_hide,'),
    ('    ("panel",): panel_show,', '    ("panel",): panel_hide,'),
    ('cmd[1] if len(cmd) == 2 and cmd[1] != "next" else None', 'cmd[1] if len(cmd) == 2 else None'),
    # Alt+Esc, E (animacao_tap)
    ('if now - last >= ANIM_REPEAT_MS:', 'if True:'),
    ('if state == "hold":', 'if False:'),
    ('prev = before if before in ANIMACOES else prev', 'prev = prev'),
    ('if kernel32.GetTickCount64() - last > 250:', 'if True:'),
    ('f"{now} {current} tap {prev}"', 'f"{now} {current} tap -"'),
    # painel e guia em .mjs (fase 2c): apanhados pelo node --test
    ("hostname.replace(/^www\\./, '')", 'hostname'),
    ("/[&<>\"']/g", "/[<>\"']/g"),
    ('const fixed = state.fixed.includes(id);', 'const fixed = false;'),
    ('.filter(k => !drawn.has(k.key))', '.filter(() => false)'),
    (".replace(/\\//g, '_').replace(/=+$/, '');", ".replace(/\\//g, '_');"),
    ('.map((w, i) => ({ ...w, index: i }))', ''),
    (".replace(/\\+\\+/g, '+\\u0000')", ''),
    ("l && !l.startsWith('#') && l.includes('=')", "l && l.includes('=')"),
    ('rows: [...appRows, ...s.rows]', 'rows: [...s.rows, ...appRows]'),
]
FICHEIROS = [*PACK.glob("*.py"), *PACK.glob("comum/*.mjs"), *PACK.glob("painel/*.mjs"), *PACK.glob("guia/*.mjs")]
TESTES_PY = ["py", "-I", "-m", "unittest", "discover", "-s", "tests"]
TESTES_JS = ["node", "--test", *map(str, pathlib.Path("tests").glob("*.test.mjs"))]


def onde_esta(texto):
    achados = [p for p in FICHEIROS if p.read_text(encoding="utf-8").count(texto) == 1]
    return achados[0] if len(achados) == 1 else None


for testes in (TESTES_PY, TESTES_JS):
    base = subprocess.run(testes, capture_output=True, timeout=180)
    if base.returncode != 0:  # com testes já vermelhos, todos os estragos seriam "apanhados" (falso 100 %)
        raise SystemExit("Os testes falham com o código certo: corrija antes de correr os estragos.")

apanhados = 0
for antes, depois in MUTANTES:
    ficheiro = onde_esta(antes)
    if not ficheiro:
        print(f"NÃO ENCONTRADO (ou repetido): {antes[:60]!r}")
        continue
    original = ficheiro.read_bytes()
    ficheiro.write_bytes(original.decode("utf-8").replace(antes, depois).encode("utf-8"))
    try:
        r = subprocess.run(TESTES_JS if ficheiro.suffix == ".mjs" else TESTES_PY, capture_output=True, timeout=180)
        apanhado = r.returncode != 0
    except subprocess.TimeoutExpired:
        apanhado = True
    finally:
        ficheiro.write_bytes(original)
    apanhados += apanhado
    print(f"{'APANHADO' if apanhado else 'ESCAPOU '} {ficheiro.name}: {antes[:60]!r}")
print(f"\n{apanhados}/{len(MUTANTES)} apanhados")
