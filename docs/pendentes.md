# Pendentes (por ordem)

Trabalho combinado com o utilizador e ainda não feito. Quando um item começa, ganha plano próprio (ou ADR);
quando acaba, sai daqui. Ordem registada e confirmada pelo dono a 2026-10-31.
Feitos a 2026-10-31: o plano Morg Laws (`morg-laws/plano-01.md`) e o bug do painel "Apps e arranque"; o relatório de erros (`planos/0002-relatorio-de-erros.md`).
Feitos a 2026-11-03/04: a reinstalação sem esconder as janelas (`planos/0005-…`) e o modal dos limites do Claude (`planos/0006-…`).
Desistido pelo dono a 2026-11-07: as frases do arranque por dia do ano (não se fazem).

1. **Guia do Alt+R** (pedido de 2026-10-31): ao entrar no modo `resize`, aparece por baixo da
   data, no topo, um guia curto de como o usar.

2. **Auditoria F1–F7** (`auditoria-2026-10-24.md`): arranque robusto, injeções de gravidade baixa, instalador,
   ferramentas, organização dos docs e páginas (o que não passou para o plano Morg Laws).

3. **Experiência 0001 — cobertura A contra C**, fases 4–6: `experiencias/0001-cobertura-a-vs-c.md`.

4. **Ecrã do jogo em tela cheia** (relatado a 2026-10-25; em curso, pesquisa em `pesquisa/jogos-ecra-inteiro.md`).
   A regra `ignore` do Baldur's Gate 3 pô-lo em ecrã inteiro com os atalhos a funcionar, mas ao trocar de
   workspace o jogo minimiza-se (o DirectX larga o ecrã inteiro exclusivo quando fica tapado). **2.º teste (P5.2,
   feita a 2026-11-07, à espera do teste real do dono):** a regra passou a `set-fullscreen` e o jogo tem de estar
   em "janela sem bordas" (passos em `validacao-manual.md` §11). Depois: a lista automática dos jogos da Steam e um painel
   com atalho (não o `Alt+Shift+I`, que abre o Edge) que mostra o que já foi adicionado e pergunta antes.

5. **Os ~5 s de papel de parede ao entrar (A38).** Diagnóstico com o WPR (como administrador, 1 reinício; passos em
    `pesquisa/arranque-windows.md` §2). Se a causa tiver correção limpa, fase própria.

6. **App da Store já aberta quando entra no painel (caso raro, decidido pelo dono a 2026-11-01: fica para depois).**
   Uma app da Store posta no painel entra no `layout.json` sem processo; o restauro aprende-o pela primeira janela
   nova que aparecer. Se a app já estiver aberta (ex.: reinstalar com o Claude aberto, 2026-10-31 22:50), não
   aparece janela nova, a correção do P2.1 ignora a que já existia, e a app só é colocada no próximo arranque em
   que esteja fechada (ao ligar o PC, 2026-11-01 05:48: "aprendi Claude = claude; ficou no 1"). Depois de aprendido,
   o processo fica no `layout.json` e uma reinstalação mantém-no. Correção possível: ligar a janela à app pelo
   AppUserModelID da Store (`Claude_pzs8sxrjxfjjc!Claude`), com pesquisa antes.

7. **Arrastar abas do Chrome desorienta a arrumação** (bug, 2026-11-03; em curso desde 2026-11-07, a validar com o dono; pesquisa em `pesquisa/arrastar-janelas.md`):
    a issue #1080 do GlazeWM, por resolver na 3.10.1. Animações suaves: o GlazeWM não as tem.

8. **Atualizar o Morg Keys pelo `Alt+Esc, U`** (pedido de 2026-11-03): procura uma versão nova no GitHub e, se
    houver, atualiza sem mais passos. Pede pesquisa antes (verificar o que se descarrega, manter as
    personalizações, reinstalar sem esconder as janelas) e plano próprio.

9. **A medição "fundo à vista sem cortina"** do registo do arranque fica errada quando o ambiente arranca sem
    reiniciar o Explorador (ex.: reinstalar).
