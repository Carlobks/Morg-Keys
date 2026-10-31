"""Carrega e corre pelo caminho os scripts que não estão num pacote: os portões do git, os hooks do Claude
Code e a statusLine."""

import importlib.util
import io
import runpy
from pathlib import Path
from types import SimpleNamespace
from unittest import mock

RAIZ = Path(__file__).resolve().parent.parent
PASTA_PORTOES = RAIZ / "scripts" / "portoes"
PASTA_HOOKS = RAIZ / ".claude" / "hooks"
PASTA_STATUSLINE = RAIZ / "2-configuracao" / "claude"


def _carregar(caminho, nome):
    especificacao = importlib.util.spec_from_file_location(nome, caminho)
    modulo = importlib.util.module_from_spec(especificacao)
    especificacao.loader.exec_module(modulo)
    return modulo


def carregar_portao(nome):
    """Importa scripts/portoes/<nome>.py como módulo."""
    return _carregar(PASTA_PORTOES / f"{nome}.py", f"portao_{nome}")


def carregar_hook(nome):
    """Importa .claude/hooks/<nome>.py como módulo."""
    return _carregar(PASTA_HOOKS / f"{nome}.py", f"hook_{nome}")


def carregar_statusline():
    """Importa 2-configuracao/claude/statusline.py como módulo."""
    return _carregar(PASTA_STATUSLINE / "statusline.py", "statusline")


def correr_como_script(caminho, entrada):
    """Corre o script como __main__ dentro deste processo (conta na cobertura), com `entrada` (bytes) no stdin.

    Devolve (código de saída, stdout, stderr); o código é 0 se o script acabar sem sys.exit.
    """
    saida = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
    erro = io.TextIOWrapper(io.BytesIO(), encoding="utf-8")
    codigo = 0
    with mock.patch("sys.stdin", SimpleNamespace(buffer=io.BytesIO(entrada))),             mock.patch("sys.stdout", saida), mock.patch("sys.stderr", erro):
        try:
            runpy.run_path(str(caminho), run_name="__main__")
        except SystemExit as fim:
            codigo = fim.code
        saida.flush()
        erro.flush()
    return codigo, saida.buffer.getvalue().decode("utf-8"), erro.buffer.getvalue().decode("utf-8")
