// Modal dos limites do Claude (limites/limites-logica.mjs, P7): valores iniciais, de onde vêm, pedido e erros.
import assert from 'node:assert/strict';
import { test } from 'node:test';
import { unb64 } from '../2-configuracao/glzr/zebar/omarchy-catppuccin/painel/apps-logica.mjs';
import {
  errosDaResposta, ESTADO_DE_EXEMPLO, origemDosValores, pedidoDeGravar, valoresIniciais,
} from '../2-configuracao/glzr/zebar/omarchy-catppuccin/limites/limites-logica.mjs';

const AGORA = 1_800_000_000;
const SEM_NADA = { now: AGORA, captured_at: null, origem: null, five_hour: null, seven_day: null };

test('valoresIniciais: o % atual nos campos e o reset atual só como dica (vazio mantém)', () => {
  const estado = { ...SEM_NADA, five_hour: { pct: 39.6, resets_at: AGORA + 8100 },
    seven_day: { pct: 70, resets_at: AGORA + 2 * 86400 + 3600 } };
  assert.deepEqual(valoresIniciais(estado), {
    five_pct: '40', five_reset: '', week_pct: '70', week_reset: '',
    five_reset_dica: 'vazio: fica 2h15', week_reset_dica: 'vazio: fica 2d1h',
  });
});

test('valoresIniciais: sem valores, campos vazios e exemplos do que se pode escrever', () => {
  assert.deepEqual(valoresIniciais(SEM_NADA), {
    five_pct: '', five_reset: '', week_pct: '', week_reset: '',
    five_reset_dica: 'ex.: 14:30 ou 2h15', week_reset_dica: 'ex.: qui 16:00',
  });
});

test('origemDosValores: à mão, do terminal ou ainda nenhuns', () => {
  assert.equal(origemDosValores(SEM_NADA), 'Ainda sem valores guardados.');
  assert.equal(origemDosValores({ ...SEM_NADA, captured_at: AGORA - 300, origem: 'manual' }),
    'Postos à mão há 5m.');
  assert.equal(origemDosValores({ ...SEM_NADA, captured_at: AGORA - 7200 }),
    'Do Claude Code no terminal, há 2h00.');
});

test('pedidoDeGravar: só os quatro campos, sem espaços à volta, em base64url', () => {
  const b64 = pedidoDeGravar({ five_pct: ' 40 ', five_reset: '2h15', week_pct: '70', week_reset: 'sáb 9:00', x: 1 });
  assert.match(b64, /^[A-Za-z0-9_-]+$/);
  assert.deepEqual(JSON.parse(unb64(b64)),
    { five_pct: '40', five_reset: '2h15', week_pct: '70', week_reset: 'sáb 9:00' });
  assert.deepEqual(JSON.parse(unb64(pedidoDeGravar({}))),
    { five_pct: '', five_reset: '', week_pct: '', week_reset: '' });
});

test('errosDaResposta: gravado, erros por campo ou um erro geral', () => {
  assert.deepEqual(errosDaResposta({ ok: true, state: SEM_NADA }), { ok: true, porCampo: {}, geral: '' });
  assert.deepEqual(errosDaResposta({ ok: false, errors: { five_pct: 'Falta o %.' } }),
    { ok: false, porCampo: { five_pct: 'Falta o %.' }, geral: '' });
  assert.deepEqual(errosDaResposta({ ok: false, error: 'Pedido estragado.' }),
    { ok: false, porCampo: {}, geral: 'Pedido estragado.' });
  assert.deepEqual(errosDaResposta(null), { ok: false, porCampo: {}, geral: 'Sem resposta do bar_helper.py.' });
});

test('ESTADO_DE_EXEMPLO: serve à pré-visualização (valores à mão, as duas janelas)', () => {
  assert.equal(ESTADO_DE_EXEMPLO.origem, 'manual');
  assert.ok(ESTADO_DE_EXEMPLO.five_hour.resets_at > ESTADO_DE_EXEMPLO.now);
  assert.ok(ESTADO_DE_EXEMPLO.seven_day.resets_at > ESTADO_DE_EXEMPLO.now);
});
