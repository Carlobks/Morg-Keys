"""Falsos das bibliotecas do Windows (user32, kernel32, shell32, subprocess) para os testes de cobertura.

`Gravador` é uma bomba que só deixa chamar as funções com resposta prevista: cada chamada fica gravada
em `chamadas` e devolve a resposta (valor, ou função chamada com os mesmos argumentos). Uma função sem
resposta rebenta (ToqueNoSistemaReal), como as bombas do sistema_falso.py: o teste nunca chega ao Windows.
"""

import subprocess as subprocess_real
from types import SimpleNamespace

from sistema_falso import ToqueNoSistemaReal


class Gravador:
    """user32/kernel32/shell32/dwmapi falsos: `Gravador("user32", ShowWindow=1, FindWindowW=lambda c, t: 7)`."""

    def __init__(self, nome, **respostas):
        self._nome, self._respostas, self.chamadas = nome, respostas, []

    def __getattr__(self, funcao):
        if funcao.startswith("_"):
            raise AttributeError(funcao)
        if funcao not in self._respostas:
            raise ToqueNoSistemaReal(f"o teste tocou em {self._nome}.{funcao}")
        resposta = self._respostas[funcao]

        def chamar(*args):
            self.chamadas.append((funcao, *args))
            return resposta(*args) if callable(resposta) else resposta
        return chamar

    def nomes(self):
        """Só os nomes das funções chamadas, pela ordem."""
        return [chamada[0] for chamada in self.chamadas]

    def de(self, funcao):
        """Os argumentos de cada chamada a esta função."""
        return [chamada[1:] for chamada in self.chamadas if chamada[0] == funcao]


class SubprocessFalso:
    """Faz de módulo `subprocess`: grava `run`/`Popen` e devolve o que `ao_correr(cmd)` disser.

    `ao_correr` devolve o stdout (texto) ou levanta uma exceção (ex.: OSError) para simular a falha.
    """

    DEVNULL, STDOUT, PIPE = subprocess_real.DEVNULL, subprocess_real.STDOUT, subprocess_real.PIPE
    TimeoutExpired = subprocess_real.TimeoutExpired

    def __init__(self, ao_correr=lambda cmd: ""):
        self.ao_correr, self.corridos, self.lancados = ao_correr, [], []

    def run(self, cmd, **kw):
        self.corridos.append((list(cmd), kw))
        return SimpleNamespace(stdout=self.ao_correr(cmd), returncode=0)

    def Popen(self, cmd, **kw):
        self.lancados.append((list(cmd), kw))
        self.ao_correr(cmd)
        return SimpleNamespace(pid=4321, poll=lambda: None)


def falha_uma_vez(excecao=OSError):
    """ao_correr que rebenta na 1.ª chamada e depois corre bem (ex.: sem BREAKAWAY_FROM_JOB)."""
    estado = {"vezes": 0}

    def ao_correr(cmd):
        estado["vezes"] += 1
        if estado["vezes"] == 1:
            raise excecao("falso")
        return ""
    return ao_correr
