# Plano 0008: Morg mais leve (2026-11-10)

## Contexto

Duas fugas de peso medidas no PC do dono: (1) as páginas do Zebar abriam duas vezes (apps ×2, limites ×2,
cerca de 60 MB), porque o `boot` e o primeiro `startup_commands` do GlazeWM lançavam ambos o arranque do Zebar;
(2) a chávena da barra corria o `bar_helper.py` inteiro (importa metade do pack) 12 vezes por minuto.
A medição está em `docs/pesquisa/` (peso do Morg Keys). Aprovado pelo dono a 2026-11-10.

## Passos

- [x] 8.1 Teste vermelho: o `boot` não lança o arranque do Zebar (só o GlazeWM o faz).
- [x] 8.2 Corrigir o `morg_arranque.py` (mantém a etapa "barra" do progresso) e o comentário do `config.yaml`.
- [x] 8.3 `morg_acordado_estado.py` (só `ctypes`, abre o mutex `Local\OmarchyAwakeAlive`); a barra pergunta ao
  carregar, ao clicar, quando o modo `sistema` fecha (`vigiaSistema`) e a cada 60 s.
- [x] 8.4 Estragos novos todos apanhados, `testar.ps1` verde, changelog, plano, passo manual.
- [x] 8.5 Teste do dono: reiniciar, contar as janelas do Zebar e ver a chávena (clique e atalho). 2026-11-10,
  depois de reinstalar (sem reiniciar o PC): cada página 1×, 0 processos Python novos em 60 s, chávena certa pelo
  clique e pelo `Alt+Esc, I`. O caminho do arranque do PC fica por ver no próximo reinício.

## Fora do escopo

Juntar ou tirar páginas pré-carregadas; a memória da interface do Zebar; usar o `pythonw.exe` direto no
`arrastar`; o temporizador de 200 ms do `sistema`.

## Prova

Testes vermelhos e depois verdes, cobertura a 100 %, estragos novos todos apanhados, e o teste do dono (8.5):
depois de reiniciar, cada página do Zebar aparece uma só vez (bar, guia, sistema, apps, limites, splash) e a chávena
muda com o clique e com o atalho `Alt+Esc, I` (até 1 s depois de sair do modo).
