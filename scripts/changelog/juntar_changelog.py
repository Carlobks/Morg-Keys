"""Junta os fragmentos de changelog.d/ no CHANGELOG.md, na hora de lançar uma versão (ML13).

Formato de um fragmento (changelog.d/AAAA-MM-DD-assunto.md, assunto em minúsculas com hífenes):

    Categoria: Corrigido

    - O que mudou, escrito para quem usa o Morg Keys.
      Uma linha de continuação começa por dois espaços.

As categorias e a ordem são as do Keep a Changelog 1.1.0 (Adicionado, Alterado, Obsoleto, Removido,
Corrigido, Segurança); a ideia de um ficheiro por mudança, apagado ao juntar, vem do towncrier
(docs/pesquisa/changelog.md). O README.md da pasta explica isto e não é um fragmento.
Uso: py -I scripts/changelog/juntar_changelog.py <versão> [--rascunho]
     --rascunho só mostra a secção; sem ele escreve-a no CHANGELOG.md e apaga os fragmentos juntados.
"""

import re
import sys
from datetime import date
from pathlib import Path

RAIZ = Path(__file__).resolve().parents[2]
CATEGORIAS = ("Adicionado", "Alterado", "Obsoleto", "Removido", "Corrigido", "Segurança")
NOME = re.compile(r"^\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*\.md$")
CATEGORIA = re.compile(r"^Categoria: (.+)$")
IGNORADOS = ("README.md",)


def ler_fragmento(texto):
    """(categoria, linhas dos itens) de um fragmento; ValueError com o motivo se estiver mal."""
    linhas = texto.splitlines()
    cabeca = CATEGORIA.match(linhas[0]) if linhas else None
    if not cabeca:
        raise ValueError("a primeira linha tem de ser 'Categoria: <" + "|".join(CATEGORIAS) + ">'")
    if cabeca.group(1) not in CATEGORIAS:
        raise ValueError(f"categoria desconhecida: {cabeca.group(1)}")
    if len(linhas) > 1 and linhas[1]:
        raise ValueError("falta a linha em branco depois da categoria")
    itens = linhas[2:]
    while itens and not itens[-1]:
        itens.pop()
    if not itens:
        raise ValueError("sem itens")
    if not itens[0].startswith("- ") or any(not linha.startswith(("- ", "  ")) for linha in itens):
        raise ValueError("cada item começa por '- ' (continuação com dois espaços), sem linhas vazias")
    return cabeca.group(1), itens


def fragmentos_da_pasta(pasta):
    """[(caminho, categoria, itens)] por ordem do nome, e a lista de erros 'nome: motivo'."""
    lidos, erros = [], []
    for caminho in sorted(p for p in pasta.iterdir() if p.name not in IGNORADOS):
        if not NOME.match(caminho.name):
            erros.append(f"{caminho.name}: o nome tem de ser AAAA-MM-DD-assunto.md (minúsculas e hífenes)")
            continue
        try:
            lidos.append((caminho, *ler_fragmento(caminho.read_bytes().decode("utf-8"))))
        except ValueError as motivo:
            erros.append(f"{caminho.name}: {motivo}")
    return lidos, erros


def erros_da_pasta(pasta):
    """Erros dos fragmentos da pasta (vazio se estiverem todos certos)."""
    return fragmentos_da_pasta(pasta)[1]


def secao(versao, dia, lidos):
    """Texto da secção da versão, com as categorias pela ordem do Keep a Changelog."""
    partes = [f"## [{versao}] - {dia.isoformat()}\n"]
    for categoria in CATEGORIAS:
        itens = [linha for _, cat, linhas in lidos if cat == categoria for linha in linhas]
        if itens:
            partes.append(f"\n### {categoria}\n\n" + "\n".join(itens) + "\n")
    return "".join(partes)


def juntar(raiz, versao, dia, rascunho=False):
    """(código, texto): 0 e a secção escrita (ou só mostrada); 1 e o motivo, sem mexer em nada."""
    lidos, erros = fragmentos_da_pasta(raiz / "changelog.d")
    if erros:
        return 1, "\n".join(erros)
    if not lidos:
        return 1, "Não há fragmentos em changelog.d/ para juntar."
    nova = secao(versao, dia, lidos)
    if not rascunho:
        destino = raiz / "CHANGELOG.md"
        atual = destino.read_bytes().decode("utf-8")
        corte = atual.find("\n## [")
        corte = len(atual) if corte < 0 else corte
        destino.write_bytes((atual[:corte] + "\n" + nova + atual[corte:]).encode("utf-8"))
        for caminho, _, _ in lidos:
            caminho.unlink()
    return 0, nova


def escrever(canal, texto):
    """Escreve em UTF-8: numa consola cp1252 o print rebentava com o "✻" e estragava os acentos (A16)."""
    canal.flush()
    canal.buffer.write((texto + "\n").encode("utf-8"))
    canal.flush()


def main(argv, raiz=RAIZ, hoje=date.today):
    if len(argv) not in (2, 3) or argv[2:] not in ([], ["--rascunho"]):
        escrever(sys.stderr, __doc__.split("Uso: ")[1])
        return 2
    codigo, texto = juntar(raiz, argv[1], hoje(), rascunho=argv[2:] == ["--rascunho"])
    escrever(sys.stderr if codigo else sys.stdout, texto)
    return codigo


if __name__ == "__main__":
    sys.exit(main(sys.argv))
