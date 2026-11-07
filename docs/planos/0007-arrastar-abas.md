# Plano 0007: arrastar abas sem a arrumação saltar (2026-11-07)

## Contexto

Ao arrastar uma aba do Chrome para fora, o GlazeWM mete a janela nova no mosaico 0,24 s depois de
ela aparecer, com o botão do rato ainda carregado, e tudo se rearruma várias vezes. É a issue #1080, confirmada
com o dono a 2026-11-07. A pesquisa está em `docs/pesquisa/arrastar-janelas.md`.

## Decisão do dono (A, mosaico ao largar)

Enquanto se arrasta, a janela nova fica solta e nada se mexe; ao
largar, entra no mosaico de uma vez.

## Como

Um ajudante sempre ligado, `bar_helper.py arrastar`, arrancado pelos `startup_commands` do GlazeWM.
1. Liga-se ao WebSocket do GlazeWM (`127.0.0.1:6123`) e pede `sub -e window_managed`. Fica à espera sem gastar
   CPU.
2. A cada janela nova, se o botão principal do rato estiver carregado (`GetAsyncKeyState`, com os botões trocados
   tidos em conta), manda `command --id <id> set-floating --centered=false`.
3. Enquanto o botão estiver carregado, vê-o a cada 50 ms. Ao largar, manda `command --id <id> set-tiling` (o
   erro de uma janela que já não existe ignora-se).
4. Quando o GlazeWM fecha, a ligação cai e o ajudante sai. Só pode haver um ajudante a correr de cada vez.

## Ficheiros

- `morg_websocket.py` (novo): o cliente WebSocket mínimo, só com a biblioteca padrão (aperto de mão e tramas
  RFC 6455), testado sem rede;
- `morg_arrastar.py` (novo): a decisão (evento + botão → comandos) e o ciclo, com a rede e o rato injetados; a
  cola com o `ctypes` fica fina, com o motivo da exclusão da cobertura e o passo em `docs/validacao-manual.md`;
- `bar_helper.py`: o subcomando `arrastar` na docstring e no `COMANDOS`;
- `2-configuracao/glzr/glazewm/config.yaml`: a linha nova nos `startup_commands`;
- testes em `tests/`, estragos em `scripts/estragos.py`, changelog (Corrigido), armadilha se aparecer alguma.

## Fora do escopo

As animações; mudar o GlazeWM; regras por app (vale para qualquer janela nova criada com o
botão carregado).

## Passos (cada um com teste vermelho antes)

- [ ] 7.1 `morg_websocket.py` e testes.
- [ ] 7.2 `morg_arrastar.py` (decisão e ciclo) e testes.
- [ ] 7.3 Subcomando, `startup_commands`, estragos, docs; `testar.ps1` verde.
- [ ] 7.4 Teste do dono: arrastar abas do Chrome sem pausa, depois de reinstalar.

## Prova

Testes vermelhos e depois verdes, cobertura a 100 %, estragos todos apanhados e o teste do dono. O teste
mede também o risco que fica: o `window_managed` chega depois de o GlazeWM já ter arrumado a janela, por isso pode
ficar **um** salto curto em vez de muitos.
