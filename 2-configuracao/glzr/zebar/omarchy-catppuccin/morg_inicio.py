"""Hora a que o Python começou a correr o código do Morg Keys (o bar_helper.py importa-o primeiro).

Só serve a medição do arranque (morg_arranque._boot_timing_log): separa o tempo do próprio Python a
arrancar do tempo a carregar os módulos morg_*.py.
"""

import time

T_INICIO = time.time()
