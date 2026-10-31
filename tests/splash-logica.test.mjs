// Ecrã de arranque (arranque/splash.html): saudação, ícones, etapas e quando sair (splash-logica.mjs).
import assert from 'node:assert/strict';
import { test } from 'node:test';
import {
  APP_ICONS, animacaoValida, autorDaFrase, classesDaEtapa, deveFechar, emPreVisualizacao, EXEMPLO, horaTexto, iconFor,
  MIN_ITEM_MS, podeSair, saudacao,
} from '../2-configuracao/glzr/zebar/omarchy-catppuccin/arranque/splash-logica.mjs';

test('pré-visualização: file: ou ?preview; no Zebar não', () => {
  assert.equal(emPreVisualizacao('file:', ''), true);
  assert.equal(emPreVisualizacao('http:', '?preview'), true);
  assert.equal(emPreVisualizacao('http:', '?x=1&preview=1'), true);
  assert.equal(emPreVisualizacao('http:', ''), false);
});

test('EXEMPLO: um arranque em curso com o nome fictício, a frase e duas etapas', () => {
  assert.equal(EXEMPLO.nome, 'Ana');
  assert.equal(deveFechar(EXEMPLO, Date.now() / 1000), false);
  assert.deepEqual(EXEMPLO.steps.map(s => s.state), ['feito', 'a_carregar']);
});

test('deveFechar: sem progresso, já no fim ou com mais de 60 s', () => {
  const agora = 1000;
  assert.equal(deveFechar(null, agora), true);
  assert.equal(deveFechar({ started: agora, fim: true }, agora), true);
  assert.equal(deveFechar({ started: agora - 61, fim: false }, agora), true);
  assert.equal(deveFechar({ started: agora - 60, fim: false }, agora), false);
});

test('animacaoValida: a do progresso se existir; senão "cafe"', () => {
  assert.equal(animacaoValida('cafe', ['cafe', 'chuva']), 'cafe');
  assert.equal(animacaoValida('chuva', ['cafe', 'chuva']), 'chuva');
  assert.equal(animacaoValida('antiga', ['cafe']), 'cafe');
  assert.equal(animacaoValida(undefined, ['cafe']), 'cafe');
});

test('saudação com e sem nome; hora como no relógio da barra', () => {
  assert.equal(saudacao('Ana'), 'Muito bem-vindo, Ana');
  assert.equal(saudacao(''), 'Muito bem-vindo');
  assert.equal(saudacao(undefined), 'Muito bem-vindo');
  assert.equal(horaTexto(new Date(2026, 9, 31, 7, 3)), '07:03 · sábado, 31 de outubro');
});

test('autorDaFrase: personagem e anime, só um deles, ou nenhum', () => {
  assert.equal(autorDaFrase({ personagem: 'Dr. Hiriluk', anime: 'One Piece' }), '— Dr. Hiriluk, One Piece');
  assert.equal(autorDaFrase({ personagem: 'Dr. Hiriluk' }), '— Dr. Hiriluk');
  assert.equal(autorDaFrase({ anime: 'One Piece', personagem: '' }), '— One Piece');
  assert.equal(autorDaFrase({ texto: 'só a frase' }), null);
});

test('iconFor: um ícone por tipo de etapa; apps conhecidas pelo processo; o resto genérico', () => {
  assert.equal(iconFor('barra'), 0xf035c);
  assert.equal(iconFor('glazewm'), 0xf0574);
  assert.equal(iconFor('fim'), 0xf012c);
  assert.equal(iconFor('anim'), 0xf03d8);
  assert.equal(iconFor('apps'), 0xf003b);
  assert.equal(iconFor('bat:2'), 0xf489);
  assert.equal(iconFor('app:chrome'), APP_ICONS.chrome);
  assert.equal(iconFor('app:notepad'), 0xf0614);
  assert.equal(iconFor('outra'), 0xf0614);
});

test('classesDaEtapa: feito e falhou só depois de a linha estar visível o tempo mínimo', () => {
  assert.deepEqual(classesDaEtapa('feito', MIN_ITEM_MS - 1), []);
  assert.deepEqual(classesDaEtapa('feito', MIN_ITEM_MS), ['done']);
  assert.deepEqual(classesDaEtapa('falhou', MIN_ITEM_MS), ['done', 'fail']);
  assert.deepEqual(classesDaEtapa('a_carregar', 10_000), []);
});

test('podeSair: o fim tem de durar 300 ms e o ecrã estar mais de 1,8 s à vista', () => {
  assert.equal(podeSair(300, 1801), true);
  assert.equal(podeSair(299, 5000), false);
  assert.equal(podeSair(1000, 1800), false);
});
