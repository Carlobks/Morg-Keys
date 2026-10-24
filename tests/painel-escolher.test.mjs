// Painel "Apps e arranque": desenho da lista e dos workspaces, escolher e enviar, teclas e "+ site"
// (funções de apps-logica.mjs que o apps.mjs liga à página) e os pedidos da pré-visualização.
import assert from 'node:assert/strict';
import { test } from 'node:test';
import { chamadaDeExemplo } from '../2-configuracao/glzr/zebar/omarchy-catppuccin/painel/apps-exemplo.mjs';
import {
  b64, destinoDaTecla, enviarParaTecla, enviarParaWorkspace, escolhaDosDados, estadoDaResposta, listaHtml, mesmaEscolha,
  moverCursor, siteDoEndereco, textoDoErro, tirarDoWorkspace, tirarEscolha, tirarTecla, workspacesHtml,
} from '../2-configuracao/glzr/zebar/omarchy-catppuccin/painel/apps-logica.mjs';

const ESTADO = {
  keys: [{ key: 'alt+shift+b', value: 'Google Chrome' }, { key: 'alt+y', value: 'web: https://www.youtube.com' }],
  fixed: ['alt+shift+h'],
  workspaces: [{ index: 0, workspace: '2', label: 'Notas', value: 'Notas' },
               { index: 1, workspace: '2', label: 'web.whatsapp.com', value: 'web: https://web.whatsapp.com' },
               { index: 2, workspace: 'S', label: 'Terminal', process: 'WindowsTerminal' }],
  undo: 0,
};
const MENU = [{ name: 'Google Chrome', value: 'Google Chrome' }, { name: 'Obsidian', value: 'Obsidian' }];
const grupos = html => [...html.matchAll(/<div class="group">([^<]*)<\/div>/g)].map(m => m[1]);
const apps = html => [...html.matchAll(/data-kind="app" data-value="([^"]*)"/g)].map(m => m[1]);

test('listaHtml: especiais, sites (das teclas, dos workspaces e acrescentados) e menu Iniciar', () => {
  const { html, count } = listaHtml(ESTADO, MENU, ['web: https://novo.pt', 'web: https://www.youtube.com'], null, '');
  assert.deepEqual(grupos(html), ['Especiais', 'Sites', 'Menu Iniciar']);
  assert.deepEqual(apps(html), ['terminal', 'claude-code', 'explorador', 'web: https://www.youtube.com',
    'web: https://web.whatsapp.com', 'web: https://novo.pt', 'Google Chrome', 'Obsidian']);
  assert.match(html, /data-value="Google Chrome" data-label="Google Chrome">.*<span class="used">Alt\+Shift\+B<\/span><\/div>/);
  assert.equal(count, '2 no menu Iniciar');
});

test('listaHtml: filtro pelo nome ou pelo valor; grupos vazios desaparecem; escolhida marcada', () => {
  const { html } = listaHtml(ESTADO, MENU, [], { kind: 'app', value: 'Obsidian' }, '  OBSID ');
  assert.deepEqual(grupos(html), ['Menu Iniciar']);
  assert.match(html, /<div class="app sel" data-kind="app" data-value="Obsidian"/);
  assert.deepEqual(apps(listaHtml(ESTADO, MENU, [], null, 'whatsapp').html), ['web: https://web.whatsapp.com']);
  assert.deepEqual(apps(listaHtml(ESTADO, MENU, [], { kind: 'key', value: 'Obsidian' }, 'obsidian').html), ['Obsidian']);
  assert.doesNotMatch(listaHtml(ESTADO, MENU, [], { kind: 'key', value: 'Obsidian' }, 'obsidian').html, /app sel/);
});

test('listaHtml: sem resultados ou ainda sem o menu Iniciar', () => {
  assert.deepEqual(listaHtml(ESTADO, MENU, [], null, 'zzz'), { html: '<div class="empty">Nenhuma app com esse nome.</div>', count: '2 no menu Iniciar' });
  assert.deepEqual(listaHtml(ESTADO, [], [], null, 'zzz'), { html: '<div class="empty">A carregar as apps do menu Iniciar…</div>', count: '' });
});

test('workspacesHtml: 1–10 sempre, outros só com apps; contagem; chip escolhido', () => {
  const html = workspacesHtml(ESTADO, { kind: 'ws', index: 1 });
  assert.deepEqual([...html.matchAll(/<div class="box[^"]*" data-ws="([^"]*)"/g)].map(m => m[1]),
    ['1', '2', '3', '4', '5', '6', '7', '8', '9', '10', 'S']);
  assert.match(html, /<div class="box has" data-ws="2"><div class="head"><kbd>2<\/kbd><span>2 apps<\/span>/);
  assert.match(html, /<div class="box has" data-ws="S"><div class="head"><kbd>S<\/kbd><span>1 app<\/span>/);
  assert.match(html, /<div class="box" data-ws="1"><div class="head"><kbd>1<\/kbd><span><\/span><\/div><div class="hint">vazio<\/div>/);
  assert.match(html, /<div class="chip sel" data-kind="ws" data-index="1" data-ws="2" data-value="web: https:\/\/web.whatsapp.com"/);
  assert.match(html, /<div class="chip" data-kind="ws" data-index="2" data-ws="S" data-value="" data-label="Terminal"/);
  assert.match(html, /data-wsdel="0" title="Não abrir no arranque">✕<\/button>/);
  assert.doesNotMatch(workspacesHtml(ESTADO, { kind: 'key', index: 1 }), /chip sel/);
  // Sem app nem processo (entrada antiga): o ícone vem do nome.
  assert.match(workspacesHtml({ workspaces: [{ index: 0, workspace: '1', label: 'Spotify' }] }, null),
    /data-icon="984263" style="--ic:var\(--green\)"><\/span><span>Spotify<\/span>/);
});

test('estadoDaResposta e textoDoErro', () => {
  assert.deepEqual(estadoDaResposta({ ok: true }, '✓ Feito'), ['✓ Feito', 'ok']);
  assert.deepEqual(estadoDaResposta({ ok: true }), ['✓ Guardado', 'ok']);
  assert.deepEqual(estadoDaResposta({ ok: true }, ''), ['', 'ok']);
  assert.deepEqual(estadoDaResposta({ ok: false, error: 'Ocupado.' }), ['Ocupado.', 'err']);
  assert.deepEqual(estadoDaResposta({ ok: false }), ['Erro desconhecido.', 'err']);
  assert.equal(textoDoErro(new Error('x')), 'x');
  assert.equal(textoDoErro('texto'), 'texto');
  assert.equal(textoDoErro(null), null);
});

test('escolhaDosDados e mesmaEscolha', () => {
  assert.deepEqual(escolhaDosDados({ kind: 'ws', value: 'v', label: 'l', ws: '2', index: '3' }),
    { kind: 'ws', value: 'v', label: 'l', key: undefined, ws: '2', index: 3 });
  assert.equal(escolhaDosDados({ kind: 'app' }).index, undefined);
  const a = { kind: 'key', value: 'x', key: 'alt+b', index: undefined };
  assert.equal(mesmaEscolha(a, { ...a }), true);
  assert.equal(mesmaEscolha(null, a), false);
  for (const muda of [{ kind: 'app' }, { value: 'y' }, { key: 'alt+c' }, { index: 1 }]) {
    assert.equal(mesmaEscolha(a, { ...a, ...muda }), false);
  }
});

test('enviarParaTecla: tecla do sistema, a mesma, sem nome, nova e mudar de tecla', () => {
  const app = { kind: 'app', value: 'Obsidian', label: 'Obsidian' };
  assert.equal(enviarParaTecla(null, 'alt+shift+o', ESTADO), null);
  assert.deepEqual(enviarParaTecla(app, 'alt+shift+h', ESTADO),
    { limpar: false, erro: 'Alt+Shift+H é usado pelo sistema: escolha outra tecla.' });
  assert.deepEqual(enviarParaTecla({ kind: 'key', key: 'alt+shift+b', value: 'Google Chrome' }, 'alt+shift+b', ESTADO), { limpar: true });
  assert.deepEqual(enviarParaTecla({ kind: 'ws', label: 'Terminal', value: '' }, 'alt+shift+o', ESTADO),
    { limpar: true, erro: 'Esta app não tem um nome do menu Iniciar: escolha-a na lista.' });
  assert.deepEqual(enviarParaTecla(app, 'alt+shift+o', ESTADO),
    { limpar: true, op: { op: 'key', key: 'alt+shift+o', value: 'Obsidian' }, ok: '✓ Obsidian em Alt+Shift+O' });
  assert.deepEqual(enviarParaTecla({ kind: 'key', key: 'alt+shift+b', value: 'Google Chrome' }, 'alt+shift+g', ESTADO).op,
    { op: 'key', key: 'alt+shift+g', value: 'Google Chrome', from: 'alt+shift+b' });
});

test('enviarParaWorkspace: mover, o mesmo, sem nome e acrescentar', () => {
  const chip = { kind: 'ws', index: 1, ws: '2', label: 'web.whatsapp.com', value: 'web: https://web.whatsapp.com' };
  assert.equal(enviarParaWorkspace(null, '3'), null);
  assert.deepEqual(enviarParaWorkspace(chip, '2'), { limpar: true });
  assert.deepEqual(enviarParaWorkspace(chip, '3'), { limpar: true, ok: '✓ Agora abre no workspace 3',
    op: { op: 'ws-move', index: 1, ws: '3', expect_ws: '2', expect_label: 'web.whatsapp.com' } });
  assert.deepEqual(enviarParaWorkspace({ kind: 'key', value: '' }, '3'), { limpar: true });
  assert.deepEqual(enviarParaWorkspace({ kind: 'app', value: 'Obsidian', label: 'Notas O' }, '4'),
    { limpar: true, op: { op: 'ws-add', ws: '4', value: 'Obsidian', label: 'Notas O' }, ok: '✓ Notas O abre no workspace 4' });
  assert.equal(enviarParaWorkspace({ kind: 'key', value: 'web: https://www.x.pt' }, '4').op.label, 'x.pt');
});

test('tirarEscolha, tirarTecla e tirarDoWorkspace', () => {
  assert.equal(tirarEscolha(null, ESTADO), null);
  assert.deepEqual(tirarEscolha({ kind: 'key', key: 'alt+y' }, ESTADO), tirarTecla('alt+y'));
  assert.deepEqual(tirarTecla('alt+y'), { limpar: true, op: { op: 'unkey', key: 'alt+y' }, ok: '✓ Atalho tirado' });
  const chip = { kind: 'ws', index: 2, ws: 'S', label: 'Terminal' };
  assert.deepEqual(tirarEscolha(chip, ESTADO), tirarDoWorkspace(2, chip));
  assert.deepEqual(tirarDoWorkspace(2, chip), { limpar: true, ok: '✓ Já não abre no arranque',
    op: { op: 'ws-del', index: 2, expect_ws: 'S', expect_label: 'Terminal' } });
  assert.deepEqual(tirarEscolha({ kind: 'app', value: 'google chrome', label: 'Google Chrome' }, ESTADO),
    { limpar: true, op: { op: 'unkey', key: 'alt+shift+b' }, ok: '✓ Google Chrome já não tem atalho' });
  assert.deepEqual(tirarEscolha({ kind: 'app', value: 'Obsidian', label: 'Obsidian' }, ESTADO),
    { limpar: true, erro: 'Obsidian não tem atalho para tirar.' });
});

test('destinoDaTecla: Esc, Del, Enter, números e letras', () => {
  assert.deepEqual(destinoDaTecla('Escape'), ['cancelar']);
  assert.deepEqual(destinoDaTecla('Delete'), ['tirar']);
  assert.deepEqual(destinoDaTecla('Backspace'), ['tirar']);
  assert.deepEqual(destinoDaTecla('Enter', false), ['tecla', 'alt+enter']);
  assert.deepEqual(destinoDaTecla('Enter', true), ['tecla', 'alt+shift+enter']);
  assert.deepEqual(destinoDaTecla('3'), ['workspace', '3']);
  assert.deepEqual(destinoDaTecla('0'), ['workspace', '10']);
  assert.deepEqual(destinoDaTecla('G'), ['tecla', 'alt+shift+g']);
  assert.equal(destinoDaTecla('Tab'), null);
  assert.equal(destinoDaTecla('ç'), null);
});

test('moverCursor: setas dentro da lista', () => {
  assert.equal(moverCursor(0, 3, 'ArrowDown'), 1);
  assert.equal(moverCursor(2, 3, 'ArrowDown'), 2);
  assert.equal(moverCursor(0, 3, 'ArrowUp'), 0);
  assert.equal(moverCursor(2, 3, 'ArrowUp'), 1);
  assert.equal(moverCursor(0, 0, 'ArrowDown'), 0);
});

test('siteDoEndereco: vazio, sem esquema, inválido', () => {
  assert.equal(siteDoEndereco('   '), null);
  assert.deepEqual(siteDoEndereco(' youtube.com '), { value: 'web: https://youtube.com' });
  assert.deepEqual(siteDoEndereco('HTTP://x.pt/a'), { value: 'web: HTTP://x.pt/a' });
  assert.deepEqual(siteDoEndereco('http://'), { erro: 'Endereço inválido.' });
});

test('chamadaDeExemplo: apps, estado, acrescentar e mover num workspace', async () => {
  const call = chamadaDeExemplo(0);
  assert.equal((await call(['apps'])).apps.length, 15);
  const antes = (await call(['state'])).state.workspaces.length;
  let res = await call(['do', b64(JSON.stringify({ op: 'ws-add', ws: '5', value: 'Obsidian', label: 'Obsidian' }))]);
  assert.deepEqual(res.state.workspaces.at(-1), { index: antes, workspace: '5', label: 'Obsidian', value: 'Obsidian' });
  res = await call(['do', b64(JSON.stringify({ op: 'ws-move', index: 0, ws: '9' }))]);
  assert.equal(res.state.workspaces[0].workspace, '9');
  res = await call(['do', b64(JSON.stringify({ op: 'outra' }))]);
  assert.equal(res.state.undo, 3);
  assert.equal(typeof chamadaDeExemplo(), 'function');  // demora por omissão (só no navegador)
});
