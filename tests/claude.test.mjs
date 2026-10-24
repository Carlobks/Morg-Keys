// Quota do Claude na barra (comum/claude.mjs): valores, sem valores (só o ✻), esbatido e esconder.
import assert from 'node:assert/strict';
import { test } from 'node:test';
import { claudeVista, fmtUntil, level, STALE_AFTER_S } from '../2-configuracao/glzr/zebar/omarchy-catppuccin/comum/claude.mjs';

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
  assert.match(v.dica, /Clique: abre a página de uso/);
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
