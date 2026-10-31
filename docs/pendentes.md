# Pendentes (por ordem)

Trabalho combinado com o utilizador e ainda não feito. Quando um item começa, ganha plano próprio (ou ADR);
quando acaba, sai daqui. Ordem registada e confirmada pelo dono a 2026-10-31.

1. **Plano Morg Laws, ML12–ML15** (ML0–ML11b feitas): `morg-laws/plano-01.md`.

2. **Bug do painel "Apps e arranque" (Alt+Esc, C)** (relatado a 2026-10-31). Auditar antes de
   corrigir, com um teste que falha por sintoma:
   - ao ligar o PC, o Claude abre no workspace 5 sem estar configurado para isso;
   - as apps postas no arranque trocam de workspace depois de fechar o painel;
   - `Alt+Esc, G` (gravar arranjo) faz o som de erro do Windows e não mostra nada.

3. **Relatório de erros** (pedido de 2026-10-31). Hoje um erro não deixa um registo que sirva
   para corrigir.
   - Pesquisa primeiro, guardada em `pesquisa/`: o que um relatório de erro tem de levar, segundo a documentação
     oficial de grandes empresas e normas (ISO, IETF ou parecidas).
   - Depois: um popup com o erro, ligado por omissão e desligável. O utilizador escolhe onde guardar o relatório,
     para o juntar a uma issue no GitHub sem dados pessoais a mais.

4. **Frases do arranque** (combinado a 2026-10-31):
   - uma por dia do ano, a repetir desde o início quando acabam;
   - 7 frases novas (fontes: pensador.com e capricho.abril.com.br), como vieram e só com a obra quando a
     personagem não está confirmada;
   - o instalador pergunta (S/N) se troca o `frases.txt` do PC quando o novo é diferente.

5. **Modal dos limites do Claude** (combinado a 2026-10-31): o clique esquerdo no ✻ da barra deixa de abrir a página
   de uso e abre um modal pequeno para pôr à mão, com o rato ou o teclado, o % das 5 h, o % da semana e a hora
   do próximo reset das 5 h (para quem não usa o Claude Code no terminal).

6. **Guia do Alt+R** (pedido de 2026-10-31): ao entrar no modo `resize`, aparece por baixo da
   data, no topo, um guia curto de como o usar.

7. **Auditoria F1–F7** (`auditoria-2026-10-24.md`): arranque robusto, injeções de gravidade baixa, instalador,
   ferramentas, organização dos docs e páginas (o que não passou para o plano Morg Laws).

8. **Experiência 0001 — cobertura A contra C**, fases 4–6: `experiencias/0001-cobertura-a-vs-c.md`.

9. **Jogos em ecrã inteiro não funcionam (relatado pelo utilizador, 2026-10-25).** Ao abrir um jogo em ecrã inteiro,
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

10. **Os ~5 s de papel de parede ao entrar (A38).** Diagnóstico com o WPR (como administrador, 1 reinício; passos em
    `pesquisa/arranque-windows.md` §2). Se a causa tiver correção limpa, fase própria.
