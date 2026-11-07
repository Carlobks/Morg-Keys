"""Cliente WebSocket mínimo (morg_websocket.py): aperto de mão e tramas da RFC 6455, testado sem rede.

O socket é falso: guarda o que o cliente envia e entrega, pedaço a pedaço, o que o "servidor" diria.
"""

import base64
import hashlib
import importlib
import unittest

from sistema_falso import carregar_bar_helper

carregar_bar_helper()  # põe a pasta do pack no sys.path
morg_websocket = importlib.import_module("morg_websocket")

CHAVE = base64.b64encode(bytes(range(16))).decode()
GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
ACEITE = base64.b64encode(hashlib.sha1((CHAVE + GUID).encode()).digest()).decode()  # a RFC 6455 manda SHA-1


def resposta_http(aceite=ACEITE, estado="101 Switching Protocols"):
    return (f"HTTP/1.1 {estado}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
            f"Sec-WebSocket-Accept: {aceite}\r\n\r\n").encode()


def trama_do_servidor(carga, opcode=1, fim=True):
    """Trama sem máscara (o servidor nunca mascara), com o tamanho em 7, 16 ou 64 bits."""
    cabecalho = bytes([(0x80 if fim else 0) | opcode])
    if len(carga) < 126:
        cabecalho += bytes([len(carga)])
    elif len(carga) < 65536:
        cabecalho += bytes([126]) + len(carga).to_bytes(2, "big")
    else:
        cabecalho += bytes([127]) + len(carga).to_bytes(8, "big")
    return cabecalho + carga


class SocketFalso:
    def __init__(self, *pedacos):
        self.entrada, self.enviados, self.fechado, self.limite = list(pedacos), [], False, "nunca"

    def sendall(self, dados):
        self.enviados.append(bytes(dados))

    def settimeout(self, valor):
        self.limite = valor

    def recv(self, quantos):
        if not self.entrada:
            return b""
        pedaco = self.entrada.pop(0)
        if isinstance(pedaco, Exception):
            raise pedaco
        if len(pedaco) > quantos:
            self.entrada.insert(0, pedaco[quantos:])
            pedaco = pedaco[:quantos]
        return pedaco

    def close(self):
        self.fechado = True


def desmascarar(trama):
    """Lê uma trama do cliente: devolve (opcode, fim, carga) e confirma que veio mascarada."""
    assert trama[1] & 0x80, "o cliente tem de mascarar"
    tamanho, posicao = trama[1] & 0x7F, 2
    if tamanho == 126:
        tamanho, posicao = int.from_bytes(trama[2:4], "big"), 4
    elif tamanho == 127:
        tamanho, posicao = int.from_bytes(trama[2:10], "big"), 10
    mascara = trama[posicao:posicao + 4]
    carga = bytes(b ^ mascara[i % 4] for i, b in enumerate(trama[posicao + 4:posicao + 4 + tamanho]))
    assert len(carga) == tamanho
    return trama[0] & 0x0F, bool(trama[0] & 0x80), carga


def ligar(*pedacos, aceite=ACEITE, estado="101 Switching Protocols"):
    socket_falso = SocketFalso(resposta_http(aceite, estado), *pedacos)
    cliente = morg_websocket.ligar("127.0.0.1", 6123, criar_ligacao=lambda endereco: socket_falso,
                                   chave_aleatoria=lambda n: bytes(range(n)), mascara_aleatoria=lambda n: b"\x01\x02\x03\x04")
    return cliente, socket_falso


class ApertoDeMao(unittest.TestCase):

    def test_pede_a_atualizacao_com_a_chave_e_aceita_a_resposta_certa(self):
        cliente, socket_falso = ligar()
        pedido = socket_falso.enviados[0].decode()
        self.assertTrue(pedido.startswith("GET / HTTP/1.1\r\n"))
        self.assertIn("Host: 127.0.0.1:6123\r\n", pedido)
        self.assertIn("Upgrade: websocket\r\n", pedido)
        self.assertIn("Connection: Upgrade\r\n", pedido)
        self.assertIn(f"Sec-WebSocket-Key: {CHAVE}\r\n", pedido)
        self.assertIn("Sec-WebSocket-Version: 13\r\n", pedido)
        self.assertTrue(pedido.endswith("\r\n\r\n"))
        self.assertFalse(socket_falso.fechado)
        self.assertIsNotNone(cliente)

    def test_resposta_que_chega_aos_bocados(self):
        resposta = resposta_http()
        socket_falso = SocketFalso(resposta[:10], resposta[10:30], resposta[30:])
        morg_websocket.ligar("127.0.0.1", 6123, criar_ligacao=lambda endereco: socket_falso,
                             chave_aleatoria=lambda n: bytes(range(n)))
        self.assertFalse(socket_falso.fechado)

    def test_aceite_errado_fecha_e_recusa(self):
        with self.assertRaises(morg_websocket.ErroWebSocket):
            ligar(aceite="ZXJyYWRv")
        # (o socket falso fica fechado: ver o teste seguinte, que o guarda)

    def test_aceite_errado_fecha_o_socket(self):
        socket_falso = SocketFalso(resposta_http(aceite="ZXJyYWRv"))
        with self.assertRaises(morg_websocket.ErroWebSocket):
            morg_websocket.ligar("127.0.0.1", 6123, criar_ligacao=lambda endereco: socket_falso,
                                 chave_aleatoria=lambda n: bytes(range(n)))
        self.assertTrue(socket_falso.fechado)

    def test_estado_diferente_de_101_recusa(self):
        with self.assertRaises(morg_websocket.ErroWebSocket):
            ligar(estado="200 OK")

    def test_servidor_que_fecha_a_meio_do_aperto_de_mao(self):
        socket_falso = SocketFalso(b"HTTP/1.1 101 Swit")
        with self.assertRaises(ConnectionError):
            morg_websocket.ligar("127.0.0.1", 6123, criar_ligacao=lambda endereco: socket_falso,
                                 chave_aleatoria=lambda n: bytes(range(n)))
        self.assertTrue(socket_falso.fechado)

    def test_o_que_vem_depois_do_aperto_de_mao_fica_para_ler(self):
        socket_falso = SocketFalso(resposta_http() + trama_do_servidor(b"ola"))
        cliente = morg_websocket.ligar("127.0.0.1", 6123, criar_ligacao=lambda endereco: socket_falso,
                                       chave_aleatoria=lambda n: bytes(range(n)))
        self.assertEqual(cliente.receber(), "ola")

    def test_sem_injecao_usa_a_rede_e_o_acaso_do_sistema(self):
        socket_falso = SocketFalso()
        chaves = []

        def criar(endereco):
            chaves.append(endereco)
            return socket_falso
        with self.assertRaises(morg_websocket.ErroWebSocket):  # o servidor falso não responde: 0 bytes
            morg_websocket.ligar("127.0.0.1", 6123, criar_ligacao=criar)
        self.assertEqual(chaves, [("127.0.0.1", 6123)])


class Enviar(unittest.TestCase):

    def enviar(self, texto):
        cliente, socket_falso = ligar()
        socket_falso.enviados.clear()
        cliente.enviar_texto(texto)
        return socket_falso.enviados

    def test_trama_curta_mascarada(self):
        enviados = self.enviar("sub -e window_managed")
        self.assertEqual(len(enviados), 1)
        self.assertEqual(desmascarar(enviados[0]), (1, True, b"sub -e window_managed"))

    def test_trama_de_16_bits(self):
        texto = "a" * 300
        enviados = self.enviar(texto)
        self.assertEqual(enviados[0][1] & 0x7F, 126)
        self.assertEqual(desmascarar(enviados[0]), (1, True, texto.encode()))

    def test_trama_de_64_bits(self):
        texto = "b" * 70000
        enviados = self.enviar(texto)
        self.assertEqual(enviados[0][1] & 0x7F, 127)
        self.assertEqual(desmascarar(enviados[0]), (1, True, texto.encode()))

    def test_acentos_vao_em_utf8(self):
        self.assertEqual(desmascarar(self.enviar("não")[0])[2], "não".encode())

    def test_a_mascara_muda_a_cada_trama(self):
        mascaras = iter([b"\x01\x02\x03\x04", b"\x05\x06\x07\x08"])
        socket_falso = SocketFalso(resposta_http())
        cliente = morg_websocket.ligar("127.0.0.1", 6123, criar_ligacao=lambda endereco: socket_falso,
                                       chave_aleatoria=lambda n: bytes(range(n)), mascara_aleatoria=lambda n: next(mascaras))
        cliente.enviar_texto("x")
        cliente.enviar_texto("x")
        self.assertEqual(socket_falso.enviados[1][2:6], b"\x01\x02\x03\x04")
        self.assertEqual(socket_falso.enviados[2][2:6], b"\x05\x06\x07\x08")


class Receber(unittest.TestCase):

    def test_trama_curta(self):
        cliente, _ = ligar(trama_do_servidor(b'{"a":1}'))
        self.assertEqual(cliente.receber(), '{"a":1}')

    def test_trama_de_16_bits(self):
        carga = ("c" * 300).encode()
        cliente, _ = ligar(trama_do_servidor(carga))
        self.assertEqual(cliente.receber(), "c" * 300)

    def test_trama_de_64_bits(self):
        carga = ("d" * 70000).encode()
        cliente, _ = ligar(trama_do_servidor(carga))
        self.assertEqual(cliente.receber(), "d" * 70000)

    def test_trama_aos_bocados(self):
        trama = trama_do_servidor(b"abcdef")
        cliente, _ = ligar(trama[:1], trama[1:3], trama[3:])
        self.assertEqual(cliente.receber(), "abcdef")

    def test_cabecalho_de_tamanho_cortado_a_meio(self):
        trama = trama_do_servidor(("e" * 300).encode())
        cliente, _ = ligar(trama[:3], trama[3:])
        self.assertEqual(cliente.receber(), "e" * 300)

    def test_duas_tramas_seguidas_no_mesmo_pedaco(self):
        cliente, _ = ligar(trama_do_servidor(b"um") + trama_do_servidor(b"dois"))
        self.assertEqual([cliente.receber(), cliente.receber()], ["um", "dois"])

    def test_mensagem_fragmentada(self):
        cliente, _ = ligar(trama_do_servidor(b"ab", 1, fim=False), trama_do_servidor(b"cd", 0, fim=False),
                           trama_do_servidor(b"ef", 0, fim=True))
        self.assertEqual(cliente.receber(), "abcdef")

    def test_ping_responde_com_pong_e_continua(self):
        cliente, socket_falso = ligar(trama_do_servidor(b"xyz", 9), trama_do_servidor(b"texto"))
        socket_falso.enviados.clear()
        self.assertEqual(cliente.receber(), "texto")
        self.assertEqual(desmascarar(socket_falso.enviados[0]), (10, True, b"xyz"))

    def test_pong_ignora_se(self):
        cliente, socket_falso = ligar(trama_do_servidor(b"", 10), trama_do_servidor(b"texto"))
        socket_falso.enviados.clear()
        self.assertEqual(cliente.receber(), "texto")
        self.assertEqual(socket_falso.enviados, [])

    def test_close_do_servidor_responde_close_e_devolve_none(self):
        cliente, socket_falso = ligar(trama_do_servidor(b"\x03\xe8", 8))
        socket_falso.enviados.clear()
        self.assertIsNone(cliente.receber())
        self.assertEqual(desmascarar(socket_falso.enviados[0])[0], 8)
        self.assertTrue(socket_falso.fechado)

    def test_close_com_o_socket_ja_partido_nao_rebenta(self):
        class Partido(SocketFalso):
            def sendall(self, dados):
                if self.entrada == []:
                    raise ConnectionResetError
                super().sendall(dados)
        socket_falso = Partido(resposta_http(), trama_do_servidor(b"", 8))
        cliente = morg_websocket.ligar("127.0.0.1", 6123, criar_ligacao=lambda endereco: socket_falso,
                                       chave_aleatoria=lambda n: bytes(range(n)))
        self.assertIsNone(cliente.receber())

    def test_ligacao_que_cai_levanta_erro_de_ligacao(self):
        cliente, _ = ligar(trama_do_servidor(b"abc")[:3])
        with self.assertRaises(ConnectionError):
            cliente.receber()

    def test_espera_com_limite_de_tempo_e_nao_perde_o_que_ja_veio(self):
        trama = trama_do_servidor(b"abcdef")
        cliente, socket_falso = ligar(trama[:3], TimeoutError(), trama[3:])
        with self.assertRaises(TimeoutError):
            cliente.receber(timeout=0.05)
        self.assertEqual(socket_falso.limite, 0.05)
        self.assertEqual(cliente.receber(timeout=0.05), "abcdef")

    def test_sem_limite_bloqueia(self):
        cliente, socket_falso = ligar(trama_do_servidor(b"a"))
        cliente.receber()
        self.assertIsNone(socket_falso.limite)

    def test_trama_mascarada_do_servidor_e_recusada(self):
        cliente, _ = ligar(bytes([0x81, 0x80 | 1]) + b"\x00\x00\x00\x00x")
        with self.assertRaises(morg_websocket.ErroWebSocket):
            cliente.receber()

    def test_opcode_binario_e_ignorado(self):
        cliente, _ = ligar(trama_do_servidor(b"\x00\x01", 2), trama_do_servidor(b"texto"))
        self.assertEqual(cliente.receber(), "texto")


class Fechar(unittest.TestCase):

    def test_fechar_manda_close_e_fecha_o_socket(self):
        cliente, socket_falso = ligar()
        socket_falso.enviados.clear()
        cliente.fechar()
        self.assertEqual(desmascarar(socket_falso.enviados[0])[0], 8)
        self.assertTrue(socket_falso.fechado)

    def test_fechar_com_o_socket_partido_nao_rebenta(self):
        class Partido(SocketFalso):
            def sendall(self, dados):
                if len(self.enviados) >= 1:
                    raise BrokenPipeError
                super().sendall(dados)
        socket_falso = Partido(resposta_http())
        cliente = morg_websocket.ligar("127.0.0.1", 6123, criar_ligacao=lambda endereco: socket_falso,
                                       chave_aleatoria=lambda n: bytes(range(n)))
        cliente.fechar()
        self.assertTrue(socket_falso.fechado)


if __name__ == "__main__":
    unittest.main()
