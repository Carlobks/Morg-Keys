// Partilhado pelo guia e pelo painel (comum.mjs): pré-visualização, origem da animação, filtro e ícones.
// drawIcons corre com um DOM falso mínimo (fontes, canvas para medir e SVG), sem navegador.
import assert from 'node:assert/strict';
import { test } from 'node:test';
import {
  comecaAProcurar, drawIcons, ePreVisualizacao, origemDaChavena,
} from '../2-configuracao/glzr/zebar/omarchy-catppuccin/comum/comum.mjs';

test('ePreVisualizacao: file: ou ?preview; no Zebar não', () => {
  assert.equal(ePreVisualizacao({ protocol: 'file:', search: '' }), true);
  assert.equal(ePreVisualizacao({ protocol: 'http:', search: '?preview' }), true);
  assert.equal(ePreVisualizacao({ protocol: 'http:', search: '?a=1&preview=1' }), true);
  assert.equal(ePreVisualizacao({ protocol: 'tauri:', search: '' }), false);
});

test('origemDaChavena: chávena 72 px antes do meio, posição física a dividir pela escala', () => {
  assert.deepEqual(origemDaChavena(1920, { x: 300, y: 80 }, 1), { ox: '588px', oy: '-66px' });
  assert.deepEqual(origemDaChavena(1920, { x: 600, y: 160 }, 2), { ox: '588px', oy: '-66px' });
  assert.deepEqual(origemDaChavena(1365, { x: 0, y: 0 }, 0), { ox: '611px', oy: '14px' });  // escala 0 = 1; meio arredondado
});

test('comecaAProcurar: só teclas de texto, sem Ctrl/Alt e fora do filtro', () => {
  assert.equal(comecaAProcurar({ key: 'a' }, false), true);
  assert.equal(comecaAProcurar({ key: 'a' }, true), false);
  assert.equal(comecaAProcurar({ key: 'a', ctrlKey: true }, false), false);
  assert.equal(comecaAProcurar({ key: 'a', altKey: true }, false), false);
  assert.equal(comecaAProcurar({ key: 'Enter' }, false), false);
});

// DOM falso: o canvas mede o ícone com uma caixa de 12 px de largura (2 a 14) e 12 de altura (-10 a 2).
function domFalso({ fonteFalha = false, icones = [] } = {}) {
  const no = tag => ({
    tag, attrs: {}, style: {}, filhos: [], textContent: '',
    setAttribute(k, v) { this.attrs[k] = String(v); },
    appendChild(filho) { this.filhos.push(filho); },
  });
  const medidas = { actualBoundingBoxLeft: 2, actualBoundingBoxRight: 14, actualBoundingBoxAscent: 10, actualBoundingBoxDescent: 2 };
  globalThis.document = {
    fonts: { load: async () => { if (fonteFalha) throw new Error('sem fonte'); } },
    createElement: () => ({ getContext: () => ({ font: '', measureText: () => medidas }) }),
    createElementNS: (_ns, tag) => no(tag),
    querySelectorAll: () => icones,
  };
  globalThis.getComputedStyle = () => ({ fontSize: '18px', color: 'red' });
}

const icone = offsetWidth => ({
  offsetWidth, dataset: { icon: '983870' }, desenho: null, tirado: null,
  replaceChildren(svg) { this.desenho = svg; },
  removeAttribute(nome) { this.tirado = nome; },
});

test('drawIcons: SVG do tamanho da caixa, texto centrado pelo desenho real, sem data-icon depois', async () => {
  const largo = icone(30);
  const semLargura = icone(0);
  domFalso();
  await drawIcons({ querySelectorAll: () => [largo, semLargura] }, 20);
  assert.deepEqual(largo.desenho.attrs, { width: '30', height: '30' });
  assert.equal(largo.desenho.style.display, 'block');
  const texto = largo.desenho.filhos[0];
  assert.deepEqual(texto.attrs, { x: '9', y: '19', 'font-family': 'JetBrainsMono NF', 'font-size': '18px', fill: 'red' });
  assert.equal(texto.textContent, String.fromCodePoint(983870));
  assert.equal(largo.tirado, 'data-icon');
  assert.deepEqual(semLargura.desenho.attrs, { width: '20', height: '20' });  // escondido: usa o tamanho dado
});

test('drawIcons: por omissão procura em todo o documento, 24 px; desenha mesmo sem a fonte carregada', async () => {
  const semLargura = icone(0);
  domFalso({ fonteFalha: true, icones: [semLargura] });
  await drawIcons();
  assert.deepEqual(semLargura.desenho.attrs, { width: '24', height: '24' });
  assert.equal(semLargura.desenho.filhos[0].attrs.x, '6');
});
