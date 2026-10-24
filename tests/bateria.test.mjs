// Bateria na barra (comum/bateria.mjs): ícone de 10 em 10 %, cores, dica e PC sem bateria.
import assert from 'node:assert/strict';
import { test } from 'node:test';
import { AVISO, BAIXA, bateria, DESCONHECIDA, duracao } from '../2-configuracao/glzr/zebar/omarchy-catppuccin/comum/bateria.mjs';

test('sem bateria (sem saída do provider ou sem percentagem): nada a mostrar', () => {
  assert.equal(bateria(undefined), null);
  assert.equal(bateria(null), null);
  assert.equal(bateria({ state: 'unknown' }), null);
});

test('a descarregar: ícone pelo passo de 10 % mais próximo, texto e o tempo que resta', () => {
  assert.deepEqual(bateria({ chargePercent: 76.4, isCharging: false, state: 'discharging', timeTillEmpty: 185 * 60000 }),
    { icone: 0xf0081, texto: '76%', nivel: '', dica: 'Bateria: 76% · restam 3h05' });
  assert.equal(bateria({ chargePercent: 100, state: 'discharging' }).icone, 0xf0079);
  assert.equal(bateria({ chargePercent: 3, state: 'discharging' }).icone, 0xf0083);  // quase vazia: alerta
  assert.equal(bateria({ chargePercent: 50, state: 'discharging' }).dica, 'Bateria: 50%');  // sem estimativa
});

test('cores: amarela abaixo do aviso, vermelha abaixo da baixa; a carregar fica verde', () => {
  assert.equal(bateria({ chargePercent: AVISO, state: 'discharging' }).nivel, '');
  assert.equal(bateria({ chargePercent: AVISO - 1, state: 'discharging' }).nivel, 'warn');
  assert.equal(bateria({ chargePercent: BAIXA - 1, state: 'discharging' }).nivel, 'high');
  assert.equal(bateria({ chargePercent: BAIXA - 1, isCharging: true, state: 'charging' }).nivel, 'ok');
});

test('a carregar: ícone com raio, tempo até cheia; cheia; estado desconhecido', () => {
  assert.deepEqual(bateria({ chargePercent: 42, isCharging: true, state: 'charging', timeTillFull: 75 * 60000 }),
    { icone: 0xf0088, texto: '42%', nivel: 'ok', dica: 'Bateria: 42% · a carregar · cheia em 1h15' });
  assert.equal(bateria({ chargePercent: 0, state: 'charging' }).icone, 0xf089f);  // só o state diz que carrega
  assert.equal(bateria({ chargePercent: 60, isCharging: true }).dica, 'Bateria: 60% · a carregar');
  assert.deepEqual(bateria({ chargePercent: 100, isCharging: true, state: 'full' }),
    { icone: 0xf0085, texto: '100%', nivel: 'ok', dica: 'Bateria: 100% · cheia' });
  assert.equal(bateria({ chargePercent: 55, state: 'unknown' }).icone, DESCONHECIDA);
  assert.equal(bateria({ chargePercent: 140, state: 'discharging' }).texto, '100%');  // valores fora de 0–100
  assert.equal(bateria({ chargePercent: -5, state: 'discharging' }).texto, '0%');
});

test('duracao: horas e minutos, ou só minutos', () => {
  assert.equal(duracao(75 * 60000), '1h15');
  assert.equal(duracao(5 * 60000), '5 min');
  assert.equal(duracao(120 * 60000), '2h00');
});
