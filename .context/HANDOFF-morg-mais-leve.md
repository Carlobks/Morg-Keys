# Handoff: Morg Keys mais leve (plano 0008) e o que falta a seguir

Para retomar numa sessão nova. Confirme o estado no repositório (`git log --oneline -8`, `git status --short -uall`)
antes de confiar neste ficheiro. Modelo: skill `orquestrando-sessoes` §3. Parámos a 2026-11-10 a pedido do dono.

## Objetivo

Tirar ao Morg Keys o peso que não serve para nada, sem mudar o que o dono vê. A medição de 2026-11-10
(`docs/pesquisa/peso-do-morg-keys.md`) mostrou que, parado, gasta ~614 MB (quase tudo do Zebar/WebView2) e ~0 % de
CPU, com dois defeitos: páginas do Zebar abertas duas vezes no arranque do PC e a chávena da barra a lançar um
Python a cada 5 s. Plano: `docs/planos/0008-morg-mais-leve.md` (o original está na aba Plano do Claude).

## Estado verificado (2026-11-10, ramo `exp/a`)

| O quê | Commits | Estado |
|---|---|---|
| Plano 0007, arrastar abas do Chrome | `e762026`..`40a328b`, `bf30da1` | Testado pelo dono e **enviado** |
| Pesquisa do peso | `a685af0` | **Enviada** |
| 8.1–8.2 um só `zebar startup` no arranque do PC | `198b58b` | Local, sem push |
| 8.3 chávena com `morg_acordado_estado.py` | `559b87e` | Local, sem push |
| 8.4 plano, changelog, estragos, passo manual §13 | `d7f2665` | Local, sem push |

- `testar.ps1` verde, cobertura a 100 %, estragos 146/146 (corrida da sessão do plano 0008). Revisto pela sessão-mãe:
  os testes do plano (`test_acordado_estado`, `test_arranque_sem_duplicados`, `test_arranque`, 17 do
  `bar-logica.test.mjs`) passam.
- **Não verificado:** o ambiente real (não se arranca daqui) e o passo 8.5.

## Decisões

- **Defeito 1:** quem abre as páginas é só o 1.º `startup_commands` do GlazeWM. O `boot` (`morg_arranque.py`)
  deixou de pedir `zebar startup` e ficou só com o passo de progresso "Barra". Dois pedidos em corrida faziam o
  `apps` e o `limites` abrir a dobrar. Custo: a barra aparece ~1 s mais tarde. Se o GlazeWM não arrancar, também
  não há barra (antes havia).
- **Defeito 2:** a chávena pergunta ao `morg_acordado_estado.py` (só `ctypes`, sem importar o pack). Faz-no ao
  carregar, quando o modo `sistema` fecha (`vigiaSistema`/`sistemaFechou` em `bar-logica.mjs`, porque o atalho
  `Alt+Esc, I` muda o estado sem passar pela barra) e de 60 em 60 s, como rede. Clicar continua a usar o
  `bar_helper.py awake toggle`. O nome do mutex é igual ao do `morg_acordado.py`, e um teste confirma-o.
- O dono prefere que a implementação corra numa sessão a frio, com o Sonnet 5.5 médio. A sessão-mãe revê.
- Títulos das sessões no formato `ESTADO | MORG-KEYS · assunto` (regra do Morg-laws, `orquestrando-sessoes` §6).

## Descartado

- Juntar as páginas numa só ou deixar de as pré-carregar: poupava ~30 MB cada, mas abrir ficava lento.
- `MemoryUsageTargetLevel` e a memória da interface do próprio Zebar (~110 MB): só mudando o Zebar (Rust).
- Chamar o `pythonw.exe` diretamente no ajudante do arrastar: poupa 1,5 MB e o caminho muda quando o Python é
  atualizado.
- O `setInterval` de 200 ms da `sistema`: 0,007 % do PC.

## Próximos passos

0. **Feito a 2026-11-10:** 8.5 depois de reinstalar (cada página 1×, 0 Python novos em 60 s, chávena certa) e
   push do `exp/a`. Falta só ver as janelas depois de um **reinício do PC** (o caminho do `boot`). Pendente novo:
   o `Alt+Esc, I` não aparece no painel do `Alt+Esc` (`docs/pendentes.md` item 7).
1. **8.5, o teste do dono (original):** reinstalar e reiniciar o PC. A sessão conta as janelas do Zebar por página (cada uma
   1×; antes, `apps` e `limites` ×2) com um script só de leitura no scratchpad. Conta também os processos
   Python num minuto (antes ~24, agora ~2). O dono vê a chávena mudar pelo clique e pelo `Alt+Esc, I`. Passo
   em `docs/validacao-manual.md` §13.
2. Com o "sim" do dono: push do `exp/a` (`198b58b`, `559b87e`, `d7f2665` e este handoff).
3. Ainda por fazer:
   - o teste do dono no BG3 (P5.2, já enviada);
   - juntar o `exp/a` ao `main` (decisão do dono);
   - o resto por ordem na aba Plano e em `docs/pendentes.md`: a lista dos jogos da Steam, o `Alt+Esc, U`, o guia
     do `Alt+R`, F1–F7, a experiência 0001, a A38, a etiqueta "erro" e o workflow no `main`.

**Cuidados:** Regra n.º 1 (A2): o hook recusa comandos que tenham o nome do executável do Zebar ou do GlazeWM;
medir com scripts `.ps1` no scratchpad, corridos com `powershell -NoProfile -File`. O `estragos.py` leva
~10 min e mexe nos ficheiros do pack: enquanto corre, não se edita nem se commita.
