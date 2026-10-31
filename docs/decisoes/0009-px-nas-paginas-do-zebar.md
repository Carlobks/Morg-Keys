# 0009 — Tamanhos em `px` nas páginas do Zebar (a regra do `rem` não se aplica)

- **Estado:** aceite (2026-10-31, ML12 do plano Morg Laws). Confirma-se no teste real do dono com a escala do
  Windows a 125 %.
- **Contexto:** a skill `desenhando-telas` (Morg Laws) pede tamanhos em `rem`, nunca em `px` fixo, "para respeitar
  o tamanho que a pessoa escolhe". Num navegador isso é o tamanho de letra que a pessoa define nas definições dele,
  e o `rem` segue-o. As páginas do Morg Keys não correm num navegador: são widgets do Zebar em WebView2.
  - Ninguém escolhe o tamanho de letra de uma página do Zebar: não há definição de letra no WebView2 do Zebar, por
    isso a raiz fica sempre nos 16 px de omissão e `1rem` é sempre igual a `16px`.
  - A escala do Windows (100 %, 125 %, 150 %) já chega às páginas: o WebView2 multiplica cada `px` de CSS pelo
    `devicePixelRatio`, tal como faria com o `rem`.
  - A barra é medida ao pixel: o preset do `zpack.json` dá-lhe `30px` de altura, e os ícones (20 px), o texto
    (12 px) e os espaços foram acertados contra essa altura e contra as impressões digitais da fase 2c da
    experiência 0001.
- **Decisão:** as páginas do pack ficam em `px`. A regra do `rem` não se aplica aos widgets do Zebar: trocar daria
  os mesmos tamanhos (porque `1rem` é sempre `16px`) com mais contas e mais risco de partir o acerto da barra.
- **Consequências:**
  - O que a regra quer proteger (a pessoa que precisa de letra maior) vem da escala do Windows, que as páginas já
    seguem. A opção "Tamanho do texto" da Acessibilidade do Windows não foi medida aqui: se o teste real mostrar que
    o WebView2 a segue em `rem` e não em `px`, esta ADR revê-se.
  - Uma página que um dia corra num navegador a sério (fora do Zebar) volta à regra do `rem`.
  - Os `!important` do bloco `prefers-reduced-motion` (ML12) seguem o mesmo motivo da ADR 0008: têm de ganhar a
    qualquer regra de animação acima.
