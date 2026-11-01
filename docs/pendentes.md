# Pendentes (por ordem)

Trabalho combinado com o utilizador e ainda não feito. Quando um item começa, ganha plano próprio (ou ADR);
quando acaba, sai daqui. Ordem registada e confirmada pelo dono a 2026-10-31.
Feitos a 2026-10-31: o plano Morg Laws (`morg-laws/plano-01.md`) e o bug do painel "Apps e arranque"; o relatório de erros (`planos/0002-relatorio-de-erros.md`).

1. **Frases do arranque** (combinado a 2026-10-31):
   - uma por dia do ano, a repetir desde o início quando acabam;
   - 7 frases novas (fontes: pensador.com e capricho.abril.com.br), como vieram e só com a obra quando a
     personagem não está confirmada;
   - o instalador pergunta (S/N) se troca o `frases.txt` do PC quando o novo é diferente.

2. **Modal dos limites do Claude** (combinado a 2026-10-31): o clique esquerdo no ✻ da barra deixa de abrir a página
   de uso e abre um modal pequeno para pôr à mão, com o rato ou o teclado, o % das 5 h, o % da semana e a hora
   do próximo reset das 5 h (para quem não usa o Claude Code no terminal).

3. **Guia do Alt+R** (pedido de 2026-10-31): ao entrar no modo `resize`, aparece por baixo da
   data, no topo, um guia curto de como o usar.

4. **Auditoria F1–F7** (`auditoria-2026-10-24.md`): arranque robusto, injeções de gravidade baixa, instalador,
   ferramentas, organização dos docs e páginas (o que não passou para o plano Morg Laws).

5. **Experiência 0001 — cobertura A contra C**, fases 4–6: `experiencias/0001-cobertura-a-vs-c.md`.

6. **Jogos em ecrã inteiro não funcionam (relatado pelo utilizador, 2026-10-25).** Ao abrir um jogo em ecrã inteiro,
   o Morg Keys obriga-o a ficar em janela; o jogo recusa e fica minimizado. Hoje, para jogar em ecrã inteiro, é
   preciso desinstalar o Morg Keys. **Estudar antes de mexer:**
   - que tipo de ecrã inteiro é: exclusivo (DirectX/Vulkan) ou janela sem bordas;
   - quem força: as regras `window_rules` / `float` / `fullscreen` do `config.yaml`, o GlazeWM em si, ou os
     nossos ajudantes (restauro de janelas, `uncloak.ps1`, painel, foco do WebView2);
   - o que dizem a documentação e as issues do GlazeWM sobre jogos (`ignore`, `fullscreen`, `shown_on_fullscreen`
     da barra, pausar o gestor de janelas);
   - como o Omarchy/Hyprland trata o mesmo caso.
   Testar com 2 ou 3 jogos (um exclusivo, um sem bordas) e anotar o que acontece em cada um. A solução tem de
   ser automática ou um atalho simples (ex.: pausar o gestor de janelas e esconder a barra), nunca desinstalar.

7. **Os ~5 s de papel de parede ao entrar (A38).** Diagnóstico com o WPR (como administrador, 1 reinício; passos em
    `pesquisa/arranque-windows.md` §2). Se a causa tiver correção limpa, fase própria.

8. **App da Store já aberta quando entra no painel (caso raro, decidido pelo dono a 2026-11-01: fica para depois).**
   Uma app da Store posta no painel entra no `layout.json` sem processo; o restauro aprende-o pela primeira janela
   nova que aparecer. Se a app já estiver aberta (ex.: reinstalar com o Claude aberto, 2026-10-31 22:50), não
   aparece janela nova, a correção do P2.1 ignora a que já existia, e a app só é colocada no próximo arranque em
   que esteja fechada (ao ligar o PC, 2026-11-01 05:48: "aprendi Claude = claude; ficou no 1"). Depois de aprendido,
   o processo fica no `layout.json` e uma reinstalação mantém-no. Correção possível: ligar a janela à app pelo
   AppUserModelID da Store (`Claude_pzs8sxrjxfjjc!Claude`), com pesquisa antes.
