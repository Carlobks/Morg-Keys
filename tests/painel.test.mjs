// Painel "Apps e arranque" (Alt+Esc, C): funções puras de comum.mjs, apps-logica.mjs e apps-exemplo.mjs.
import assert from 'node:assert/strict';
import { test } from 'node:test';
import { appLabel, esc } from '../2-configuracao/glzr/zebar/omarchy-catppuccin/comum/comum.mjs';
import { chamadaDeExemplo } from '../2-configuracao/glzr/zebar/omarchy-catppuccin/painel/apps-exemplo.mjs';
import {
  b64, iconFor, keyboardHtml, keyHtml, keyId, keyLong, unb64,
} from '../2-configuracao/glzr/zebar/omarchy-catppuccin/painel/apps-logica.mjs';

const ESTADO = {
  keys: [{ key: 'alt+shift+b', value: 'Google Chrome' }, { key: 'alt+b', value: 'web: https://www.youtube.com' }],
  fixed: ['alt+shift+h'],
  workspaces: [],
  undo: 0,
};

test('appLabel: palavras especiais, sites sem www, caminhos de .exe', () => {
  assert.equal(appLabel(' Claude-Code '), 'Claude Code no terminal');
  assert.equal(appLabel('web: https://www.youtube.com/watch'), 'youtube.com');
  assert.equal(appLabel('web: isto não é url'), 'web: isto não é url');
  assert.equal(appLabel('C:\\Programas\\Notepad++\\notepad++.EXE'), 'notepad++');
  assert.equal(appLabel('Google Chrome'), 'Google Chrome');
});

test('esc: escapa o que partiria o HTML', () => {
  assert.equal(esc(`<a href="x">'&'</a>`), '&#60;a href=&#34;x&#34;&#62;&#39;&#38;&#39;&#60;/a&#62;');
});

test('iconFor: primeira palavra que bate; sites pelo domínio; ícones por omissão', () => {
  assert.deepEqual(iconFor('claude-code'), [0xf489, 'var(--peach)']);  // antes de "claude"
  assert.deepEqual(iconFor('Claude'), [0xf06c4, 'var(--peach)']);
  assert.deepEqual(iconFor('explorador'), [0xf024b, 'var(--yellow)']);  // pelo nome especial
  assert.deepEqual(iconFor('web: https://www.youtube.com'), [0xf05c3, 'var(--red)']);
  assert.deepEqual(iconFor('web: https://exemplo.pt'), [0xf059f, 'var(--sky)']);
  assert.deepEqual(iconFor('App Desconhecida'), [0xf003b, 'var(--lavender)']);
});

test('keyId e keyLong: letra -> id do GlazeWM -> texto do apps.txt', () => {
  assert.equal(keyId('B'), 'alt+shift+b');
  assert.equal(keyLong('alt+shift+b'), 'Alt+Shift+B');
  assert.equal(keyLong('alt+enter'), 'Alt+Enter');
  assert.equal(keyLong('alt+space'), 'Alt+Space');
});

test('keyHtml: tecla do sistema, com app, livre e escolhida', () => {
  const sistema = keyHtml('alt+shift+h', 'H', false, ESTADO, null);
  assert.match(sistema, /class="key fixed"/);
  assert.doesNotMatch(sistema, /data-unkey/);
  const comApp = keyHtml('alt+shift+b', 'B', false, ESTADO, null);
  assert.match(comApp, /class="key has"/);
  assert.match(comApp, /data-kind="key" data-value="Google Chrome"/);
  assert.match(comApp, /data-unkey="alt\+shift\+b"/);
  assert.match(keyHtml('alt+shift+z', 'Z', false, ESTADO, null), /class="key free".*title="Z: livre"/);
  assert.match(keyHtml('alt+shift+z', 'Z', true, ESTADO, { kind: 'key', key: 'alt+shift+z' }), /class="key wide free sel"/);
});

test('keyboardHtml: 26 letras, os dois Enter e os atalhos fora do teclado desenhado', () => {
  const html = keyboardHtml(ESTADO, null);
  assert.equal(html.match(/data-key="alt\+shift\+[a-z]"/g).length, 26);
  assert.match(html, /data-key="alt\+enter"/);
  assert.match(html, /data-key="alt\+shift\+enter"/);
  assert.match(html, /data-key="alt\+b".*<span class="cap">Alt B<\/span>/);
});

test('b64: sem + / = (passa no argsRegex) e ida e volta com acentos', () => {
  // Três tamanhos: o base64 normal acabaria em "==", "=" e nada.
  for (const fim of ['', '!', '!!']) {
    const texto = JSON.stringify({ op: 'ws-add', label: 'Câmara ✓', value: '>>>???' }) + fim;
    const codificado = b64(texto);
    assert.match(codificado, /^[A-Za-z0-9_-]+$/);
    assert.equal(unb64(codificado), texto);
  }
});

test('chamadaDeExemplo: mudar de tecla, tirar do arranque e desfazer', async () => {
  const call = chamadaDeExemplo(0);
  const pedir = o => call(['do', b64(JSON.stringify(o))]);
  let res = await pedir({ op: 'key', key: 'alt+shift+g', value: 'Google Chrome', from: 'alt+shift+b' });
  assert.equal(res.ok, true);
  assert.deepEqual(res.state.keys.filter(k => k.value === 'Google Chrome'), [{ key: 'alt+shift+g', value: 'Google Chrome' }]);
  res = await pedir({ op: 'ws-del', index: 1 });
  assert.deepEqual(res.state.workspaces.map(w => [w.index, w.label]),
    [[0, 'Terminal'], [1, 'web.whatsapp.com'], [2, 'Spotify']]);
  assert.equal(res.state.undo, 2);
  res = await call(['undo']);
  assert.equal(res.ok, false);
});
