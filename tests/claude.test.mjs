// Quota do Claude na barra (partilhado/claude.mjs): valores, sem valores (só o ✻), esbatido e esconder.
import assert from 'node:assert/strict';
import { test } from 'node:test';
import {
  claudeVista, fmtUntil, level, ligarClaude, RAPIDO_DURANTE_MS, RAPIDO_MS, RELER_MS, STALE_AFTER_S,
} from '../2-configuracao/glzr/zebar/omarchy-catppuccin/partilhado/claude.mjs';

const AGORA = 1_800_000_000;

test('fmtUntil: dias, horas e minutos; nunca negativo', () => {
  assert.equal(fmtUntil(AGORA + 27 * 3600, AGORA), '1d3h');
  assert.equal(fmtUntil(AGORA + 65 * 60, AGORA), '1h05');
  assert.equal(fmtUntil(AGORA + 7 * 60, AGORA), '7m');
  assert.equal(fmtUntil(AGORA - 600, AGORA), '0m');
});

test('level: sem cor abaixo de 50 %, amarelo a partir de 50 %, vermelho a partir de 80 %', () => {
  assert.deepEqual([49, 50, 79, 80].map(level), ['', 'warn', 'warn', 'high']);
});

test('esconder (claude = esconder no arranque.txt): o indicador sai da barra', () => {
  assert.deepEqual(claudeVista({ now: AGORA, mostrar: false, five_hour: { pct: 10, resets_at: AGORA } }),
    { mostrar: false, html: '', stale: false, dica: '' });
});

test('sem valores: só o ✻, com a dica a explicar porquê (e há quanto tempo expiraram os últimos)', () => {
  const v = claudeVista({ now: AGORA, mostrar: true, captured_at: null, five_hour: null, seven_day: null });
  assert.equal(v.mostrar, true);
  assert.equal(v.html, '');
  assert.match(v.dica, /sem valores\.\nSó chegam quando usa o Claude Code num terminal/);
  assert.match(v.dica, /Clique: pôr os valores à mão · Botão direito: página de uso\./);
  assert.match(v.dica, /claude = esconder/);
  assert.doesNotMatch(v.dica, /expiraram/);
  const antigos = claudeVista({ now: AGORA, captured_at: AGORA - 7200, five_hour: null, seven_day: null });
  assert.match(antigos.dica, /Os últimos \(de há 2h00\) já expiraram\./);
});

test('com as duas janelas: percentagens com cor, reposição e idade; frescos não ficam esbatidos', () => {
  const v = claudeVista({ now: AGORA, mostrar: true, captured_at: AGORA - 60,
    five_hour: { pct: 23.5, resets_at: AGORA + 3600 }, seven_day: { pct: 85, resets_at: AGORA + 86400 } });
  assert.equal(v.html, '<span class="">5h 24%</span> <span class="sep">·</span> <span class="high">sem 85%</span>'
    + ' <span class="sep">·</span> <span class="muted">↺ 1h00</span>');
  assert.equal(v.stale, false);
  assert.equal(v.dica.split('\n')[0], 'Sessão (5h): 23.5% — repõe em 1h00');
  assert.match(v.dica, /Semanal: 85% — repõe em 1d0h\nValores de há 1m \(última sessão no terminal\)\./);
});

test('só uma janela; valores velhos ou sem hora ficam esbatidos', () => {
  const so5h = claudeVista({ now: AGORA, captured_at: AGORA - STALE_AFTER_S - 1,
    five_hour: { pct: 60, resets_at: AGORA + 60 }, seven_day: null });
  assert.match(so5h.html, /<span class="warn">5h 60%<\/span>.*<span class="muted">sem —<\/span>/);
  assert.equal(so5h.stale, true);
  const soSemana = claudeVista({ now: AGORA, captured_at: null, five_hour: null,
    seven_day: { pct: 10, resets_at: AGORA + 60 } });
  assert.match(soSemana.html, /^<span class="muted">5h —<\/span>.*sem 10%<\/span>$/);
  assert.equal(soSemana.stale, true);
  assert.match(soSemana.dica, /Ainda sem a hora dos valores\./);
});

test('valores postos à mão no modal: a dica diz de onde vêm e há quanto tempo', () => {
  const v = claudeVista({ now: AGORA, captured_at: AGORA - 300, origem: 'manual',
    five_hour: { pct: 40, resets_at: AGORA + 8100 }, seven_day: null });
  assert.match(v.dica, /Valores postos à mão há 5m\./);
  assert.doesNotMatch(v.dica, /terminal/);
});

// Elemento e relógio falsos: o ligarClaude só usa addEventListener, setInterval/clearInterval e setTimeout/clearTimeout.
function falsos() {
  const ouvintes = {};
  const el = { addEventListener: (tipo, f) => { ouvintes[tipo] = f; } };
  const relogio = { proximo: 1, ativos: new Map(), feitos: [],
    setInterval(f, ms) { const id = this.proximo++; this.ativos.set(id, { f, ms, tipo: 'cada' }); return id; },
    setTimeout(f, ms) { const id = this.proximo++; this.ativos.set(id, { f, ms, tipo: 'uma' }); return id; },
    clearInterval(id) { this.ativos.delete(id); },
    clearTimeout(id) { this.ativos.delete(id); },
    de(ms, tipo) { return [...this.ativos.values()].filter(a => a.ms === ms && a.tipo === tipo); },
  };
  return { ouvintes, el, relogio };
}

test('ligarClaude: lê já e de 30 em 30 s; o clique abre o modal e relê de 3 em 3 s durante 1 min', async () => {
  const { ouvintes, el, relogio } = falsos();
  const pedidos = [];
  ligarClaude(el, { reler: () => pedidos.push('reler'), abrirModal: async () => pedidos.push('modal'),
    abrirUso: () => pedidos.push('uso') }, relogio);
  assert.deepEqual(pedidos, ['reler']);
  assert.equal(relogio.de(RELER_MS, 'cada').length, 1);
  ouvintes.click();
  ouvintes.click(); // um 2.º clique recomeça o minuto, sem duplicar a releitura rápida
  await Promise.resolve();
  assert.deepEqual(pedidos, ['reler', 'modal', 'modal']);
  assert.equal(relogio.de(RAPIDO_MS, 'cada').length, 1);
  const [fim] = relogio.de(RAPIDO_DURANTE_MS, 'uma');
  relogio.de(RAPIDO_MS, 'cada')[0].f();
  assert.equal(pedidos.at(-1), 'reler');
  fim.f();
  assert.equal(relogio.de(RAPIDO_MS, 'cada').length, 0);
  assert.equal(relogio.de(RELER_MS, 'cada').length, 1);
});

test('ligarClaude: o botão direito abre a página de uso sem o menu do WebView2; um erro do modal não rebenta', async () => {
  const { ouvintes, el, relogio } = falsos();
  const pedidos = [];
  const erros = [];
  const erroOriginal = console.error;
  console.error = e => erros.push(String(e));
  try {
    ligarClaude(el, { reler: () => {}, abrirUso: () => pedidos.push('uso'),
      abrirModal: () => Promise.reject(new Error('sem Zebar')) }, relogio);
    let evitado = false;
    ouvintes.contextmenu({ preventDefault: () => { evitado = true; } });
    assert.deepEqual([pedidos, evitado], [['uso'], true]);
    ouvintes.click();
    await new Promise(r => setImmediate(r));
    assert.deepEqual(erros, ['Error: sem Zebar']);
  } finally {
    console.error = erroOriginal;
  }
});
