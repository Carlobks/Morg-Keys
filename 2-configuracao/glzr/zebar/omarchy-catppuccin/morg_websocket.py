"""Cliente WebSocket mínimo (RFC 6455), só com a biblioteca padrão.

Serve ao ajudante `arrastar`, que fala com o IPC do GlazeWM (WebSocket em 127.0.0.1:6123). Faz só o que ele
precisa: aperto de mão, texto com máscara, ler texto (inclui mensagens fragmentadas), responder ao ping e ao
close. A rede e o acaso entram por parâmetro, para os testes não tocarem em nada real.
"""

import base64
import hashlib
import os
import socket

GUID_RFC6455 = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
OPCODE_CONTINUACAO, OPCODE_TEXTO, OPCODE_FECHAR, OPCODE_PING, OPCODE_PONG = 0, 1, 8, 9, 10


class ErroWebSocket(ConnectionError):
    """O servidor não cumpriu o protocolo, ou a ligação caiu a meio."""


def ligar(host, port, criar_ligacao=None, chave_aleatoria=os.urandom, mascara_aleatoria=os.urandom):
    """Abre a ligação, faz o aperto de mão e devolve o ClienteWebSocket."""
    ligacao = (criar_ligacao or socket.create_connection)((host, port))
    try:
        chave = base64.b64encode(chave_aleatoria(16)).decode()
        ligacao.sendall(_pedido_de_atualizacao(host, port, chave).encode())
        sobra = _verificar_resposta(ligacao, chave)
    except BaseException:
        ligacao.close()
        raise
    return ClienteWebSocket(ligacao, mascara_aleatoria, sobra)


def _pedido_de_atualizacao(host, port, chave):
    return ("GET / HTTP/1.1\r\n"
            f"Host: {host}:{port}\r\n"
            "Upgrade: websocket\r\n"
            "Connection: Upgrade\r\n"
            f"Sec-WebSocket-Key: {chave}\r\n"
            "Sec-WebSocket-Version: 13\r\n\r\n")


def _verificar_resposta(ligacao, chave):
    """Lê a resposta HTTP até à linha em branco; devolve os bytes que vieram a mais (já tramas)."""
    recebido = b""
    while b"\r\n\r\n" not in recebido:
        pedaco = ligacao.recv(4096)
        if not pedaco:
            raise ErroWebSocket("o servidor fechou durante o aperto de mão")
        recebido += pedaco
    cabecalho, _, sobra = recebido.partition(b"\r\n\r\n")
    linhas = cabecalho.decode("latin-1").split("\r\n")
    if linhas[0].split()[1:2] != ["101"]:
        raise ErroWebSocket(f"resposta inesperada: {linhas[0]}")
    campos = {linha.split(":", 1)[0].strip().lower(): linha.split(":", 1)[1].strip()
              for linha in linhas[1:] if ":" in linha}
    esperado = base64.b64encode(hashlib.sha1((chave + GUID_RFC6455).encode()).digest()).decode()  # a RFC 6455 manda SHA-1
    if campos.get("sec-websocket-accept") != esperado:
        raise ErroWebSocket("Sec-WebSocket-Accept não confere")
    return sobra


def _trama_do_cliente(opcode, carga, mascara):
    """Trama final, com máscara (obrigatória no cliente) e o tamanho em 7, 16 ou 64 bits."""
    tamanho = len(carga)
    if tamanho < 126:
        cabecalho = bytes([0x80 | opcode, 0x80 | tamanho])
    elif tamanho < 65536:
        cabecalho = bytes([0x80 | opcode, 0x80 | 126]) + tamanho.to_bytes(2, "big")
    else:
        cabecalho = bytes([0x80 | opcode, 0x80 | 127]) + tamanho.to_bytes(8, "big")
    return cabecalho + mascara + bytes(b ^ mascara[i % 4] for i, b in enumerate(carga))


def _ler_trama(buffer):
    """(opcode, fim, carga, bytes usados) da trama no início do buffer, ou None se ainda está incompleta."""
    if len(buffer) < 2:
        return None
    if buffer[1] & 0x80:
        raise ErroWebSocket("o servidor não pode mascarar tramas")
    tamanho, inicio = buffer[1] & 0x7F, 2
    if tamanho in (126, 127):
        bytes_do_tamanho = 2 if tamanho == 126 else 8
        inicio += bytes_do_tamanho
        if len(buffer) < inicio:
            return None
        tamanho = int.from_bytes(buffer[2:inicio], "big")
    if len(buffer) < inicio + tamanho:
        return None
    return buffer[0] & 0x0F, bool(buffer[0] & 0x80), bytes(buffer[inicio:inicio + tamanho]), inicio + tamanho


class ClienteWebSocket:
    def __init__(self, ligacao, mascara_aleatoria, sobra=b""):
        self._ligacao, self._mascara_aleatoria = ligacao, mascara_aleatoria
        self._buffer, self._fragmentos, self._opcode_da_mensagem = bytearray(sobra), b"", OPCODE_TEXTO

    def enviar_texto(self, texto):
        self._enviar(OPCODE_TEXTO, texto.encode("utf-8"))

    def _enviar(self, opcode, carga):
        self._ligacao.sendall(_trama_do_cliente(opcode, carga, self._mascara_aleatoria(4)))

    def receber(self, timeout=None):
        """Próxima mensagem de texto; None se o servidor fechou. TimeoutError se `timeout` passou sem trama
        completa (o que já chegou fica guardado para a chamada seguinte)."""
        self._ligacao.settimeout(timeout)
        while True:
            trama = _ler_trama(self._buffer)
            if trama is None:
                self._ler_mais()
                continue
            opcode, fim, carga, usados = trama
            del self._buffer[:usados]
            if opcode == OPCODE_FECHAR:
                self.fechar()
                return None
            texto = self._tratar(opcode, fim, carga)
            if texto is not None:
                return texto

    def _ler_mais(self):
        pedaco = self._ligacao.recv(65536)
        if not pedaco:
            raise ErroWebSocket("a ligação caiu")
        self._buffer += pedaco

    def _tratar(self, opcode, fim, carga):
        """Ping -> pong; fragmentos juntam-se; devolve o texto completo, ou None se ainda não há."""
        if opcode == OPCODE_PING:
            self._enviar(OPCODE_PONG, carga)
            return None
        if opcode == OPCODE_PONG:
            return None
        if opcode != OPCODE_CONTINUACAO:
            self._fragmentos, self._opcode_da_mensagem = b"", opcode
        self._fragmentos += carga
        if not fim:
            return None
        completo, self._fragmentos = self._fragmentos, b""
        return completo.decode("utf-8") if self._opcode_da_mensagem == OPCODE_TEXTO else None

    def fechar(self):
        """Manda o close (se o socket ainda deixar) e fecha."""
        try:
            self._enviar(OPCODE_FECHAR, b"")
        except OSError:
            pass  # já estava partido: só falta fechar
        self._ligacao.close()
