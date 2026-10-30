"""Portão do git (pre-push): nada sai desta máquina sem as verificações (Morg Laws, skill auditoria-de-seguranca).

Para cada ref enviada (o git dá uma por linha no stdin: <ref local> <sha local> <ref remota> <sha remoto>):
1. mostra os ficheiros de cada commit a enviar, também os apagados depois, para o dono ver o que sai (Akita #78);
2. corre o gitleaks nesses commits; sem gitleaks o push não sai (falhar fechado);
3. com package-lock.json, corre o npm audit e só trava um aviso crítico ou alto que não esteja na linha de base
   .seguranca/audit-linha-de-base.txt (um ID por linha; a lista só encolhe, nunca se acrescenta para passar).
Uso: no .githooks/pre-push. Sai com 1 se travar e com 0 se o push puder sair.
"""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

# Com `py -I` a pasta do script não entra no sys.path: sem isto o import seguinte falhava.
sys.path.insert(0, str(Path(__file__).resolve().parent))
import lista_negra

RAIZ = Path(__file__).resolve().parents[2]
ZEROS = "0" * 40
GRAVES = ("critical", "high")
# O winget instala o gitleaks aqui; o PATH novo só chega às consolas abertas depois da instalação.
PASTA_DO_WINGET = Path(os.environ.get("LOCALAPPDATA", "")) / "Microsoft" / "WinGet" / "Packages"


def intervalos(linhas):
    """[(ref local, opções do git log com os commits a enviar)]; apagar um ramo não envia código."""
    resultado = []
    for linha in linhas:
        partes = linha.split()
        if len(partes) != 4 or partes[1] == ZEROS:
            continue
        ref_local, sha_local, _, sha_remoto = partes
        novo = sha_remoto == ZEROS  # ramo novo: só o que nenhum remoto conhecido tem
        resultado.append((ref_local, [sha_local, "--not", "--remotes"] if novo else [f"{sha_remoto}..{sha_local}"]))
    return resultado


def achar_gitleaks(which=None, candidatos=None):
    """Caminho do gitleaks: o do PATH ou o da pasta do winget; None se não estiver instalado."""
    no_path = (which or shutil.which)("gitleaks")
    if no_path:
        return no_path
    if candidatos is None:
        candidatos = sorted(PASTA_DO_WINGET.glob("Gitleaks.Gitleaks_*/gitleaks.exe"))
    return str(candidatos[0]) if candidatos else None


def ler_base(caminho):
    """IDs da linha de base do npm audit (sem comentários)."""
    if not caminho.is_file():
        return set()
    linhas = caminho.read_text(encoding="utf-8").splitlines()
    return {linha.split("#")[0].strip() for linha in linhas if linha.split("#")[0].strip()}


def avisos_novos(texto, base):
    """Avisos críticos ou altos do `npm audit --json` fora da linha de base; ValueError se ilegível."""
    try:
        relatorio = json.loads(texto)
    except json.JSONDecodeError as erro:
        raise ValueError("o relatório do npm audit não é JSON") from erro
    if "vulnerabilities" not in relatorio:
        raise ValueError(f"o npm audit não devolveu as vulnerabilidades: {str(relatorio.get('error'))[:200]}")
    novos = []
    for pacote in relatorio["vulnerabilities"].values():
        for via in pacote.get("via", []):
            if isinstance(via, dict) and via.get("severity") in GRAVES and str(via.get("source")) not in base:
                novos.append(f"{via['source']} {via['severity']} {via['name']}: {via['title']}")
    return novos


def verificar_commits(intervalo, correr, gitleaks):
    """Mostra os ficheiros dos commits e corre o gitleaks; devolve True se puderem sair."""
    ref_local, opcoes = intervalo
    lista = correr(["git", "log", "--name-status", "--format=%h %s", *opcoes], capture_output=True, text=True,
                   encoding="utf-8", errors="replace", check=False).stdout
    lista_negra.escrever_erro(f"== A enviar em {ref_local}:\n{lista.strip()}")
    if gitleaks is None:
        lista_negra.escrever_erro("ERRO: o gitleaks não está instalado; o push não sai sem a verificação de segredos.")
        return False
    resultado = correr([gitleaks, "git", f"--log-opts={' '.join(opcoes)}", "--redact", "--no-banner"], check=False)
    if resultado.returncode != 0:
        lista_negra.escrever_erro(f"ERRO: o gitleaks achou um possível segredo em {ref_local}. Tire-o do histórico.")
        return False
    return True


def verificar_bibliotecas(correr, which, raiz):
    """npm audit contra a linha de base; devolve True se não houver aviso grave novo."""
    if not (raiz / "package-lock.json").is_file():
        return True
    npm = (which or shutil.which)("npm") or "npm"
    saida = correr([npm, "audit", "--json"], capture_output=True, text=True, encoding="utf-8", errors="replace",
                   check=False, cwd=raiz).stdout
    try:
        novos = avisos_novos(saida, ler_base(raiz / ".seguranca" / "audit-linha-de-base.txt"))
    except ValueError as erro:
        lista_negra.escrever_erro(f"ERRO: npm audit sem relatório legível ({erro}). O push não sai sem a verificação.")
        return False
    for aviso in novos:
        lista_negra.escrever_erro(f"ERRO: aviso novo de segurança nas dependências: {aviso}")
    if novos:
        lista_negra.escrever_erro("Atualize a biblioteca. Não acrescente o ID à linha de base para passar.")
    return not novos


def main(entrada=None, correr=None, achar=None, which=None, raiz=None):
    correr, raiz = correr or subprocess.run, raiz or RAIZ
    linhas = (entrada or sys.stdin.buffer).read().decode("utf-8", errors="replace").splitlines()
    pedidos = intervalos(linhas)
    gitleaks = (achar or achar_gitleaks)() if pedidos else None
    resultados = [verificar_commits(pedido, correr, gitleaks) for pedido in pedidos]
    resultados.append(verificar_bibliotecas(correr, which, raiz))
    return 0 if all(resultados) else 1


if __name__ == "__main__":
    sys.exit(main())
