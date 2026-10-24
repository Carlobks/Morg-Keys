// Partilhado pelo guia (Alt+K) e pelo painel "Apps e arranque" (Alt+Esc, C).
// Sem DOM ao importar: as funções puras testam-se com node --test (tests/*.test.mjs).

export const esc = s => String(s).replace(/[&<>"']/g, c => `&#${c.charCodeAt(0)};`);

// Palavras especiais do apps.txt (as mesmas do SPECIAL_APPS do morg_atalhos.py).
export const SPECIAL = {
  terminal: 'Terminal',
  'claude-code': 'Claude Code no terminal',
  explorador: 'Explorador de ficheiros',
  explorer: 'Explorador de ficheiros',
};

// Texto da direita do apps.txt -> nome a mostrar ("web: https://www.youtube.com" -> "youtube.com").
export function appLabel(value) {
  const v = String(value).trim();
  if (SPECIAL[v.toLowerCase()]) return SPECIAL[v.toLowerCase()];
  if (/^web:/i.test(v)) {
    try { return new URL(v.slice(4).trim()).hostname.replace(/^www\./, ''); } catch { return v; }
  }
  return v.split(/[\\/]/).pop().replace(/\.exe$/i, '');
}

// No navegador (file: ou ?preview) as páginas são normais (pré-visualização); no Zebar ligam-se a ele.
export const ePreVisualizacao = loc => loc.protocol === 'file:' || new URLSearchParams(loc.search).has('preview');

// Origem da animação de abrir/fechar: o centro da chávena da barra (à esquerda do relógio, 72 px antes
// do meio, 14 px abaixo do topo) relativo a esta janela. A posição da janela vem em px físicos; a
// chávena e o CSS estão em px lógicos (escala 0 ou em falta = 1).
export function origemDaChavena(larguraDoEcra, pos, escala) {
  const s = escala || 1;
  return { ox: `${Math.round(larguraDoEcra / 2) - 72 - pos.x / s}px`, oy: `${14 - pos.y / s}px` };
}

// Escrever em qualquer lado começa a procurar: uma tecla de texto, sem Ctrl/Alt, fora do filtro.
export const comecaAProcurar = (e, noFiltro) => e.key.length === 1 && !noFiltro && !e.ctrlKey && !e.altKey;

// Ícones centrados a sério: na fonte "JetBrainsMono NF" cada ícone é mais largo do que a
// célula e fica desviado, por isso mede-se o desenho real. Desenha-se em SVG e não em canvas:
// o canvas do WebView2 do Zebar saía às vezes com ícones estragados ou vazios; texto vetorial
// desenha-se como a barra (sempre certo). A origem do texto fica onde o desenho real fica centrado.
export async function drawIcons(root = document, tamanho = 24) {
  try { await document.fonts.load('16px "JetBrainsMono NF"'); } catch {}
  for (const el of root.querySelectorAll('.ico[data-icon]')) {
    const size = el.offsetWidth || tamanho;
    const css = getComputedStyle(el);
    const mctx = document.createElement('canvas').getContext('2d');
    mctx.font = `${css.fontSize} "JetBrainsMono NF"`;
    const ch = String.fromCodePoint(Number(el.dataset.icon));
    const m = mctx.measureText(ch);
    const NS = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(NS, 'svg');
    svg.setAttribute('width', size);
    svg.setAttribute('height', size);
    svg.style.display = 'block';
    const tx = document.createElementNS(NS, 'text');
    tx.setAttribute('x', size / 2 - (m.actualBoundingBoxRight - m.actualBoundingBoxLeft) / 2);
    tx.setAttribute('y', size / 2 - (m.actualBoundingBoxDescent - m.actualBoundingBoxAscent) / 2);
    tx.setAttribute('font-family', 'JetBrainsMono NF');
    tx.setAttribute('font-size', css.fontSize);
    tx.setAttribute('fill', css.color);
    tx.textContent = ch;
    svg.appendChild(tx);
    el.replaceChildren(svg);
    el.removeAttribute('data-icon');
  }
}
