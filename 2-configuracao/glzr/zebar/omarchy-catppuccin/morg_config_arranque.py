"""Configuração do arranque (arranque.txt): animação escolhida e programas .bat."""

import os
from pathlib import Path

from morg_processos import HERE

SPLASH_DIR = HERE / "arranque"

# Configuração do arranque, editável pelo utilizador (Documentos\Guia de Atalhos\arranque.txt):
#   animacao = cafe
#   bat = C:\caminho\programa.bat | http://localhost:3000 | Nome   (endereço e nome opcionais)
ARRANQUE_FILE = HERE / "guia" / "arranque.txt"
# Animações do ecrã de arranque: nome -> (rótulo, imagem da cortina nativa, largura, altura).
# A imagem é o 1.º quadro da animação, no mesmo tamanho e sítio (centro a ANIM_CY da altura)
# em que o splash.html a desenha: assim a passagem cortina -> animação não se nota.
# Nova animação: entrada aqui + bloco data-anim no splash.html + BMP (ver docs/receitas.md, receita 5b).
ANIMACOES = {
    "cafe": ("Café", "cafe.bmp", 280, 280),
}
ANIM_CY = 0.38

def _arranque_cfg():
    """Lê arranque.txt: {"animacao": nome, "bats": [{"path", "url", "name"}]}."""
    cfg = {"animacao": "cafe", "bats": []}
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
