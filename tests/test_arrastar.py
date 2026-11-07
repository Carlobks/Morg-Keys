"""Ajudante `arrastar` (morg_arrastar): a janela criada com o botão do rato carregado fica solta até largar.

A decisão (evento + botão -> comando) é função pura; o ciclo e a entrada recebem a rede, o rato e o tempo
por parâmetro, por isso nada aqui toca no GlazeWM nem no rato reais.
"""

import json
import sys
import unittest

from falsos_windows import Gravador
from sistema_falso import SistemaFalso, carregar_bar_helper

carregar_bar_helper()
ARRASTAR = sys.modules["morg_arrastar"]

ID_A, ID_B = "11111111-aaaa-bbbb-cccc-000000000001", "22222222-aaaa-bbbb-cccc-000000000002"


def evento(id_da_janela, **trocas):
    """Uma mensagem `window_managed` como o GlazeWM 3.10.1 a envia (messageType/eventType/managedWindow)."""
    mensagem = {"messageType": "event_subscription", "success": True, "error": None, "subscriptionId": "s1",
                "data": {"eventType": "window_managed", "managedWindow": {"type": "window", "id": id_da_janela}}}
    mensagem.update(trocas)
    return json.dumps(mensagem)


def resposta_ao_comando(**trocas):
    mensagem = {"messageType": "client_response", "clientMessage": "command", "success": True, "data": None,
                "error": None}
    mensagem.update(trocas)
    return json.dumps(mensagem)


class ClienteFalso:
    """receber() devolve o que está em `chegadas` (texto, None, TimeoutError ou outra exceção a levantar)."""

    def __init__(self, chegadas):
        self.chegadas, self.enviados, self.esperas, self.fechado = list(chegadas), [], [], False

    def enviar_texto(self, texto):
        self.enviados.append(texto)

    def receber(self, timeout=None):
        self.esperas.append(timeout)
        proxima = self.chegadas.pop(0)
        if isinstance(proxima, BaseException):
            raise proxima
        return proxima

    def fechar(self):
        self.fechado = True


class BotaoFalso:
    """Estado do botão a cada pergunta; esgotado, rebenta (o teste não previu mais perguntas)."""

    def __init__(self, *estados):
        self.estados = list(estados)

    def __call__(self):
        return self.estados.pop(0)


class MutexFalso:
    livre = True

    def __init__(self, nome, timeout_ms=2000):
        MutexFalso.nome, MutexFalso.espera = nome, timeout_ms

    def __enter__(self):
        return MutexFalso.livre

    def __exit__(self, *erro):
        return False


class QualJanelaNasceu(unittest.TestCase):
    def test_evento_de_janela_gerida(self):
        self.assertEqual(ARRASTAR.janela_nova(evento(ID_A)), ID_A)

    def test_texto_que_nao_e_json(self):
        self.assertIsNone(ARRASTAR.janela_nova("isto não é json"))

    def test_json_que_nao_e_um_objeto(self):
        self.assertIsNone(ARRASTAR.janela_nova("[1, 2]"))

    def test_resposta_a_um_comando_nao_e_evento(self):
        self.assertIsNone(ARRASTAR.janela_nova(resposta_ao_comando()))

    def test_outro_evento_nao_conta(self):
        outro = {"eventType": "focus_changed", "focusedContainer": {"type": "window", "id": ID_A}}
        self.assertIsNone(ARRASTAR.janela_nova(evento(ID_A, data=outro)))

    def test_data_sem_forma_de_objeto(self):
        self.assertIsNone(ARRASTAR.janela_nova(evento(ID_A, data=None)))

    def test_janela_gerida_sem_forma_de_objeto(self):
        dados = {"eventType": "window_managed", "managedWindow": "estranho"}
        self.assertIsNone(ARRASTAR.janela_nova(evento(ID_A, data=dados)))

    def test_contentor_que_nao_e_janela(self):
        dados = {"eventType": "window_managed", "managedWindow": {"type": "workspace", "id": ID_A}}
        self.assertIsNone(ARRASTAR.janela_nova(evento(ID_A, data=dados)))

    def test_janela_sem_id_ou_com_id_estranho(self):
        for id_estranho in (None, "", 7):
            dados = {"eventType": "window_managed", "managedWindow": {"type": "window", "id": id_estranho}}
            with self.subTest(id=id_estranho):
                self.assertIsNone(ARRASTAR.janela_nova(evento(ID_A, data=dados)))

    def test_id_que_nao_e_um_uuid_nao_vai_para_o_comando(self):
        """O id entra numa linha de comandos separada por espaços: nada de espaços nem de opções à solta."""
        self.assertIsNone(ARRASTAR.janela_nova(evento("1 --centered=true")))


class QueComandoMandar(unittest.TestCase):
    def test_botao_carregado_solta_a_janela(self):
        self.assertEqual(ARRASTAR.comando_ao_aparecer(evento(ID_A), True),
                         f"command --id {ID_A} set-floating --centered=false")

    def test_botao_solto_nao_faz_nada(self):
        self.assertIsNone(ARRASTAR.comando_ao_aparecer(evento(ID_A), False))

    def test_sem_janela_nova_nao_faz_nada_mesmo_com_o_botao_carregado(self):
        self.assertIsNone(ARRASTAR.comando_ao_aparecer(resposta_ao_comando(), True))

    def test_ao_largar_volta_ao_mosaico(self):
        self.assertEqual(ARRASTAR.comando_mosaico(ID_A), f"command --id {ID_A} set-tiling")


class BotaoDoRato(unittest.TestCase):
    def consultar(self, trocados, estados):
        user32 = Gravador("user32", GetSystemMetrics=lambda indice: trocados,
                          GetAsyncKeyState=lambda tecla: estados[tecla])
        return ARRASTAR.botao_principal_carregado(user32), user32

    def test_esquerdo_carregado(self):
        carregado, user32 = self.consultar(0, {0x01: -32767})  # bit mais alto ligado (c_short negativo)
        self.assertTrue(carregado)
        self.assertEqual(user32.de("GetAsyncKeyState"), [(0x01,)])
        self.assertEqual(user32.de("GetSystemMetrics"), [(23,)])  # SM_SWAPBUTTON

    def test_esquerdo_solto(self):
        self.assertFalse(self.consultar(0, {0x01: 0})[0])

    def test_so_o_bit_de_foi_carregado_desde_a_ultima_vez_nao_conta(self):
        self.assertFalse(self.consultar(0, {0x01: 1})[0])

    def test_botoes_trocados_olha_o_direito(self):
        carregado, user32 = self.consultar(1, {0x02: -32768})
        self.assertTrue(carregado)
        self.assertEqual(user32.de("GetAsyncKeyState"), [(0x02,)])


class CicloDoAjudante(unittest.TestCase):
    def correr(self, chegadas, *botao):
        cliente = ClienteFalso(chegadas)
        ARRASTAR.correr(cliente, BotaoFalso(*botao))
        return cliente

    def test_pede_so_os_eventos_de_janela_nova(self):
        cliente = self.correr([None])
        self.assertEqual(cliente.enviados, ["sub -e window_managed"])

    def test_parado_sem_arrasto_espera_sem_limite(self):
        cliente = self.correr([evento(ID_A), None], False)
        self.assertEqual(cliente.esperas, [None, None])
        self.assertEqual(cliente.enviados, ["sub -e window_managed"])

    def test_janela_nova_com_o_botao_carregado_fica_solta_ate_largar(self):
        # evento (botão carregado) -> 50 ms sem nada (ainda carregado) -> 50 ms sem nada (largou) -> fecha
        cliente = self.correr([evento(ID_A), TimeoutError(), TimeoutError(), None],
                              True, True,  # ao chegar: decide + ainda carregado
                              True,  # primeira espera
                              False)  # segunda espera: largou
        self.assertEqual(cliente.enviados[1:], [f"command --id {ID_A} set-floating --centered=false",
                                                f"command --id {ID_A} set-tiling"])
        self.assertEqual(cliente.esperas, [None, 0.05, 0.05, None])

    def test_arrasto_confirma_so_depois_de_largar(self):
        cliente = self.correr([evento(ID_A), TimeoutError(), None], True, True, False)
        self.assertEqual(len(cliente.enviados), 3)  # sub, floating, tiling
        self.assertTrue(cliente.enviados[-1].endswith("set-tiling"))

    def test_janela_nova_com_o_botao_solto_nao_se_mexe(self):
        cliente = self.correr([evento(ID_A), None], False)
        self.assertEqual(cliente.enviados, ["sub -e window_managed"])

    def test_janelas_que_chegam_durante_o_arrasto_largam_todas_juntas(self):
        cliente = self.correr([evento(ID_A), evento(ID_B), None],
                              True, True,  # A: decide + carregado
                              True, True,  # B: decide + carregado
                              )
        self.assertEqual(cliente.enviados[1:3], [f"command --id {ID_A} set-floating --centered=false",
                                                 f"command --id {ID_B} set-floating --centered=false"])
        self.assertEqual(len(cliente.enviados), 3)  # o fim da ligação deixa-as soltas, sem tiling

    def test_largar_manda_o_mosaico_de_cada_uma_e_limpa_a_lista(self):
        cliente = self.correr([evento(ID_A), evento(ID_B), TimeoutError(), TimeoutError(), None],
                              True, True, True, True, False)
        self.assertEqual(cliente.enviados[3:], [f"command --id {ID_A} set-tiling",
                                                f"command --id {ID_B} set-tiling"])
        self.assertEqual(cliente.esperas, [None, 0.05, 0.05, None, None][:len(cliente.esperas)])

    def test_depois_de_largar_volta_a_esperar_sem_limite(self):
        cliente = self.correr([evento(ID_A), TimeoutError(), None], True, True, False)
        self.assertEqual(cliente.esperas, [None, 0.05, None])

    def test_respostas_aos_comandos_sao_ignoradas(self):
        """O erro de um set-tiling a uma janela que o Chrome já destruiu não pára o ajudante."""
        erro = resposta_ao_comando(success=False, error="Window not found")
        cliente = self.correr([evento(ID_A), erro, resposta_ao_comando(), TimeoutError(), None],
                              True, True, True, True, False)
        self.assertEqual(cliente.enviados[-1], f"command --id {ID_A} set-tiling")

    def test_a_ligacao_que_cai_levanta_para_o_arrastar_sair(self):
        cliente = ClienteFalso([ConnectionError("caiu")])
        with self.assertRaises(ConnectionError):
            ARRASTAR.correr(cliente, BotaoFalso())


class ComoOAjudanteArranca(unittest.TestCase):
    def preparar(self, s, ligacoes):
        """`ligacoes`: o que cada tentativa de `ligar` devolve (cliente) ou levanta (exceção)."""
        s.trocar("_NamedMutex", MutexFalso)
        MutexFalso.livre = True
        self.tentativas, self.dormidas = [], []

        def ligar(host, porta):
            self.tentativas.append((host, porta))
            proxima = ligacoes.pop(0)
            if isinstance(proxima, BaseException):
                raise proxima
            return proxima
        return ligar

    def arrastar(self, ligar):
        user32 = Gravador("user32", GetSystemMetrics=0, GetAsyncKeyState=0)
        ARRASTAR.arrastar(ligar=ligar, user32=user32, dormir=self.dormidas.append)

    def test_liga_ao_ipc_local_do_glazewm_e_fecha_no_fim(self):
        with SistemaFalso() as s:
            cliente = ClienteFalso([None])
            self.arrastar(self.preparar(s, [cliente]))
            self.assertEqual(self.tentativas, [("127.0.0.1", 6123)])
            self.assertEqual(cliente.enviados, ["sub -e window_managed"])
            self.assertTrue(cliente.fechado)
            self.assertEqual(MutexFalso.nome, "Local\\MorgArrastar")
            self.assertEqual(MutexFalso.espera, 0)  # não espera pelo outro: sai logo

    def test_outro_ajudante_ja_corre_nao_liga(self):
        with SistemaFalso() as s:
            ligar = self.preparar(s, [])
            MutexFalso.livre = False
            self.arrastar(ligar)
            self.assertEqual(self.tentativas, [])

    def test_glazewm_ainda_a_arrancar_tenta_de_novo(self):
        with SistemaFalso() as s:
            cliente = ClienteFalso([None])
            self.arrastar(self.preparar(s, [ConnectionRefusedError(), TimeoutError(), cliente]))
            self.assertEqual(len(self.tentativas), 3)
            self.assertEqual(self.dormidas, [ARRASTAR.PAUSA_ENTRE_TENTATIVAS] * 2)
            self.assertTrue(cliente.fechado)

    def test_desiste_depois_de_todas_as_tentativas(self):
        with SistemaFalso() as s:
            falhas = [ConnectionRefusedError()] * ARRASTAR.TENTATIVAS_DE_LIGACAO
            self.arrastar(self.preparar(s, falhas))
            self.assertEqual(len(self.tentativas), ARRASTAR.TENTATIVAS_DE_LIGACAO)
            self.assertEqual(len(self.dormidas), ARRASTAR.TENTATIVAS_DE_LIGACAO - 1)

    def test_ligacao_que_cai_a_meio_acaba_sem_erro_e_fecha(self):
        with SistemaFalso() as s:
            cliente = ClienteFalso([ConnectionResetError("caiu")])
            self.arrastar(self.preparar(s, [cliente]))
            self.assertTrue(cliente.fechado)

    def test_o_helper_nunca_toca_no_rato_real_quando_nao_ha_janela_nova(self):
        with SistemaFalso() as s:
            user32 = Gravador("user32")  # qualquer chamada rebenta
            cliente = ClienteFalso([resposta_ao_comando(), None])
            ligar = self.preparar(s, [cliente])
            ARRASTAR.arrastar(ligar=ligar, user32=user32, dormir=self.dormidas.append)
            self.assertEqual(user32.chamadas, [])


if __name__ == "__main__":
    unittest.main()
