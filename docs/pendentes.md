# Pendentes (por ordem)

Trabalho combinado com o utilizador e ainda não feito. Quando um item começa, ganha plano próprio (ou ADR);
quando acaba, sai daqui.

1. **Experiência 0001 — cobertura A contra C** (em curso): `experiencias/0001-cobertura-a-vs-c.md`.

A fazer agora, no `exp/a`, antes da fase 4 da experiência (pedido de 2026-10-24). Já feitos: correções
pequenas, bateria na barra e quota do Claude (via oficial + `claude = esconder`; pesquisa em
`pesquisa/quota-claude.md`). Já feito também: o piscar na passagem cortina → animação e o ecrã de boas-vindas (escurecer, saudação, hora, frase do dia).

2. **Jogos em ecrã inteiro não funcionam (relatado pelo utilizador, 2026-10-25).** Ao abrir um jogo em ecrã inteiro,
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

3. **Os ~5 s de papel de parede ao entrar (A38).** Diagnóstico com o WPR (como administrador, 1 reinício; passos em `pesquisa/arranque-windows.md` §2). Se a causa tiver correção limpa, fase própria.

