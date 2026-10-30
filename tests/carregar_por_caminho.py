"""Carrega pelo caminho os scripts que não estão num pacote: os portões do git e os hooks do Claude Code."""

import importlib.util
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PASTA_PORTOES = RAIZ / "scripts" / "portoes"
PASTA_HOOKS = RAIZ / ".claude" / "hooks"


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
