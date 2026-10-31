"""Junta os fragmentos de changelog.d/ no CHANGELOG.md, na hora de lançar uma versão (ML13).

Formato de um fragmento (changelog.d/AAAA-MM-DD-assunto.md, assunto em minúsculas com hífenes):

    Categoria: Corrigido
    Incompatível: <o que quem instala tem de mudar> (linha opcional)

    - O que mudou, escrito para quem usa o Morg Keys.
      Uma linha de continuação começa por dois espaços.

As categorias e a ordem são as do Keep a Changelog 1.1.0 (Adicionado, Alterado, Obsoleto, Removido,
Corrigido, Segurança); a ideia de um ficheiro por mudança, apagado ao juntar, vem do towncrier
(docs/pesquisa/changelog.md). O README.md da pasta explica isto e não é um fragmento.

A versão (SemVer, ADR 0011) sobe só aqui, pelas categorias: Removido ou Incompatível sobe o MAIOR (no 0.x, o
MENOR); Adicionado, Alterado ou Obsoleto, o MENOR; Corrigido ou Segurança, a CORREÇÃO. O VERSION na raiz é a única
fonte e é escrito na mesma corrida que a secção.
Uso: py -I scripts/changelog/juntar_changelog.py [<versão>] [--rascunho]
     sem <versão>, calcula a próxima; uma <versão> à mão (ex.: a 1.0.0) tem de ser maior do que a do VERSION;
     --rascunho só mostra a secção; sem ele escreve-a no CHANGELOG.md e no VERSION e apaga os fragmentos juntados.
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
INCOMPATIVEL = re.compile(r"^Incompatível: (.+)$")
MARCA_INCOMPATIVEL = "- **Incompatível:** "
SEMVER = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")
SOBE_O_MENOR = {"Adicionado", "Alterado", "Obsoleto"}


def ler_fragmento(texto):
    """(categoria, linhas dos itens) de um fragmento; ValueError com o motivo se estiver mal.
    A linha "Incompatível: …" passa a ser o primeiro item, para se ver na secção da versão."""
    linhas = texto.splitlines()
    cabeca = CATEGORIA.match(linhas[0]) if linhas else None
    if not cabeca:
        raise ValueError("a primeira linha tem de ser 'Categoria: <" + "|".join(CATEGORIAS) + ">'")
    if cabeca.group(1) not in CATEGORIAS:
        raise ValueError(f"categoria desconhecida: {cabeca.group(1)}")
    aviso = INCOMPATIVEL.match(linhas[1]) if len(linhas) > 1 else None
    if aviso:
        linhas = [linhas[0], *linhas[2:]]
    if len(linhas) > 1 and linhas[1]:
        raise ValueError("falta a linha em branco depois da categoria")
    itens = linhas[2:]
    while itens and not itens[-1]:
        itens.pop()
    if not itens:
        raise ValueError("sem itens")
    if not itens[0].startswith("- ") or any(not linha.startswith(("- ", "  ")) for linha in itens):
        raise ValueError("cada item começa por '- ' (continuação com dois espaços), sem linhas vazias")
    return cabeca.group(1), ([MARCA_INCOMPATIVEL + aviso.group(1)] if aviso else []) + itens


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


def ler_versao(raiz):
    """A versão do VERSION na raiz; "0.0.0" antes do 1.º lançamento; ValueError se estiver mal escrita."""
    try:
        texto = (raiz / "VERSION").read_bytes().decode("utf-8").strip()
    except FileNotFoundError:
        return "0.0.0"
    if not SEMVER.match(texto):
        raise ValueError(f"VERSION mal escrito: {texto!r} (tem de ser MAIOR.MENOR.CORREÇÃO)")
    return texto


def numeros(versao):
    """(MAIOR, MENOR, CORREÇÃO) em inteiros, para comparar: 9.9.10 vem depois de 9.9.9."""
    return tuple(int(n) for n in versao.split("."))


def proxima_versao(atual, categorias, incompativel):
    """A versão seguinte pelo SemVer; no 0.x uma mudança incompatível sobe só o MENOR (ADR 0011)."""
    maior, menor, correcao = numeros(atual)
    if incompativel or "Removido" in categorias:
        return f"{maior + 1}.0.0" if maior else f"0.{menor + 1}.0"
    if SOBE_O_MENOR.intersection(categorias):
        return f"{maior}.{menor + 1}.0"
    return f"{maior}.{menor}.{correcao + 1}"


def juntar(raiz, versao, dia, rascunho=False):
    """(código, texto): 0 e a secção escrita (ou só mostrada); 1 e o motivo, sem mexer em nada.
    Sem `versao`, calcula-a; uma à mão tem de ser maior do que a do VERSION."""
    lidos, erros = fragmentos_da_pasta(raiz / "changelog.d")
    if erros:
        return 1, "\n".join(erros)
    if not lidos:
        return 1, "Não há fragmentos em changelog.d/ para juntar."
    try:
        atual = ler_versao(raiz)
    except ValueError as motivo:
        return 1, str(motivo)
    if versao is None:
        incompativel = any(linha.startswith(MARCA_INCOMPATIVEL) for _, _, itens in lidos for linha in itens)
        versao = proxima_versao(atual, [categoria for _, categoria, _ in lidos], incompativel)
    elif not SEMVER.match(versao) or numeros(versao) <= numeros(atual):
        return 1, f"A versão {versao} tem de ser MAIOR.MENOR.CORREÇÃO e maior do que a atual ({atual})."
    nova = secao(versao, dia, lidos)
    if not rascunho:
        destino = raiz / "CHANGELOG.md"
        texto = destino.read_bytes().decode("utf-8")
        corte = texto.find("\n## [")
        corte = len(texto) if corte < 0 else corte
        destino.write_bytes((texto[:corte] + "\n" + nova + texto[corte:]).encode("utf-8"))
        (raiz / "VERSION").write_bytes(f"{versao}\n".encode())
        for caminho, _, _ in lidos:
            caminho.unlink()
    return 0, nova


def escrever(canal, texto):
    """Escreve em UTF-8: numa consola cp1252 o print rebentava com o "✻" e estragava os acentos (A16)."""
    canal.flush()
    canal.buffer.write((texto + "\n").encode("utf-8"))
    canal.flush()


def main(argv, raiz=RAIZ, hoje=date.today):
    rascunho = argv[-1:] == ["--rascunho"]
    resto = argv[1:-1] if rascunho else argv[1:]
    if len(resto) > 1 or any(a.startswith("--") for a in resto):
        escrever(sys.stderr, __doc__.split("Uso: ")[1])
        return 2
    codigo, texto = juntar(raiz, resto[0] if resto else None, hoje(), rascunho=rascunho)
    escrever(sys.stderr if codigo else sys.stdout, texto)
    return codigo


if __name__ == "__main__":
    sys.exit(main(sys.argv))
