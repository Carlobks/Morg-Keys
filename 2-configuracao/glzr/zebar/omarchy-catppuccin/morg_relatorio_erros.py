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

import json
import platform
import re
import traceback
from pathlib import Path

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


def popup_ligado(arranque=ARRANQUE):
    """O popup do erro está ligado por omissão; "erros = esconder" no arranque.txt desliga-o."""
    try:
        linhas = arranque.read_text(encoding="utf-8-sig").splitlines()
    except (OSError, ValueError):
        return True
    for linha in linhas:
        chave, igual, valor = linha.partition("=")
        if igual and chave.strip().lower() == "erros":
            return valor.strip().lower() not in ESCONDER
    return True


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
