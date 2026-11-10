// Barra (bar.html): o HTML de cada zona, o relógio, o volume, a chávena e os comandos (bar-logica.mjs).
import assert from 'node:assert/strict';
import { test } from 'node:test';
import {
  APPS, audioVista, awakeVista, bateriaHTML, clockText, comandosDoBotao, cpuHTML, esc, ICON, isoWeek, memoryHTML,
  minimizadas, minimizedHTML, modesHTML, networkHTML, networkIcon, proximoVolume, SCRATCH, sistemaFechou, vigiaSistema, volumeIcon,
  workspacesHTML,
} from '../2-configuracao/glzr/zebar/omarchy-catppuccin/bar-logica.mjs';

const ws = (name, extra = {}) => ({ name, hasFocus: false, isDisplayed: false, children: [{}], ...extra });

test('esc: escapa o HTML e trata null/undefined como texto vazio', () => {
  assert.equal(esc('<a href="x">\'&'), '&#60;a href=&#34;x&#34;&#62;&#39;&#38;');
  assert.equal(esc(null), '');
  assert.equal(esc(undefined), '');
});

test('workspacesHTML: focado, vazio, nome a mostrar; o scratchpad só aberto', () => {
  const html = workspacesHTML([
    ws('1', { hasFocus: true }), ws('2', { children: [], displayName: 'Dois' }), ws(SCRATCH), ws('<x>'),
  ]);
  assert.equal(html,
    '<button class="workspace focused  " data-ws="1">1</button>' +
    '<button class="workspace  empty " data-ws="2">Dois</button>' +
    '<button class="workspace   " data-ws="&#60;x&#62;">&#60;x&#62;</button>');
  assert.equal(workspacesHTML([ws(SCRATCH, { isDisplayed: true })]),
    '<button class="workspace   scratch" data-ws="S">S</button>');
});

test('minimizadas: procura em toda a árvore do workspace; sem workspace não há nenhuma', () => {
  const janela = (id, minimizada) => ({ type: 'window', id, state: { type: minimizada ? 'minimized' : 'tiling' } });
  const arvore = { type: 'workspace', children: [janela('a', true), { type: 'split', children: [janela('b', true), janela('c', false)] }, { type: 'window' }] };
  assert.deepEqual(minimizadas(arvore).map(j => j.id), ['a', 'b']);
  assert.deepEqual(minimizadas(undefined), []);
});

test('minimizedHTML: ícone e nome curto das apps conhecidas; nome do processo nas outras', () => {
  const html = minimizedHTML([
    { id: 'id1', processName: 'chrome', title: 'Página <1>' },
    { id: 'id2', processName: 'notepad', title: 'Notas' },
  ]);
  assert.equal(html,
    `<button class="min-chip" data-restore="id1" title="Página &#60;1&#62;\nClique para restaurar"><span class="ico" data-icon="${APPS.chrome.icon}"></span>Chrome</button>` +
    `<button class="min-chip" data-restore="id2" title="Notas\nClique para restaurar"><span class="ico" data-icon="${ICON.app}"></span>notepad</button>`);
});

test('modesHTML: um botão por modo; PAUSADO à frente quando o GlazeWM está em pausa', () => {
  const modos = [{ name: 'resize' }, { name: 'sistema', displayName: 'SISTEMA' }];
  assert.equal(modesHTML({ bindingModes: modos, isPaused: false }),
    '<button class="pill" data-mode="resize">resize</button><button class="pill" data-mode="sistema">SISTEMA</button>');
  assert.equal(modesHTML({ bindingModes: [], isPaused: true }), '<button class="pill paused" data-pause="1">PAUSADO</button>');
});

test('rede: ícone pelo tipo da ligação e o nome da rede Wi-Fi', () => {
  const rede = type => ({ defaultInterface: { type } });
  assert.equal(networkIcon(rede('ethernet')), ICON.ethernet);
  assert.equal(networkIcon(rede('wifi')), ICON.wifi);
  assert.equal(networkIcon(rede('proprietary_virtual')), ICON.vpn);
  assert.equal(networkIcon(rede('outro')), ICON.wifiOff);
  assert.equal(networkIcon(undefined), ICON.wifiOff);
  assert.equal(networkHTML({ ...rede('wifi'), defaultGateway: { ssid: 'Casa & Co' } }),
    `<span class="ico" data-icon="${ICON.wifi}"></span>Casa &#38; Co`);
  assert.equal(networkHTML({}), `<span class="ico" data-icon="${ICON.wifiOff}"></span>`);
});

test('CPU acima de 85 % fica em destaque; memória arredondada', () => {
  assert.equal(cpuHTML(85.4), `<span class="ico" data-icon="${ICON.cpu}"></span><span class="">85%</span>`);
  assert.equal(cpuHTML(85.6), `<span class="ico" data-icon="${ICON.cpu}"></span><span class="high">86%</span>`);
  assert.equal(memoryHTML(41.5), `<span class="ico" data-icon="${ICON.memory}"></span>42%`);
});

test('isoWeek: semana ISO 8601, também nas viragens de ano', () => {
  assert.equal(isoWeek(new Date(2026, 9, 31)), 44);
  assert.equal(isoWeek(new Date(2027, 0, 1)), 53);  // sexta: ainda a última semana de 2026
  assert.equal(isoWeek(new Date(2024, 11, 30)), 1); // segunda: já a semana 1 de 2025
  assert.equal(isoWeek(new Date(2026, 0, 4)), 1);   // domingo
});

test('clockText: curto "sábado 31 out.  09:05" e longo com a semana', () => {
  const agora = new Date(2026, 9, 31, 9, 5);
  assert.equal(clockText(agora, false), 'sábado 31 out.  09:05');  // o ICU do Node abrevia assim o sábado
  assert.equal(clockText(agora, true), 'sábado, 31 de outubro · semana 44 · 09:05');
});

test('volume: ícone pelos degraus, silenciado ou a zero sem som', () => {
  assert.equal(volumeIcon(50, true), ICON.volOff);
  assert.equal(volumeIcon(0, false), ICON.volOff);
  assert.equal(volumeIcon(33, false), ICON.volLow);
  assert.equal(volumeIcon(34, false), ICON.volMed);
  assert.equal(volumeIcon(66, false), ICON.volMed);
  assert.equal(volumeIcon(67, false), ICON.volHigh);
});

test('audioVista: o volume pendente da roda ganha ao real; silenciado esbatido; dica com o dispositivo', () => {
  const dev = { name: 'Colunas', volume: 40.4, isMuted: false };
  assert.equal(audioVista(dev, null).html, `<span class="ico" data-icon="${ICON.volMed}"></span><span class="">40%</span>`);
  assert.equal(audioVista(dev, 70).html, `<span class="ico" data-icon="${ICON.volHigh}"></span><span class="">70%</span>`);
  assert.equal(audioVista({ ...dev, isMuted: true }, null).html,
    `<span class="ico" data-icon="${ICON.volOff}"></span><span class="muted">40%</span>`);
  assert.equal(audioVista(dev, null).title, 'Colunas\nClique: definições rápidas · Roda: volume · Botão direito: silenciar');
});

test('proximoVolume: passos de 5 a partir do pendente ou do real arredondado, entre 0 e 100', () => {
  assert.equal(proximoVolume(null, 40.4, -100), 45);
  assert.equal(proximoVolume(null, 40.6, 100), 36);
  assert.equal(proximoVolume(45, 10, -1), 50);  // a roda acumula sobre o pendente
  assert.equal(proximoVolume(98, 0, -1), 100);
  assert.equal(proximoVolume(null, 2, 1), 0);
});

test('bateriaHTML: a cor vai no ícone e no texto', () => {
  assert.equal(bateriaHTML({ icone: 1, cor: 'var(--green)', texto: '80%' }),
    '<span class="ico" data-icon="1" style="--c: var(--green)"></span><span style="color: var(--green)">80%</span>');
});

test('awakeVista: "on" (com espaços) liga a chávena cheia; o resto é a chávena vazia', () => {
  assert.deepEqual(awakeVista('on\r\n'), {
    on: true, icon: ICON.coffee,
    title: 'PC mantido acordado — clique para voltar a permitir a suspensão (Alt+Esc, I)',
  });
  const desligada = awakeVista('off');
  assert.equal(desligada.on, false);
  assert.equal(desligada.icon, ICON.coffeeOutline);
  assert.match(desligada.title, /^Suspensão permitida/);
});

test('comandosDoBotao: workspace, sair do modo, pausa; restauro e outros botões não dão comandos aqui', () => {
  assert.deepEqual(comandosDoBotao({ ws: '3' }), ['focus --workspace 3']);
  assert.deepEqual(comandosDoBotao({ mode: 'resize' }), ['wm-disable-binding-mode --name resize']);
  assert.deepEqual(comandosDoBotao({ pause: '1' }), ['wm-toggle-pause']);
  assert.deepEqual(comandosDoBotao({ restore: 'id1' }), []);
});

test('sistemaFechou: só quando o modo sistema estava ativo e deixou de estar (o atalho da chávena vive nele)', () => {
  const modo = name => ({ name });
  assert.equal(sistemaFechou([modo('sistema')], []), true);
  assert.equal(sistemaFechou([modo('sistema')], [modo('resize')]), true);
  assert.equal(sistemaFechou([modo('sistema'), modo('resize')], [modo('sistema')]), false);
  assert.equal(sistemaFechou([], []), false);
  assert.equal(sistemaFechou([], [modo('sistema')]), false);
  assert.equal(sistemaFechou([modo('resize')], []), false);
  // a 1.ª leitura não tem "antes"; e o provider pode ainda não ter a lista
  assert.equal(sistemaFechou(undefined, [modo('sistema')]), false);
  assert.equal(sistemaFechou([modo('sistema')], undefined), true);
});

test('vigiaSistema: desenha sempre e reverifica a chávena só quando o modo sistema fecha', () => {
  const eventos = [];
  let modos;
  const ouvir = vigiaSistema(() => modos, () => eventos.push('chavena'), () => eventos.push('desenho'));
  modos = [{ name: 'sistema' }];
  ouvir();
  modos = [];
  ouvir();
  modos = undefined; // o provider ainda sem lista: não conta como fecho
  ouvir();
  assert.deepEqual(eventos, ['desenho', 'chavena', 'desenho', 'desenho']);
});
