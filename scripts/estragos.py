"""Bateria de estragos (testes de mutação feitos à mão): prova que os testes falham quando o código está errado.

Cada estrago troca um texto num .py ou .mjs do pack, corre os testes (unittest ou node --test) e repõe
o ficheiro (também se rebentar). Procura o texto em todos esses ficheiros (o código pode ter mudado de
ficheiro numa refatoração).
Antes de estragar, confirma que os testes passam com o código certo (senão todos dariam "apanhado").
Estrago novo: acrescentar (texto certo, texto estragado) a MUTANTES, depois de cada bug ou função nova.
Corre numa cópia (um `git worktree` do último commit numa pasta temporária), nunca no disco partilhado: outra
sessão a testar ou a commitar veria os mutantes (ML16, M4). O que não está commitado não entra.

Uso: py -I scripts\\estragos.py   (de qualquer pasta; ~10 min)
"""

import contextlib
import os
import pathlib
import shutil
import subprocess
import tempfile

RAIZ = pathlib.Path(__file__).resolve().parent.parent
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
    # P2: a app do painel não aprende a janela de um processo que já corria (o Claude do arranque do Windows)
    ('others | ja_corriam, poll)', 'others, poll)'),
    ('ja_corriam = {_norm(p) for p in _running_images()}', 'ja_corriam = set()'),
    # P3: relatório de erros (limpeza, popup desligável, cópias, gancho)
    ('for variante in (casa.replace("\\\\", "\\\\\\\\"), casa,', 'for variante in (casa,'),
    ('for nome in sorted((n for n in nomes if n), key=len, reverse=True):', 'for nome in []:'),
    ('return ["<dados do painel>" if _BASE64.fullmatch(a) else a for a in argumentos]', 'return list(argumentos)'),
    ('return valor is None or valor.lower() not in ESCONDER', 'return True'),
    ('for antiga in sorted(pasta.glob("erro-*.md"))[:-maximo]:', 'for antiga in []:'),
    ('if not issubclass(tipo, KeyboardInterrupt):', 'if True:'),
    # o hInstance da cortina inteiro (64 bits) e o rebentamentos.log com limite
    (('cortina ficava cortado a 32 bits e o Windows dava "access violation" (tests/test_win32_tipos.py).\n'
      'kernel32.GetModuleHandleW.restype = wintypes.HMODULE\n'),
     'cortina ficava cortado a 32 bits e o Windows dava "access violation" (tests/test_win32_tipos.py).\n'),
    ('registo.stat().st_size > LIMITE_DOS_REBENTAMENTOS', 'registo.stat().st_size < 0'),
    # P3b: Alt+Esc, V liga e desliga o aviso
    ('ligar = not popup_ligado(arranque)', 'ligar = popup_ligado(arranque)'),
    ("return line && ESCONDER.has(line.split('=')[1].trim().toLowerCase()) ? 'desligado' : 'ligado';",
     "return line ? 'desligado' : 'ligado';"),
    ('late = time.monotonic() - start > wait * 2 / 3', 'late = True'),
    ('if p in running and p not in have_windows and not entry["launch"].get("args"):', 'if False:'),
    ('or _norm(process) in running or', 'or'),
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
    # o esc do partilhado/paineis.mjs (o bar-logica.mjs tem outro, que aceita null: daí o contexto)
    ("String(s).replace(/[&<>\"']/g", "String(s).replace(/[<>\"']/g"),
    ('const fixed = state.fixed.includes(id);', 'const fixed = false;'),
    ('.filter(k => !drawn.has(k.key))', '.filter(() => false)'),
    (".replace(/\\//g, '_').replace(/=+$/, '');", ".replace(/\\//g, '_');"),
    ('.map((w, i) => ({ ...w, index: i }))', ''),
    (".replace(/\\+\\+/g, '+\\u0000')", ''),
    ("l && !l.startsWith('#') && l.includes('=')", "l && l.includes('=')"),
    ('rows: [...appRows, ...s.rows]', 'rows: [...s.rows, ...appRows]'),
    # cobertura a 100 % (experiência 0001, fase 3): lógica tirada da página do painel e cola do Windows
    ('if (state.fixed.includes(key)) return', 'if (false) return'),
    ("key === '0' ? '10' : key", 'key'),
    ('url = `https://${url}`', 'url = `${url}`'),
    ('const s = escala || 1;', 'const s = 1;'),
    ('a.key === b.key && a.index === b.index', 'a.key === b.key'),
    ("items.length === 1 ? 'app' : 'apps'", "'apps'"),
    ('if pid.isdigit() and int(pid) > 4:', 'if pid.isdigit():'),
    ('return 0 <= now - last < delay_ms + 200', 'return 0 <= now - last < delay_ms'),
    # melhorias antes da fase 4: Claude Code do npm e ajuda numa consola cp1252
    ('candidatos.append(Path(os.environ["APPDATA"]) / "npm" / "claude.cmd")', 'pass'),
    ('if p is None or p.suffix.lower() == ".exe":', 'if p is None:'),
    ('__doc__.encode(codificacao, "replace")', '__doc__.encode(codificacao, "strict")'),
    # bateria na barra (partilhado/bateria.mjs)
    ('const passo = Math.round(pct / 10);', 'const passo = Math.floor(pct / 10);'),
    ('pct < BAIXA ? COR.baixa', 'pct < AVISO ? COR.baixa'),
    ('const cor = carregar ? COR.carregar', 'const cor = false ? COR.carregar'),
    ("const carregar = !!b.isCharging || b.state === 'charging';", 'const carregar = !!b.isCharging;'),
    # quota do Claude: esconder pelo arranque.txt e o indicador só com o ✻ sem valores
    ('return value.strip().lower() not in ESCONDER', 'return True'),
    ("if (u.mostrar === false) return", 'if (false) return'),
    ('if (!five && !week) {', 'if (!five) {'),
    # ecrã de boas-vindas: a cortina que escurece, a frase do dia e o nome da saudação
    ('return round(255 * (1 - (1 - p) ** 3))', 'return round(255 * p)'),
    ('frases[(dia - 1) % len(frases)]', 'frases[dia % len(frases)]'),
    ('elif key == "nome":', 'elif key == "nomes":'),
    # lógica das páginas tirada dos <script> em linha (ML11b): barra, arranque e painel do sistema
    ('.filter(ws => ws.name !== SCRATCH || ws.isDisplayed)', '.filter(() => true)'),
    ("v > 85 ? 'high'", "v >= 85 ? 'high'"),
    ('return vol < 34 ? ICON.volLow', 'return vol <= 34 ? ICON.volLow'),
    ('Math.min(100, Math.max(0, base + (deltaY < 0 ? 5 : -5)))', 'base + (deltaY < 0 ? 5 : -5)'),
    ('const day = t.getUTCDay() || 7;', 'const day = t.getUTCDay();'),
    ('agoraS - progresso.started > MAX_IDADE_S', 'agoraS - progresso.started >= MAX_IDADE_S'),
    ('if (visivelHaMs < MIN_ITEM_MS) return [];', 'if (false) return [];'),
    ('desdeOInicioMs > MIN_NO_ECRA_MS', 'desdeOInicioMs >= MIN_NO_ECRA_MS'),
    ("toLowerCase().replace('é', 'e')", 'toLowerCase()'),
    ("some(m => m.name === 'sistema')", "some(m => m.name === 'resize')"),
    # P3c: o nome do Windows no relatório e a versão SemVer (juntar_changelog.py e o portão versao_lancada.py)
    ('numero = 11 if build >= PRIMEIRO_BUILD_DO_WINDOWS_11 else 10', 'numero = 11 if build > PRIMEIRO_BUILD_DO_WINDOWS_11 else 10'),
    ('return f"{maior + 1}.0.0" if maior else f"0.{menor + 1}.0"', 'return f"{maior + 1}.0.0"'),
    ('if SOBE_O_MENOR.intersection(categorias):', 'if "Adicionado" in categorias:'),
    ('or numeros(versao) <= numeros(atual):', 'or numeros(versao) < numeros(atual):'),
    ('and not depois.endswith(parte_lancada(antes))', 'and False'),
    ('topo[1] != versao or f"## [{versao}]" in antes:', 'topo[1] != versao:'),
    # P7: modal dos limites do Claude (morg_limites.py, claude_usage.py, claude.mjs e limites-logica.mjs)
    ("if not m or int(m.group(1)) > 100:", "if not m:"),
    ("if minutos and not sufixo and not horas:", "if False:"),
    ("return int((alvo if alvo > base else alvo + timedelta(days=1)).timestamp())", "return int(alvo.timestamp())"),
    ("alvo += timedelta(days=(DIAS[dia] - base.weekday()) % 7)", "alvo += timedelta(days=DIAS[dia])"),
    ("if reset - agora > maximo + FOLGA_S:", "if False:"),
    ("or not reset or reset <= agora:", "or not reset:"),
    ('pct = anterior.get("pct") if pct is None else pct', "pct = pct"),
    ('dados.update({"captured_at": agora, "origem": "manual", "rate_limits": limites})',
     'dados.update({"captured_at": agora, "rate_limits": limites})'),
    ('result["origem"] = data["origem"] if isinstance(data.get("origem"), str) else None', 'result["origem"] = None'),
    ("rapido = t.setInterval(reler, RAPIDO_MS);", "rapido = null;"),
    ("e.preventDefault(); // sem o menu do WebView2", "// sem o menu do WebView2"),
    ("u.origem === 'manual' ? `Valores postos", "false ? `Valores postos"),
    ("estado.origem === 'manual' ? `Postos", "false ? `Postos"),
    ("r?.errors ? '' :", "r?.errors ? 'x' :"),
]
PASTAS_DO_PACK = ["*.py", "*.mjs", "partilhado/*.mjs", "painel/*.mjs", "guia/*.mjs", "arranque/*.mjs",
                  "limites/*.mjs"]
# Fora do pack, com testes Python. Só os ficheiros com estragos: os outros portões repetem o sys.path.insert do
# bar_helper.py, e um estrago só se aplica se o texto for único.
FERRAMENTAS = ["scripts/changelog/juntar_changelog.py", "scripts/portoes/versao_lancada.py"]
# MORG_PY: outro Python (o CI do GitHub não garante o py), o mesmo nome do testar.ps1 e dos .githooks.
TESTES_PY = [os.environ.get("MORG_PY", "py"), "-I", "-m", "unittest", "discover", "-s", "tests"]


@contextlib.contextmanager
def copia_do_repositorio(correr=subprocess.run, copiar=shutil.copytree):
    """Pasta temporária com um git worktree do último commit; removida no fim, também se rebentar (M4).

    Leva uma cópia do node_modules (o teste das páginas corre o Biome de lá). Copiado e não ligado: com uma
    junção, o "worktree remove --force" podia apagar o node_modules verdadeiro.
    """
    pasta = pathlib.Path(tempfile.mkdtemp(prefix="morg-estragos-")) / "copia"
    correr(["git", "-C", str(RAIZ), "worktree", "add", "--detach", "--quiet", str(pasta), "HEAD"], check=True)
    try:
        if (RAIZ / "node_modules").is_dir():
            copiar(RAIZ / "node_modules", pasta / "node_modules")
        yield pasta
    finally:
        correr(["git", "-C", str(RAIZ), "worktree", "remove", "--force", str(pasta)], check=False)
        shutil.rmtree(pasta.parent, ignore_errors=True)


def onde_esta(texto, ficheiros):
    achados = [p for p in ficheiros if p.read_text(encoding="utf-8").count(texto) == 1]
    return achados[0] if len(achados) == 1 else None


def estragar(antes, depois, ficheiros, testes_js):
    """Aplica um estrago, corre os testes e repõe o ficheiro; devolve True (apanhado), False ou None (não achado)."""
    ficheiro = onde_esta(antes, ficheiros)
    if not ficheiro:
        print(f"NÃO ENCONTRADO (ou repetido): {antes[:60]!r}")
        return None
    original = ficheiro.read_bytes()
    ficheiro.write_bytes(original.decode("utf-8").replace(antes, depois).encode("utf-8"))
    try:
        r = subprocess.run(testes_js if ficheiro.suffix == ".mjs" else TESTES_PY, capture_output=True, timeout=180,
                           check=False)
        apanhado = r.returncode != 0
    except subprocess.TimeoutExpired:
        apanhado = True
    finally:
        ficheiro.write_bytes(original)
    print(f"{'APANHADO' if apanhado else 'ESCAPOU '} {ficheiro.name}: {antes[:60]!r}")
    return apanhado


def correr_estragos():
    """Corre a bateria na pasta atual (a cópia); devolve 0 se todos os estragos foram apanhados."""
    ficheiros = [f for padrao in PASTAS_DO_PACK for f in PACK.glob(padrao)]
    ficheiros += [f for padrao in FERRAMENTAS for f in pathlib.Path().glob(padrao)]
    testes_js = ["node", "--test", *map(str, pathlib.Path("tests").glob("*.test.mjs"))]
    for testes in (TESTES_PY, testes_js):
        base = subprocess.run(testes, capture_output=True, timeout=180, check=False)
        if base.returncode != 0:  # com testes já vermelhos, todos os estragos seriam "apanhados" (falso 100 %)
            raise SystemExit("Os testes falham com o código certo: corrija antes de correr os estragos.")
    apanhados = sum(estragar(antes, depois, ficheiros, testes_js) is True for antes, depois in MUTANTES)
    print(f"\n{apanhados}/{len(MUTANTES)} apanhados")
    return 0 if apanhados == len(MUTANTES) else 1


def main():
    with copia_do_repositorio() as pasta:
        os.chdir(pasta)
        try:
            return correr_estragos()
        finally:
            os.chdir(RAIZ)


if __name__ == "__main__":
    raise SystemExit(main())
