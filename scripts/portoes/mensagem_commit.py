"""Portão do git (commit-msg): a mensagem segue o formato do Morg Laws (skill git-e-commits).

- título `tipo(área): …` (a área é opcional), com até 72 caracteres e sem ponto final;
- linha em branco entre o título e o corpo; fix, feat e refactor levam corpo com o que mudou e porquê;
- um fix sem nenhum ficheiro em tests/ leva a linha `Sem-teste: <motivo>`.
Os títulos que o próprio git escreve (Merge …, Revert "…") passam. As linhas com # são do git e não contam.
Uso: py -I scripts/portoes/mensagem_commit.py <ficheiro da mensagem>   Sai com 1 se recusar.
"""

import re
import subprocess
import sys
from pathlib import Path

# Com `py -I` a pasta do script não entra no sys.path: sem isto o import seguinte falhava.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lista_negra

TIPOS = ("feat", "fix", "docs", "test", "refactor", "chore", "build", "ci", "perf", "style")
EXIGEM_CORPO = ("feat", "fix", "refactor")
MAXIMO_DO_TITULO = 72
TITULO = re.compile(r"^(?P<tipo>[a-z]+)(?:\([a-z0-9-]+\))?: \S")
TITULOS_DO_GIT = ("Merge ", 'Revert "')
# Linhas finais de metadados: não contam como corpo.
RODAPE = re.compile(r"^(?:Co-Authored-By|Signed-off-by|Sem-teste|Sem-changelog):", re.IGNORECASE)
SEM_TESTE = re.compile(r"^Sem-teste: *\S", re.MULTILINE)


def linhas_da_mensagem(texto):
    """Linhas da mensagem sem os comentários do git e sem as linhas vazias do fim."""
    linhas = [linha.rstrip() for linha in texto.splitlines() if not linha.startswith("#")]
    while linhas and not linhas[-1]:
        linhas.pop()
    return linhas


def erros_do_titulo(titulo):
    """Motivos para recusar o título; o tipo vem em segundo (None se o formato estiver errado)."""
    motivos = []
    if len(titulo) > MAXIMO_DO_TITULO:
        motivos.append(f"ERRO: o título tem {len(titulo)} caracteres (máximo {MAXIMO_DO_TITULO}).")
    formato = TITULO.match(titulo)
    if not formato or formato["tipo"] not in TIPOS:
        motivos.append(f"ERRO: o título tem de começar por tipo(área): … com um destes tipos: {', '.join(TIPOS)}.")
        return motivos, None
    if titulo.endswith("."):
        motivos.append("ERRO: o título não leva ponto final.")
    return motivos, formato["tipo"]


def erros(texto, ficheiros):
    """Lista dos motivos para recusar a mensagem (vazia se estiver certa); `ficheiros` são os do commit."""
    linhas = linhas_da_mensagem(texto)
    if not linhas:
        return ["ERRO: a mensagem do commit está vazia."]
    if linhas[0].startswith(TITULOS_DO_GIT):
        return []
    motivos, tipo = erros_do_titulo(linhas[0])
    if len(linhas) > 1 and linhas[1]:
        motivos.append("ERRO: falta a linha em branco entre o título e o corpo.")
    corpo = [linha for linha in linhas[1:] if linha and not RODAPE.match(linha)]
    if tipo in EXIGEM_CORPO and not corpo:
        motivos.append(f"ERRO: um commit {tipo} leva corpo com o que mudou e porquê.")
    if tipo == "fix" and not any(f.startswith("tests/") for f in ficheiros) and not SEM_TESTE.search(texto):
        motivos.append("ERRO: um fix traz o teste que pega o bug (ficheiro em tests/) ou a linha "
                       "'Sem-teste: <motivo concreto>'.")
    return motivos


def ficheiros_do_commit(correr=None):
    """Ficheiros do commit em curso (o git dá aos hooks o índice certo, também num commit por caminho)."""
    saida = (correr or subprocess.run)(["git", "diff", "--cached", "--name-only"], capture_output=True,
                                       text=True, encoding="utf-8", check=False).stdout
    return saida.splitlines()


def main(argv):
    texto = Path(argv[1]).read_bytes().decode("utf-8", errors="replace")
    motivos = erros(texto, ficheiros_do_commit())
    for motivo in motivos:
        lista_negra.escrever_erro(motivo)
    if motivos:
        lista_negra.escrever_erro("Commit recusado: corrija a mensagem (formato no início de scripts/portoes/mensagem_commit.py).")
    return 1 if motivos else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
