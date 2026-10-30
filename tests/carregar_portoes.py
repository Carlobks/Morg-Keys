"""Carrega os portões do git (scripts/portoes/*.py) pelo caminho: a pasta scripts não é um pacote."""

import importlib.util
from pathlib import Path

PASTA_PORTOES = Path(__file__).resolve().parent.parent / "scripts" / "portoes"


def carregar_portao(nome):
    """Importa scripts/portoes/<nome>.py como módulo."""
    especificacao = importlib.util.spec_from_file_location(f"portao_{nome}", PASTA_PORTOES / f"{nome}.py")
    modulo = importlib.util.module_from_spec(especificacao)
    especificacao.loader.exec_module(modulo)
    return modulo
