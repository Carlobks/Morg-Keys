// Painel do sistema (guia/sistema.html, Alt+Esc): grupos, animação e camada ativa (sistema-logica.mjs).
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { test } from 'node:test';
import {
  animacaoDoArranque, avisoDeErros, camadaAtiva, GROUPS, gruposHTML, rotulosDoArranque,
} from '../2-configuracao/glzr/zebar/omarchy-catppuccin/guia/sistema-logica.mjs';

const CONFIG = new URL('../2-configuracao/glzr/glazewm/config.yaml', import.meta.url);

test('gruposHTML: um <section> por grupo, o largo marcado, a cor e as teclas escapadas', () => {
  const html = gruposHTML([
    { title: 'A & B', color: 'var(--blue)', items: [['<', 1, 'Menor <']] },
    { title: 'Largo', color: 'var(--red)', wide: true, items: [['E', 2, 'Animação: <b id="anim">…</b>', true]] },
  ]);
  assert.match(html, /<section class="group" style="--c:var\(--blue\)">\s*<h2>A &#38; B<\/h2>/);
  assert.match(html, /<span class="lb">Menor &#60;<\/span><kbd>&#60;<\/kbd>/);
  assert.match(html, /<section class="group wide" style="--c:var\(--red\)">/);
  assert.match(html, /<span class="lb">Animação: <b id="anim">…<\/b><\/span><kbd>E<\/kbd>/);  // já é HTML
  assert.equal(gruposHTML(GROUPS).match(/<li>/g).length, 15);
});

test('GROUPS: cada tecla do painel existe na camada "sistema" do config.yaml do GlazeWM', () => {
  const config = readFileSync(CONFIG, 'utf8');
  const inicio = config.indexOf("- name: 'sistema'");
  assert.ok(inicio > 0, 'camada sistema em falta no config.yaml');
  const fim = config.indexOf('- name:', inicio + 1);
  const camada = config.slice(inicio, fim < 0 ? undefined : fim);
  for (const [tecla] of GROUPS.flatMap(g => g.items)) {
    assert.match(camada, new RegExp(`bindings: \\[[^\\]]*'${tecla.toLowerCase()}'`), `tecla ${tecla} sem ação no config.yaml`);
  }
});

test('animacaoDoArranque: lê "animação =" com ou sem acentos; sem linha é Café; nomes desconhecidos como estão', () => {
  assert.equal(animacaoDoArranque('# x\r\nanimação = cafe\r\n'), 'Café');
  assert.equal(animacaoDoArranque('  Animacao=Café'), 'Café');
  assert.equal(animacaoDoArranque('nome = Ana'), 'Café');
  assert.equal(animacaoDoArranque('animação = Chuva'), 'chuva');
});

test('camadaAtiva: só com a camada "sistema"; sem dados do GlazeWM não está', () => {
  assert.equal(camadaAtiva([{ name: 'resize' }, { name: 'sistema' }]), true);
  assert.equal(camadaAtiva([{ name: 'resize' }]), false);
  assert.equal(camadaAtiva(undefined), false);
});

test('avisoDeErros: ligado por omissão; "erros = esconder" (ou não, ocultar, off) desliga; comentários não contam', () => {
  assert.equal(avisoDeErros('animacao = cafe'), 'ligado');
  assert.equal(avisoDeErros('erros = mostrar'), 'ligado');
  for (const valor of ['esconder', 'ESCONDER', 'não', 'nao', 'ocultar', 'off']) {
    assert.equal(avisoDeErros(`erros = ${valor}`), 'desligado', valor);
  }
  assert.equal(avisoDeErros('# erros = esconder\r\nerros = mostrar'), 'ligado');
});

test('rotulosDoArranque: a animação e o aviso de erros de uma vez, com o id do elemento de cada um', () => {
  assert.deepEqual(rotulosDoArranque('animação = cafe\nerros = esconder'), [['anim', 'Café'], ['erros', 'desligado']]);
});

test('GROUPS: o V liga e desliga o aviso de erros, com o ícone de alerta e o estado em HTML', () => {
  const v = GROUPS.flatMap(g => g.items).find(([tecla]) => tecla === 'V');
  assert.deepEqual(v, ['V', 0xf0028, 'Aviso de erros: <b id="erros">…</b>', true]);
});
