"""Sistema falso para testar o bar_helper.py sem tocar no Windows real.

- Ficheiros (layout.json, apps.txt, config.yaml, desfazer, cache do menu Iniciar) numa pasta temporária.
- GlazeWM falso: árvore de workspaces em memória; `move` muda mesmo a janela de sítio.
- Relógio falso: `sleep` avança o tempo na hora (os testes não esperam).
- Abridor falso: abrir uma app faz aparecer a janela dela (já ou ao fim de N segundos).
- user32/kernel32/shell32/subprocess trocados por **bombas**: se o código chamar o Windows real por um
  caminho que o teste não previu, o teste rebenta em vez de mexer no PC (A2, ficheiros do utilizador).
"""

import copy
import importlib.util
import sys
import tempfile
import time as time_real
from contextlib import ExitStack
from pathlib import Path
from unittest import mock

PASTA_PACK = Path(__file__).resolve().parent.parent / "2-configuracao" / "glzr" / "zebar" / "omarchy-catppuccin"


class ModulosMorg:
    """O bar_helper.py e os módulos morg_*.py vistos como um só: `bh.nome` procura o nome em todos.

    Assim os testes de caracterização (escritos quando era um só ficheiro) não mudam com a divisão.
    """

    def __init__(self, modulos):
        self.modulos = modulos

    def __getattr__(self, nome):
        for modulo in self.modulos:
            if hasattr(modulo, nome):
                return getattr(modulo, nome)
        raise AttributeError(nome)

    def com_o_nome(self, nome):
        """Todos os módulos onde o nome existe (definido ou importado pelo nome)."""
        return [modulo for modulo in self.modulos if hasattr(modulo, nome)]


def carregar_bar_helper():
    """Importa o bar_helper.py pelo caminho (ele importa os morg_*.py; só configuram o ctypes)."""
    if "bar_helper" not in sys.modules:
        especificacao = importlib.util.spec_from_file_location("bar_helper", PASTA_PACK / "bar_helper.py")
        modulo = importlib.util.module_from_spec(especificacao)
        sys.modules["bar_helper"] = modulo
        especificacao.loader.exec_module(modulo)
    morg = sorted((m for n, m in sys.modules.items() if n.startswith("morg_")), key=lambda m: m.__name__)
    return ModulosMorg([sys.modules["bar_helper"], *morg])


class ToqueNoSistemaReal(AssertionError):
    """O código tentou usar o Windows real num teste."""


class Bomba:
    """Objeto que rebenta em qualquer atributo, menos nos permitidos (gravadores)."""

    def __init__(self, nome, permitidos=None):
        self._nome, self._permitidos = nome, dict(permitidos or {})

    def __getattr__(self, atributo):
        if atributo in self._permitidos:
            return self._permitidos[atributo]
        raise ToqueNoSistemaReal(f"o teste tocou em {self._nome}.{atributo}")


class RelogioFalso:
    """Substitui o módulo `time` dentro do bar_helper."""

    def __init__(self):
        self.agora = 1000.0
        self.ao_avancar = []  # funções chamadas depois de cada sleep (fazem aparecer janelas)

    def monotonic(self):
        return self.agora

    def time(self):
        return 1_800_000_000 + self.agora

    def time_ns(self):
        return int(self.time() * 1e9)

    def sleep(self, segundos):
        self.agora += segundos
        for funcao in list(self.ao_avancar):
            funcao(self.agora)

    def strftime(self, formato, *resto):
        return time_real.strftime(formato, *resto)


class GlazeFalso:
    """Faz de CLI do GlazeWM (`_glaze`): responde a query workspaces e executa `move`."""

    def __init__(self, workspaces=None, ligado=True):
        self.workspaces = workspaces if workspaces is not None else [espaco(str(n)) for n in range(1, 11)]
        self.ligado = ligado
        self.comandos = []
        self._proximo_id = 1

    def __call__(self, *args):
        if not self.ligado:
            return {}
        if args == ("query", "workspaces"):
            return {"success": True, "data": {"workspaces": copy.deepcopy(self.workspaces)}}
        self.comandos.append(args)
        if len(args) == 6 and args[0] == "command" and args[1] == "--id" and args[3:5] == ("move", "--workspace"):
            self._mover(args[2], args[5])
        return {"success": True}

    def janela(self, processo, titulo="", workspace="1"):
        """Acrescenta uma janela aberta; devolve o id."""
        ident = f"j{self._proximo_id}"
        self._proximo_id += 1
        self._espaco(workspace)["children"].append(
            {"id": ident, "type": "window", "processName": processo, "title": titulo})
        return ident

    def onde_esta(self, ident):
        for ws in self.workspaces:
            if any(c["id"] == ident for c in ws["children"]):
                return ws["name"]
        return None

    def _espaco(self, nome):
        return next(ws for ws in self.workspaces if ws["name"] == nome)

    def _mover(self, ident, destino):
        for ws in self.workspaces:
            for janela in list(ws["children"]):
                if janela["id"] == ident:
                    ws["children"].remove(janela)
                    self._espaco(destino)["children"].append(janela)
                    return


def espaco(nome, foco=False):
    return {"name": nome, "type": "workspace", "hasFocus": foco, "children": []}


class AbridorFalso:
    """Faz de `_shell_open` e `os.startfile`: regista o que se abriu e faz aparecer a janela."""

    def __init__(self, glaze, relogio):
        self.glaze, self.relogio = glaze, relogio
        self.abertos = []
        self.janelas_por_ficheiro = {}  # ficheiro -> (processo, título, atraso em segundos)
        self._por_aparecer = []
        relogio.ao_avancar.append(self._fazer_aparecer)

    def app(self, ficheiro, processo, titulo="", atraso=0.0):
        self.janelas_por_ficheiro[ficheiro] = (processo, titulo, atraso)

    def aparece_sozinha(self, processo, titulo="", atraso=0.0):
        """Uma janela que aparece daqui a `atraso` segundos sem ninguém a abrir (ex.: app do Arranque)."""
        self._por_aparecer.append((self.relogio.agora + atraso, processo, titulo))

    def shell_open(self, launch, log=None):
        ficheiro = launch["file"]
        self.abertos.append((ficheiro, launch.get("args")))
        if ficheiro not in self.janelas_por_ficheiro:
            if log:
                log(f"não consegui abrir {ficheiro} (falso)")
            return False
        processo, titulo, atraso = self.janelas_por_ficheiro[ficheiro]
        if processo is None:  # programa sem janela (ex.: o GlazeWM)
            return True
        self._por_aparecer.append((self.relogio.agora + atraso, processo, titulo))
        self._fazer_aparecer(self.relogio.agora)
        return True

    def startfile(self, caminho):
        if not self.shell_open({"file": caminho}):
            raise OSError(f"falso: não sei abrir {caminho}")

    def _fazer_aparecer(self, agora):
        for item in list(self._por_aparecer):
            quando, processo, titulo = item
            if agora >= quando:
                self._por_aparecer.remove(item)
                focado = next((w["name"] for w in self.glaze.workspaces if w.get("hasFocus")), "1")
                self.glaze.janela(processo, titulo, focado)


class SistemaFalso:
    """`with SistemaFalso() as s:` — o bar_helper (s.bh) fica a falar só com falsos."""

    def __init__(self, workspaces=None, apps_do_menu=None, processos_a_correr=()):
        self.bh = carregar_bar_helper()
        self.glaze = GlazeFalso(workspaces)
        self.relogio = RelogioFalso()
        self.abridor = AbridorFalso(self.glaze, self.relogio)
        self.apps_do_menu = list(apps_do_menu or [])  # [{"Name", "AppID"}]
        self.processos_a_correr = set(processos_a_correr)
        self.bipes = []
        self.registo = []
        self._pilha = ExitStack()

    def __enter__(self):
        self.pasta = Path(self._pilha.enter_context(tempfile.TemporaryDirectory()))
        caminhos = {
            "LAYOUT_FILE": self.pasta / "layout.json",
            "APPS_FILE": self.pasta / "apps.txt",
            "GLAZE_CONFIG": self.pasta / "config.yaml",
            "PANEL_UNDO": self.pasta / ".panel-undo.json",
            "PANEL_PREV": self.pasta / ".panel-prev",
            "START_CACHE": self.pasta / ".start-apps.json",
            "RESTORE_LOG": self.pasta / ".layout-restore.log",
        }
        bh = self.bh
        trocas = {
            **caminhos,
            "_glaze": self.glaze,
            "_shell_open": self.abridor.shell_open,
            "_start_items": lambda use_cache=False: list(self.apps_do_menu),
            "_running_images": lambda: set(self.processos_a_correr),
            "time": self.relogio,
            "user32": Bomba("user32", {"MessageBeep": self.bipes.append}),
            "kernel32": Bomba("kernel32"),
            "shell32": Bomba("shell32"),
            "dwmapi": Bomba("dwmapi"),
            "subprocess": Bomba("subprocess"),
        }
        for nome, valor in trocas.items():
            self.trocar(nome, valor)
        self._pilha.enter_context(mock.patch.object(bh.os, "startfile", self.abridor.startfile, create=True))
        bh._PANEL_PUSHED.clear()
        return self

    def trocar(self, nome, valor):
        """Troca `nome` por `valor` em todos os módulos que o têm (até ao fim do `with`)."""
        modulos = self.bh.com_o_nome(nome)
        if not modulos:
            raise AttributeError(f"nenhum módulo tem {nome}")
        for modulo in modulos:
            self._pilha.enter_context(mock.patch.object(modulo, nome, valor))

    def __exit__(self, *erro):
        return self._pilha.__exit__(*erro)

    def log(self, mensagem):
        self.registo.append(mensagem)

    def escrever(self, nome_constante, texto):
        getattr(self.bh, nome_constante).write_text(texto, encoding="utf-8")

    def ler(self, nome_constante):
        caminho = getattr(self.bh, nome_constante)
        return caminho.read_text(encoding="utf-8") if caminho.exists() else None


def config_minimo(bh, bloco=None):
    """Um config.yaml mínimo: atalhos fixos do sistema e o bloco gerado (vazio ou com estas linhas)."""
    meio = "\n".join(bloco or [])
    return (
        "general:\n  startup_commands: []\n\nkeybindings:\n"
        "  - commands: ['focus --direction left']\n    bindings: ['alt+h', 'alt+left']\n"
        "  - commands: ['toggle-floating']\n    bindings: ['alt+shift+space']\n"
        f"{bh.APPS_BEGIN}\n{meio + chr(10) if meio else ''}{bh.APPS_END}\n"
        "  - commands: ['wm-exit']\n    bindings: ['alt+shift+e']\n"
    )
