"""Ajudante `arrastar`: uma janela criada com o botão do rato carregado fica solta até se largar o botão.

Ao arrastar uma aba do Chrome para fora, o Chrome cria uma janela nova com o botão ainda carregado e o GlazeWM
mete-a logo no mosaico, rearrumando tudo várias vezes (issue #1080). Este ajudante liga-se ao IPC do GlazeWM
(WebSocket em 127.0.0.1:6123), ouve `window_managed` e, se o botão principal está carregado, põe a janela a
flutuar; ao largar, devolve-a ao mosaico de uma vez. A rede, o rato e o tempo entram por parâmetro (testes).
"""

import json
import re
import time

from morg_websocket import ligar as ligar_websocket
from morg_win32 import _NamedMutex, user32

HOST, PORTA = "127.0.0.1", 6123
NOME_DO_MUTEX = "Local\\MorgArrastar"
TENTATIVAS_DE_LIGACAO, PAUSA_ENTRE_TENTATIVAS = 10, 1.0  # o GlazeWM pode ainda estar a arrancar
INTERVALO_DO_BOTAO = 0.05  # segundos entre olhadelas ao botão enquanto há janelas soltas
PEDIDO_DE_EVENTOS = "sub -e window_managed"
SM_SWAPBUTTON, VK_LBUTTON, VK_RBUTTON, BIT_CARREGADO = 23, 0x01, 0x02, 0x8000
# O id entra numa linha de comandos separada por espaços: só se aceita a forma de um UUID.
UUID = re.compile(r"^[0-9a-fA-F]{8}(-[0-9a-fA-F]{4}){3}-[0-9a-fA-F]{12}$")


def janela_nova(texto):
    """Id da janela de um evento `window_managed` (GlazeWM 3.10.1: data.managedWindow.id), ou None."""
    try:
        mensagem = json.loads(texto)
    except ValueError:
        return None
    dados = mensagem.get("data") if isinstance(mensagem, dict) else None
    if not isinstance(dados, dict) or dados.get("eventType") != "window_managed":
        return None
    janela = dados.get("managedWindow")
    if not isinstance(janela, dict) or janela.get("type") != "window":
        return None
    id_da_janela = janela.get("id")
    return id_da_janela if isinstance(id_da_janela, str) and UUID.match(id_da_janela) else None


def comando_ao_aparecer(texto, botao_carregado):
    """Comando para soltar a janela nova se o botão está carregado; senão None."""
    id_da_janela = janela_nova(texto)
    if id_da_janela is None or not botao_carregado:
        return None
    return f"command --id {id_da_janela} set-floating --centered=false"


def comando_mosaico(id_da_janela):
    return f"command --id {id_da_janela} set-tiling"


def botao_principal_carregado(user32_):
    """Estado físico do botão principal (o direito, se os botões estão trocados); 0 do Windows = solto."""
    tecla = VK_RBUTTON if user32_.GetSystemMetrics(SM_SWAPBUTTON) else VK_LBUTTON
    return bool(user32_.GetAsyncKeyState(tecla) & BIT_CARREGADO)


def correr(cliente, botao_carregado):
    """Ciclo: ouve janelas novas; com o botão carregado solta-as, e ao largar devolve-as ao mosaico.

    Levanta OSError (ConnectionError incluído) quando a ligação cai.
    """
    cliente.enviar_texto(PEDIDO_DE_EVENTOS)
    soltas = []
    while True:
        try:
            texto = cliente.receber(INTERVALO_DO_BOTAO if soltas else None)
        except TimeoutError:
            texto = ""
        if texto is None:
            return
        id_da_janela = janela_nova(texto)
        if id_da_janela and botao_carregado():
            cliente.enviar_texto(comando_ao_aparecer(texto, True))
            soltas.append(id_da_janela)
        if soltas and not botao_carregado():
            for id_solto in soltas:  # as respostas (erro de janela que já não existe) ignoram-se ao ler
                cliente.enviar_texto(comando_mosaico(id_solto))
            soltas.clear()


def _ligar_com_tentativas(ligar, dormir):
    """O cliente ligado, ou None depois de todas as tentativas."""
    for tentativa in range(TENTATIVAS_DE_LIGACAO):
        try:
            return ligar(HOST, PORTA)
        except OSError:
            if tentativa < TENTATIVAS_DE_LIGACAO - 1:
                dormir(PAUSA_ENTRE_TENTATIVAS)
    return None


def arrastar(ligar=ligar_websocket, user32=user32, dormir=time.sleep):
    """Subcomando `arrastar`: um só ajudante de cada vez; sai quando o GlazeWM fecha a ligação."""
    with _NamedMutex(NOME_DO_MUTEX, 0) as dono:
        if not dono:
            return
        cliente = _ligar_com_tentativas(ligar, dormir)
        if cliente is None:
            return
        try:
            correr(cliente, lambda: botao_principal_carregado(user32))
        except OSError:
            pass  # a ligação caiu (o GlazeWM fechou): o ajudante acaba com ele
        finally:
            cliente.fechar()
