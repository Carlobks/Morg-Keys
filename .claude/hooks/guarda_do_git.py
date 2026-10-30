"""Hook PreToolUse (Bash/PowerShell): o agente não salta nem desliga os portões do git (Morg Laws).

Os testes, a identidade, a lista negra e a mensagem verificam-se nos hooks do git (.githooks/, ligados por
`core.hooksPath`), que valem também para os commits feitos à mão. Esta guarda recusa, a partir do agente:
- `--no-verify` (ou `-n` num commit), que salta os hooks do git;
- mudar ou desligar o `core.hooksPath` (só se pode pô-lo em `.githooks`);
- um commit com o `core.hooksPath` que não é `.githooks` (os portões não correriam);
- preparar tudo de uma vez (`git add -A` / `.` / `--all`, `git commit -a`, commit do caminho `.`): o commit é por
  caminho, para não levar o trabalho de outra sessão;
- `git commit -m` com várias linhas ou com heredoc: no Windows estraga os acentos; usar `-F <ficheiro>`.
Reconhece os comandos pelo texto (limites na A32). Sai com 2 e o motivo no stderr; sai com 0 nos outros casos.
Substitui o testes_antes_do_commit.py: os testes passaram para o .githooks/pre-commit (guarda A30 lá).
"""

import json
import re
import shlex
import subprocess
import sys
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
CAMINHO_DOS_HOOKS = ".githooks"
_SEPARADORES = {";", "&", "&&", "|", "||", "\n", "(", ")"}
_CURTAS_COM_VALOR = "mFCct"  # opções de uma letra do git commit que levam valor
_LONGAS_COM_VALOR = {"--file", "--author", "--date", "--template", "--fixup", "--squash", "--reuse-message",
                     "--reedit-message", "--cleanup", "--trailer", "--pathspec-from-file"}
_TUDO = {".", "./", ":/", "*", "-A", "--all"}


def palavras(comando):
    """Divide o comando em palavras e separadores (; && | e quebras de linha), respeitando as aspas."""
    try:
        divisor = shlex.shlex(comando, posix=True, punctuation_chars=";&|()\n")
        divisor.whitespace = " \t\r"
        divisor.whitespace_split = True
        return list(divisor)
    except ValueError:  # aspas por fechar (ex.: texto do PowerShell): divisão simples
        return re.findall(r"[;&|()\n]+|[^\s;&|()]+", comando)


def comandos_git(lista):
    """Cada `git …` da lista de palavras: (opções antes do subcomando, subcomando, argumentos)."""
    resultado, i = [], 0
    while i < len(lista):
        if Path(lista[i]).name.lower() not in ("git", "git.exe"):
            i += 1
            continue
        i, globais = i + 1, []
        while i < len(lista) and lista[i].startswith("-"):
            leva_valor = lista[i] in ("-C", "-c")
            globais.extend(lista[i:i + 1 + leva_valor])
            i += 1 + leva_valor
        fim = i
        while fim < len(lista) and lista[fim] not in _SEPARADORES:
            fim += 1
        subcomando = lista[i] if i < fim else ""
        resultado.append((globais, subcomando, lista[i + 1:fim]))
        i = fim
    return resultado


def opcoes(args):
    """(letras das opções curtas, opções longas, textos das mensagens -m, caminhos) de um git commit/add."""
    curtas, longas, mensagens, caminhos, i = set(), set(), [], [], 0
    while i < len(args):
        arg = args[i]
        if arg == "--":
            caminhos.extend(args[i + 1:])
            break
        if arg.startswith("--"):
            nome, igual, valor = arg.partition("=")
            longas.add(nome)
            if nome in _LONGAS_COM_VALOR | {"--message"} and not igual:
                valor, i = (args[i + 1] if i + 1 < len(args) else ""), i + 1
            if nome == "--message":
                mensagens.append(valor)
        elif arg.startswith("-") and len(arg) > 1:
            for posicao, letra in enumerate(arg[1:], 2):
                curtas.add(letra)
                if letra in _CURTAS_COM_VALOR:
                    valor = arg[posicao:] or (args[i + 1] if i + 1 < len(args) else "")
                    i += not arg[posicao:]
                    mensagens.extend([valor] if letra == "m" else [])
                    break
        else:
            caminhos.append(arg)
        i += 1
    return curtas, longas, mensagens, caminhos


def motivo_do_commit(args, ler_hooks):
    """Motivo para recusar um `git commit …` (None se puder seguir)."""
    curtas, longas, mensagens, caminhos = opcoes(args)
    if "n" in curtas or "--no-verify" in longas:
        return "--no-verify salta os portões do git."
    if "a" in curtas or "--all" in longas or _TUDO & set(caminhos):
        return "o commit é por caminho (git commit -F msg -- <ficheiros>), nunca de tudo (-a, --all, .)."
    if any("\n" in texto or "<<" in texto for texto in mensagens):
        return "mensagem com várias linhas em -m: escreva-a num ficheiro e use git commit -F <ficheiro>."
    hooks = ler_hooks()
    if hooks != CAMINHO_DOS_HOOKS:
        return (f"o core.hooksPath é '{hooks}', não é {CAMINHO_DOS_HOOKS}: os portões não correriam. "
                f"Corra: git config core.hooksPath {CAMINHO_DOS_HOOKS}")
    return None


def motivo_do_hooks_path(globais, subcomando, args):
    """Motivo para recusar uma mudança ao core.hooksPath (pô-lo em .githooks ou lê-lo pode)."""
    if any(valor.lower().startswith("core.hookspath") for valor in globais):
        return "git -c core.hooksPath=… troca os portões do git."
    chaves = [i for i, arg in enumerate(args) if arg.lower() == "core.hookspath"]
    if subcomando != "config" or not chaves:
        return None
    resto = args[chaves[0] + 1:]
    if any(arg.startswith("--unset") for arg in args) or (resto and resto != [CAMINHO_DOS_HOOKS]):
        return f"o core.hooksPath só pode ser {CAMINHO_DOS_HOOKS} (ligar os portões do git)."
    return None


def motivo_para_bloquear(comando, ler_hooks):
    """Devolve o motivo (texto) se o comando saltar ou estragar os portões do git; None se for seguro."""
    for globais, subcomando, args in comandos_git(palavras(comando)):
        motivo = motivo_do_hooks_path(globais, subcomando, args)
        if not motivo and subcomando == "add" and (_TUDO & set(args) or any(re.fullmatch(r"-\w*A\w*", a) for a in args)):
            motivo = "prepare por caminho (git add -- <ficheiros>), nunca tudo (-A, --all, ., :/)."
        if not motivo and subcomando == "commit":
            motivo = motivo_do_commit(args, ler_hooks)
        if not motivo and subcomando in ("push", "merge", "rebase", "am", "cherry-pick") and "--no-verify" in args:
            motivo = "--no-verify salta os portões do git."
        if motivo:
            return motivo
    return None


def ler_hooks_path(correr=None):
    """Valor de core.hooksPath deste repositório (texto vazio se não houver)."""
    return (correr or subprocess.run)(["git", "-C", str(RAIZ), "config", "--get", "core.hooksPath"],
                                      capture_output=True, text=True, encoding="utf-8", check=False).stdout.strip()


def main():
    # Bytes em UTF-8: no Windows o stdin de texto usaria a página de código local e estragaria os acentos.
    pedido = json.loads(sys.stdin.buffer.read().decode("utf-8"))
    comando = (pedido.get("tool_input") or {}).get("command") or ""
    motivo = motivo_para_bloquear(comando, ler_hooks_path)
    if motivo:
        sys.stderr.reconfigure(encoding="utf-8")
        sys.stderr.write(f"Bloqueado (portões do git, Morg Laws): {motivo}\n")
        sys.exit(2)


if __name__ == "__main__":
    main()
