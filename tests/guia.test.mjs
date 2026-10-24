// Guia de atalhos (Alt+K): tabela, teclas e linhas do apps.txt (guia-logica.mjs).
import assert from 'node:assert/strict';
import { test } from 'node:test';
import {
  columnsHtml, keysHtml, parseApps, SECTIONS, sectionHtml,
} from '../2-configuracao/glzr/zebar/omarchy-catppuccin/guia/guia-logica.mjs';

test('keysHtml: "+" separa teclas, "|" separa alternativas, "Alt++" é a tecla +', () => {
  assert.equal(keysHtml('Alt+W|Alt+Q'), '<kbd>Alt</kbd><kbd>W</kbd><span class="or">ou</span><kbd>Alt</kbd><kbd>Q</kbd>');
  assert.equal(keysHtml('Alt++'), '<kbd>Alt</kbd><kbd>+</kbd>');
  assert.equal(keysHtml('Alt+Shift+-'), '<kbd>Alt</kbd><kbd>Shift</kbd><kbd>-</kbd>');
  assert.equal(keysHtml('<b>'), '<kbd>&#60;b&#62;</kbd>');
});

test('parseApps: ignora comentários e linhas sem "="; normaliza as teclas; usa o nome a mostrar', () => {
  const texto = '# comentário\r\n# Alt+Q = linha desligada\r\n\r\nAlt + Shift + B = Google Chrome\nlixo\nAlt+Y = web: https://www.youtube.com\nAlt+X = a=b';
  assert.deepEqual(parseApps(texto), [
    ['Google Chrome', 'Alt+Shift+B'],
    ['youtube.com', 'Alt+Y'],
    ['a=b', 'Alt+X'],
  ]);
});

test('sectionHtml: data-q em minúsculas com título, descrição e teclas; ícone só se houver', () => {
  const html = sectionHtml({ title: 'Janelas', accent: 'var(--blue)', icon: 0xf05af, rows: [['Fechar', 'Alt+W'], ['Ícone', 'X', 0xf0493]] });
  assert.match(html, /^<section style="--accent:var\(--blue\)"><h2><span class="ico" data-icon="984495"><\/span>Janelas<\/h2>/);
  assert.match(html, /data-q="janelas fechar alt\+w"><span class="what">Fechar/);
  assert.match(html, /data-q="janelas ícone x"><span class="ico" data-icon="984211"><\/span>/);
});

test('columnsHtml: 4 colunas, cada secção na sua, apps do apps.txt no topo de "Abrir apps"', () => {
  const html = columnsHtml(SECTIONS, [['Google Chrome', 'Alt+Shift+B']]);
  assert.equal(html.match(/<div class="col">/g).length, 4);
  assert.equal(html.match(/<section /g).length, SECTIONS.length);
  const col1 = html.split('<div class="col">')[1];
  assert.ok(col1.indexOf('Google Chrome') < col1.indexOf('Raycast'));
  assert.ok(html.split('<div class="col">')[3].includes('Sistema — Alt+Esc e depois…'));
});

test('SECTIONS: colunas de 1 a 4 e só uma secção recebe as apps', () => {
  assert.ok(SECTIONS.every(s => [1, 2, 3, 4].includes(s.col)));
  assert.equal(SECTIONS.filter(s => s.apps).length, 1);
});
