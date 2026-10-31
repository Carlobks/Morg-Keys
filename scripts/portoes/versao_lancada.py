"""Portão do git (commit-msg, ADR 0011): uma versão lançada não muda e o VERSION só muda no lançamento.

- mudar uma secção já lançada do CHANGELOG.md (de "## [" para baixo, como estava no último commit) pede a linha
  `Changelog-corrigido: <motivo>`; acrescentar uma versão no topo ou mudar a introdução não pede nada;
- mudar o VERSION pede, no mesmo commit, a secção nova dessa versão no topo do CHANGELOG.md. É o que o
  scripts/changelog/juntar_changelog.py faz; à mão, não (regra VERSÃO SÓ NO LANÇAMENTO).
Chamado pelo mensagem_commit.py.
"""

import re
import subprocess

CHANGELOG_CORRIGIDO = re.compile(r"^Changelog-corrigido: *\S", re.MULTILINE)
SECCAO = re.compile(r"^## \[([^\]]+)\]", re.MULTILINE)


def parte_lancada(changelog):
    """O texto das versões lançadas, da primeira "## [" ao fim ("" se ainda não houver nenhuma)."""
    corte = changelog.find("\n## [")
    return "" if corte < 0 else changelog[corte:]


def erros(texto, ficheiros, antes, depois, versao):
    """Motivos para recusar. `antes` e `depois`: o CHANGELOG.md do último commit e o do commit em curso ("" se não
    houver); `versao`: o VERSION do commit em curso (None se não houver)."""
    motivos = []
    if "CHANGELOG.md" in ficheiros and not depois.endswith(parte_lancada(antes)) \
            and not CHANGELOG_CORRIGIDO.search(texto):
        motivos.append("ERRO: o commit muda uma versão já lançada do CHANGELOG.md, e uma versão lançada não muda "
                       "(ADR 0011). Se é mesmo para corrigir, diga porquê na linha 'Changelog-corrigido: <motivo>'.")
    if "VERSION" in ficheiros:
        topo = SECCAO.search(depois)
        if versao is None or not topo or topo[1] != versao or f"## [{versao}]" in antes:
            motivos.append("ERRO: o VERSION só muda no lançamento, com a secção nova no topo do CHANGELOG.md: "
                           "corra py -I scripts/changelog/juntar_changelog.py (ADR 0011).")
    return motivos


def conteudo(caminho, revisao, correr=None):
    """O ficheiro numa revisão do git ("HEAD", ou "" para o índice do commit em curso); "" se não existir."""
    resultado = (correr or subprocess.run)(["git", "show", f"{revisao}:{caminho}"], capture_output=True, text=True,
                                           encoding="utf-8", check=False)
    return resultado.stdout if resultado.returncode == 0 else ""


def erros_do_commit(texto, ficheiros, correr=None):
    """Os motivos para o commit em curso; sem o CHANGELOG.md nem o VERSION no commit, não pergunta nada ao git."""
    if "CHANGELOG.md" not in ficheiros and "VERSION" not in ficheiros:
        return []
    versao = conteudo("VERSION", "", correr).strip() or None
    return erros(texto, ficheiros, conteudo("CHANGELOG.md", "HEAD", correr), conteudo("CHANGELOG.md", "", correr),
                 versao)
