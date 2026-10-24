"""Configuração do arranque (arranque.txt): animação escolhida, nome da saudação e programas .bat;
e a frase do dia (frases.txt)."""

import os
import time
from pathlib import Path

from morg_processos import HERE

SPLASH_DIR = HERE / "arranque"

# Configuração do arranque, editável pelo utilizador (Documentos\Guia de Atalhos\arranque.txt):
#   animacao = cafe
#   nome = Carlos                                                   (saudação: "Muito bem-vindo, Carlos")
#   bat = C:\caminho\programa.bat | http://localhost:3000 | Nome   (endereço e nome opcionais)
ARRANQUE_FILE = HERE / "guia" / "arranque.txt"
# Frases do ecrã de boas-vindas, uma por dia do mês: "frase | personagem | anime" (mesma pasta, editável).
FRASES_FILE = HERE / "guia" / "frases.txt"
# Animações do ecrã de arranque: nome -> rótulo. Nova animação: entrada aqui + bloco data-anim no
# splash.html (ver docs/receitas.md, receita 5b).
ANIMACOES = {
    "cafe": "Café",
}


def _frase_do_dia(linhas, dia):
    """Frase do dia `dia` (1–31) a partir das linhas do frases.txt (comentários # e linhas vazias não contam;
    com menos linhas do que dias, volta ao início): {"texto", "personagem", "anime"} ou None."""
    frases = [[p.strip() for p in linha.split("|")] + ["", ""] for linha in linhas
              if linha.strip() and not linha.lstrip().startswith("#")]
    if not frases:
        return None
    texto, personagem, anime = frases[(dia - 1) % len(frases)][:3]
    return {"texto": texto, "personagem": personagem, "anime": anime}


def _frase_de_hoje():
    """A frase de hoje do frases.txt (None sem ficheiro ou sem frases)."""
    try:
        linhas = FRASES_FILE.read_text(encoding="utf-8-sig").splitlines()
    except OSError:
        return None
    return _frase_do_dia(linhas, time.localtime().tm_mday)


def _arranque_cfg():
    """Lê arranque.txt: {"animacao": nome, "nome": quem saudar, "bats": [{"path", "url", "name"}]}."""
    cfg = {"animacao": "cafe", "nome": "", "bats": []}
    try:
        lines = ARRANQUE_FILE.read_text(encoding="utf-8-sig").splitlines()
    except OSError:
        return cfg
    for raw in lines:
        line = raw.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = (p.strip() for p in line.split("=", 1))
        key = key.lower()
        if key in ("animacao", "animação"):
            name = value.lower().replace("é", "e")
            if name in ANIMACOES:
                cfg["animacao"] = name
        elif key == "nome":
            cfg["nome"] = value
        elif key == "bat" and value:
            parts = [p.strip().strip('"') for p in value.split("|")] + ["", ""]
            if parts[0]:
                cfg["bats"].append({"path": parts[0], "url": parts[1], "name": parts[2] or Path(parts[0]).stem})
    return cfg


def _set_animacao(name):
    """Grava "animacao = name" em arranque.txt, mantendo o resto do ficheiro."""
    try:
        lines = ARRANQUE_FILE.read_text(encoding="utf-8-sig").splitlines()
    except OSError:
        lines = []
    for i, raw in enumerate(lines):
        s = raw.strip()
        if not s.startswith("#") and "=" in s and s.split("=", 1)[0].strip().lower() in ("animacao", "animação"):
            lines[i] = f"animacao = {name}"
            break
    else:
        lines.append(f"animacao = {name}")
    tmp = ARRANQUE_FILE.with_suffix(".tmp")
    tmp.write_text("\n".join(lines) + "\n", encoding="utf-8")
    os.replace(tmp, ARRANQUE_FILE)
