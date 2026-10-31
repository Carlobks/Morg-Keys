"""Relatório de erros do Morg Keys (P3): o texto que quem usa guarda e junta a uma issue no GitHub.

O que leva vem da pesquisa (docs/pesquisa/relatorio-de-erros.md):
- o resumo (subcomando e tipo da exceção);
- quando e onde: a hora em ISO 8601 com o fuso, a versão instalada, o Windows e o Python;
- o que estava a fazer: o subcomando do bar_helper.py (os dados do painel em base64 ficam de fora);
- a exceção como o OpenTelemetry: tipo, mensagem, gravidade e stack trace;
- as últimas linhas do registo do arranque;
- os campos que quem envia preenche (passos, o que esperava, o que aconteceu, como no guia da Mozilla).
A limpeza (RFC 9457, RGPD) troca a pasta pessoal por ~ e os nomes da pessoa por <utilizador>. Aqui só se monta o
texto; o popup e o guardar são a cola com o Windows.
"""

import ctypes
import faulthandler
import json
import os
import platform
import re
import sys
import traceback
from ctypes import wintypes
from datetime import datetime
from pathlib import Path

from morg_win32 import user32

comdlg32 = ctypes.WinDLL("comdlg32")
MB_YESNO, MB_ICONERROR, MB_TOPMOST, IDYES = 0x4, 0x10, 0x40000, 6
OFN_OVERWRITEPROMPT, OFN_NOCHANGEDIR, OFN_PATHMUSTEXIST = 0x2, 0x8, 0x800

INSTALACAO = Path.home() / ".glzr" / "instalacao.json"
REGISTO_DO_ARRANQUE = Path(__file__).resolve().parent / ".layout-restore.log"
LINHAS_DO_REGISTO = 20
ARRANQUE = Path(__file__).resolve().parent / "guia" / "arranque.txt"
PASTA_DOS_ERROS = Path.home() / ".glzr" / "erros"
MAXIMO_DE_COPIAS = 10
ESCONDER = {"esconder", "ocultar", "nao", "não", "off"}  # as mesmas palavras do "claude =" (claude_usage.py)
_BASE64 = re.compile(r"[A-Za-z0-9_-]{16,}={0,2}")
# As secções da pesquisa, por ordem (o modelo fica fora da função para ela caber nas 35 linhas).
MODELO = """# Relatório de erro do Morg Keys

**Resumo:** `{resumo}`

## Quando e onde

- Hora: {hora}
- Morg Keys: {versao}
- Windows: {windows}
- Python: {python}

## O que estava a fazer

`bar_helper.py {comando}`

## A exceção

- Tipo: `{tipo}`
- Mensagem: {mensagem}
- Gravidade: ERROR

```
{pilha}
```

## Registo do arranque (últimas linhas)

```
{registo}
```

## Para preencher por quem envia

- Passos para reproduzir:
- O que esperava:
- O que aconteceu:
"""


def limpar(texto, casa, nomes):
    """Troca a pasta pessoal (as duas barras, sem olhar a maiúsculas) por ~ e cada nome por <utilizador>.

    Conta também a forma com as barras a dobrar: é a que a mensagem de um OSError mostra (repr do caminho).
    """
    for variante in (casa.replace("\\", "\\\\"), casa, casa.replace("\\", "/")):
        texto = re.sub(re.escape(variante), "~", texto, flags=re.IGNORECASE)
    for nome in sorted((n for n in nomes if n), key=len, reverse=True):  # "Ana Silva" antes de "Ana"
        texto = re.sub(rf"\b{re.escape(nome)}\b", "<utilizador>", texto, flags=re.IGNORECASE)
    return texto


def argumentos_visiveis(argumentos):
    """Os argumentos do bar_helper.py, com os dados do painel (base64) trocados por um marcador."""
    return ["<dados do painel>" if _BASE64.fullmatch(a) else a for a in argumentos]


def versao_instalada(ficheiro=INSTALACAO):
    """A versão do Morg Keys que o instalador gravou (e quando); "desconhecida" se não houver."""
    try:
        estado = json.loads(ficheiro.read_text(encoding="utf-8-sig"))
    except (OSError, ValueError):
        return "desconhecida"
    versao = estado.get("versao") or "desconhecida"
    return f"{versao}, instalado em {estado['instalado_em']}" if estado.get("instalado_em") else versao


def ultimas_linhas(ficheiro, quantas=LINHAS_DO_REGISTO):
    """As últimas linhas de um registo; texto vazio se não existir."""
    try:
        return "\n".join(ficheiro.read_text(encoding="utf-8", errors="replace").splitlines()[-quantas:])
    except OSError:
        return ""


def valor_do_arranque(chave, arranque):
    """O valor de "chave = valor" no arranque.txt (a primeira linha que não seja comentário); None se não houver."""
    try:
        linhas = arranque.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, ValueError):
        return None
    for linha in linhas:
        nome, igual, valor = linha.partition("=")
        if igual and nome.strip().lower() == chave:
            return valor.strip()
    return None


def popup_ligado(arranque=ARRANQUE):
    """O popup do erro está ligado por omissão; "erros = esconder" no arranque.txt desliga-o."""
    valor = valor_do_arranque("erros", arranque)
    return valor is None or valor.lower() not in ESCONDER


def alternar_aviso(arranque=None):
    """Alt+Esc, V: liga ou desliga o popup do erro no arranque.txt, mantendo o resto do ficheiro (como o
    _set_animacao). Devolve o estado novo: "ligado" ou "desligado"."""
    arranque = arranque or ARRANQUE
    ligar = not popup_ligado(arranque)
    try:
        linhas = arranque.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, ValueError):
        linhas = []
    nova = f"erros = {'mostrar' if ligar else 'esconder'}"
    for i, linha in enumerate(linhas):
        nome, igual, _ = linha.partition("=")
        if igual and nome.strip().lower() == "erros":
            linhas[i] = nova
            break
    else:
        linhas.append(nova)
    temporario = arranque.with_suffix(".tmp")
    temporario.write_text("\n".join(linhas) + "\n", encoding="utf-8")
    os.replace(temporario, arranque)
    return "ligado" if ligar else "desligado"


def nomes_da_pessoa():
    """Os nomes que a limpeza tira: a conta do Windows e o "nome =" da saudação do arranque.txt."""
    return [n for n in (os.environ.get("USERNAME", ""), valor_do_arranque("nome", ARRANQUE) or "") if n]


def guardar_copia(texto, agora, pasta=PASTA_DOS_ERROS, maximo=MAXIMO_DE_COPIAS):
    """Guarda sempre uma cópia do relatório (também com o popup desligado) e deixa só as `maximo` mais recentes."""
    pasta.mkdir(parents=True, exist_ok=True)
    destino = pasta / f"erro-{agora:%Y%m%d-%H%M%S}.md"
    destino.write_text(texto, encoding="utf-8")
    for antiga in sorted(pasta.glob("erro-*.md"))[:-maximo]:
        antiga.unlink(missing_ok=True)
    return destino


def montar_relatorio(erro, argv, agora, *, versao, registo, casa, nomes):
    """O relatório em Markdown, já limpo. `argv` é o sys.argv do bar_helper.py."""
    argumentos = argumentos_visiveis(argv[1:])
    texto = MODELO.format(
        resumo=f"{' '.join(argumentos[:2]) or '(sem subcomando)'}: {type(erro).__name__}",
        hora=agora.isoformat(timespec="seconds"), versao=versao, windows=platform.platform(),
        python=platform.python_version(), comando=" ".join(argumentos), tipo=type(erro).__name__, mensagem=erro,
        pilha="".join(traceback.format_exception(erro)).rstrip(), registo=registo or "(vazio)")
    return limpar(texto, casa, nomes)


def tratar_erro(erro, argv, agora=None, *, perguntar=None, escolher=None):
    """Um erro que chegou ao topo do bar_helper.py: guarda sempre a cópia e, com o popup ligado, pergunta se
    quem usa quer guardar o relatório onde escolher. Devolve o caminho da cópia."""
    agora = agora or datetime.now().astimezone()
    texto = montar_relatorio(erro, argv, agora, versao=versao_instalada(INSTALACAO),
                             registo=ultimas_linhas(REGISTO_DO_ARRANQUE), casa=str(Path.home()),
                             nomes=nomes_da_pessoa())
    copia = guardar_copia(texto, agora, PASTA_DOS_ERROS)
    resumo = re.search(r"\*\*Resumo:\*\* `(.*)`", texto).group(1)
    if popup_ligado(ARRANQUE) and (perguntar or perguntar_se_guarda)(resumo):
        destino = (escolher or pedir_destino)(copia.name, Path.home() / "Documents")
        if destino:
            destino.write_text(texto, encoding="utf-8")
    return copia


# --- Cola com o Windows (testada com o Windows simulado; passo manual em docs/validacao-manual.md) ----------------
class _OPENFILENAMEW(ctypes.Structure):
    _fields_ = [("lStructSize", wintypes.DWORD), ("hwndOwner", wintypes.HWND), ("hInstance", wintypes.HINSTANCE),
                ("lpstrFilter", wintypes.LPCWSTR), ("lpstrCustomFilter", wintypes.LPWSTR),
                ("nMaxCustFilter", wintypes.DWORD), ("nFilterIndex", wintypes.DWORD), ("lpstrFile", wintypes.LPWSTR),
                ("nMaxFile", wintypes.DWORD), ("lpstrFileTitle", wintypes.LPWSTR), ("nMaxFileTitle", wintypes.DWORD),
                ("lpstrInitialDir", wintypes.LPCWSTR), ("lpstrTitle", wintypes.LPCWSTR), ("Flags", wintypes.DWORD),
                ("nFileOffset", wintypes.WORD), ("nFileExtension", wintypes.WORD), ("lpstrDefExt", wintypes.LPCWSTR),
                ("lCustData", wintypes.LPARAM), ("lpfnHook", ctypes.c_void_p), ("lpTemplateName", wintypes.LPCWSTR),
                ("pvReserved", ctypes.c_void_p), ("dwReserved", wintypes.DWORD), ("FlagsEx", wintypes.DWORD)]


def perguntar_se_guarda(resumo):
    """Popup nativo (aparece mesmo com o Zebar em baixo): True se quem usa quer guardar o relatório."""
    texto = (f"O Morg Keys encontrou um erro:\n\n{resumo}\n\nGuardar o relatório para o juntar a uma issue no GitHub?"
             "\n\nFica também uma cópia em .glzr\\erros, na pasta pessoal.")
    return user32.MessageBoxW(None, texto, "Morg Keys: erro", MB_YESNO | MB_ICONERROR | MB_TOPMOST) == IDYES


def pedir_destino(nome_sugerido, pasta_inicial):
    """A janela "Guardar como" do Windows: o caminho escolhido, ou None se quem usa cancelar."""
    ficheiro = ctypes.create_unicode_buffer(nome_sugerido, 1024)
    filtro = ctypes.create_unicode_buffer("Markdown (*.md)\0*.md\0Todos os ficheiros\0*.*\0\0", 64)  # com os \0
    pedido = _OPENFILENAMEW(lStructSize=ctypes.sizeof(_OPENFILENAMEW), nMaxFile=1024, lpstrDefExt="md",
                            lpstrInitialDir=str(pasta_inicial), lpstrTitle="Guardar o relatório de erro",
                            Flags=OFN_OVERWRITEPROMPT | OFN_NOCHANGEDIR | OFN_PATHMUSTEXIST)
    pedido.lpstrFile = ctypes.cast(ficheiro, wintypes.LPWSTR)
    pedido.lpstrFilter = ctypes.cast(filtro, wintypes.LPCWSTR)
    return Path(ficheiro.value) if comdlg32.GetSaveFileNameW(ctypes.byref(pedido)) else None


def instalar(argv, tratar=tratar_erro):
    """Chamado pelo bar_helper.py: os erros que chegam ao topo viram relatório (sys.excepthook, sem apanhar tudo
    num except) e os rebentamentos em C, como no ctypes, ficam em rebentamentos.log (faulthandler)."""
    PASTA_DOS_ERROS.mkdir(parents=True, exist_ok=True)
    faulthandler.enable(file=os.open(PASTA_DOS_ERROS / "rebentamentos.log", os.O_WRONLY | os.O_APPEND | os.O_CREAT))

    def gancho(tipo, erro, pilha):
        if not issubclass(tipo, KeyboardInterrupt):
            try:
                tratar(erro, argv)
            except (OSError, ValueError, AttributeError):  # o relatório nunca esconde o erro original
                pass
        sys.__excepthook__(tipo, erro, pilha)

    sys.excepthook = gancho


def erro_de_teste():
    """bar_helper.py erro-de-teste: provoca um erro de propósito, para ver o popup e o relatório."""
    raise RuntimeError("erro de teste pedido por quem usa (bar_helper.py erro-de-teste)")
