// As páginas do guia e do painel (guia.mjs, apps.mjs) carregadas em modo de pré-visualização com um DOM
// falso: confirma que os imports batem com o que a lógica exporta e que a ligação à página desenha.
// O código destas páginas é cola com o DOM e o Zebar, fora da cobertura (docs/validacao-manual.md).
import assert from 'node:assert/strict';
import { test } from 'node:test';

const PACK = '../2-configuracao/glzr/zebar/omarchy-catppuccin';

function elemento(id) {
  return {
    id, value: '', textContent: '', innerHTML: '', className: '', disabled: false, scrollTop: 0, offsetWidth: 0,
    dataset: {}, style: { setProperty() {} }, ouvintes: {},
    classList: { lista: new Set(), add(...c) { for (const x of c) this.lista.add(x); }, remove(c) { this.lista.delete(c); },
                 toggle(c, sim) { if (sim) this.lista.add(c); else this.lista.delete(c); }, contains(c) { return this.lista.has(c); } },
    addEventListener(tipo, f) { this.ouvintes[tipo] = f; },
    dispatchEvent(e) { this.ouvintes[e.type]?.(e); },
    querySelectorAll: () => [], focus() {}, blur() {}, closest: () => null, scrollIntoView() {},
  };
}

function paginaFalsa() {
  const elementos = new Map();
  globalThis.document = {
    getElementById: id => elementos.get(id) ?? elementos.set(id, elemento(id)).get(id),
    body: elemento('body'), documentElement: elemento('html'), activeElement: null,
    ouvintes: {}, addEventListener(tipo, f) { this.ouvintes[tipo] = f; },
    fonts: { load: async () => {} }, querySelectorAll: () => [],
  };
  globalThis.location = { protocol: 'file:', search: '' };
  globalThis.window = { close() {}, addEventListener() {} };
  globalThis.screen = { width: 1920 };
  globalThis.requestAnimationFrame = f => f();
  return document;
}

const esperar = ms => new Promise(r => setTimeout(r, ms));

test('painel (apps.mjs): pré-visualização com os dados de exemplo e o filtro ligado', async () => {
  const doc = paginaFalsa();
  await import(`${PACK}/painel/apps.mjs`);
  await esperar(500);  // os pedidos de exemplo demoram 150 ms cada
  const $ = id => doc.getElementById(id);
  assert.ok(doc.body.classList.contains('standalone'));
  assert.equal($('count').textContent, '15 no menu Iniciar');
  assert.match($('list').innerHTML, /<div class="group">Especiais<\/div>.*<div class="group">Menu Iniciar<\/div>/);
  assert.match($('kb').innerHTML, /data-key="alt\+shift\+b"/);
  assert.match($('wsgrid').innerHTML, /data-ws="10"/);
  $('filter').value = 'obsid';
  $('filter').dispatchEvent(new Event('input'));
  assert.doesNotMatch($('list').innerHTML, /Especiais/);
  assert.match($('list').innerHTML, /data-value="Obsidian"/);
});

test('guia (guia.mjs): pré-visualização desenha as quatro colunas', async () => {
  const doc = paginaFalsa();
  await import(`${PACK}/guia/guia.mjs`);
  await esperar(50);  // apps.txt não se lê fora do Zebar: o guia desenha sem as apps
  assert.ok(doc.body.classList.contains('standalone'));
  assert.equal(doc.getElementById('sections').innerHTML.match(/<div class="col">/g).length, 4);
});
