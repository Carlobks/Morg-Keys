// Painel "Apps e arranque" (Alt+Esc, C): desenho, escolher e enviar, e a ligação ao Zebar.
// As funções puras estão em apps-logica.mjs (testadas com node --test).
import { appLabel, drawIcons as drawIconsComum, esc } from '../comum/comum.mjs';
import { chamadaDeExemplo } from './apps-exemplo.mjs';
import { b64, ico, keyboardHtml, keyId, keyLong } from './apps-logica.mjs';

const $ = id => document.getElementById(id);
const drawIcons = (root = document) => drawIconsComum(root, 22);

// --- Estado ---
let state = { keys: [], fixed: [], workspaces: [], undo: 0 };
let startApps = [];          // [{name, value}] do menu Iniciar
const extraSites = [];       // sites acrescentados nesta sessão (ainda sem tecla nem workspace)
let call = null;             // (args) => Promise<objeto JSON> — Zebar ou exemplo
let sel = null;              // o que está escolhido para enviar (ou null)
let cursor = 0;              // linha da lista onde estão as setas

function setStatus(text, kind = '') {
  const el = $('status');
  el.textContent = text;
  el.className = kind;
  clearTimeout(setStatus.t);
  if (kind === 'ok') setStatus.t = setTimeout(() => (el.textContent = ''), 2500);
}

// --- Desenho ---
// Todos os elementos escolhíveis têm data-kind (app | key | ws), data-value e data-label.
function renderList() {
  const q = $('filter').value.trim().toLowerCase();
  const used = new Map();
  for (const k of state.keys) used.set(k.value.toLowerCase(), k.key);
  const hits = it => !q || it.label.toLowerCase().includes(q) || it.value.toLowerCase().includes(q);
  const sites = [...new Set([...state.keys.map(k => k.value), ...state.workspaces.map(w => w.value || ''), ...extraSites]
    .filter(v => /^web:/i.test(v)))].map(v => ({ value: v, label: appLabel(v) }));
  const groups = [
    ['Especiais', ['terminal', 'claude-code', 'explorador'].map(v => ({ value: v, label: appLabel(v) }))],
    ['Sites', sites],
    ['Menu Iniciar', startApps.map(a => ({ value: a.value, label: a.name }))],
  ];
  const html = groups.map(([title, items]) => {
    const shown = items.filter(hits);
    if (!shown.length) return '';
    return `<div class="group">${esc(title)}</div>` + shown.map(it => {
      const k = used.get(it.value.toLowerCase());
      const isSel = sel?.kind === 'app' && sel.value === it.value;
      return `<div class="app${isSel ? ' sel' : ''}" data-kind="app" data-value="${esc(it.value)}" data-label="${esc(it.label)}">` +
        `${ico(it.value)}<span class="lb">${esc(it.label)}</span>` +
        `${k ? `<span class="used">${esc(keyLong(k))}</span>` : ''}</div>`;
    }).join('');
  }).join('');
  $('list').innerHTML = html || `<div class="empty">${startApps.length ? 'Nenhuma app com esse nome.' : 'A carregar as apps do menu Iniciar…'}</div>`;
  $('count').textContent = startApps.length ? `${startApps.length} no menu Iniciar` : '';
  cursor = Math.min(cursor, $('list').querySelectorAll('.app').length - 1);
  paintCursor(false);
  drawIcons($('list'));
}

function renderKeys() {
  $('kb').innerHTML = keyboardHtml(state, sel);
  drawIcons($('kb'));
}

function renderWorkspaces() {
  // 1–10 sempre; outros (ex.: o scratchpad S, gravado com Alt+Esc G) só se tiverem apps.
  const names = [...Array.from({ length: 10 }, (_, i) => String(i + 1)),
                 ...[...new Set(state.workspaces.map(w => w.workspace))].filter(w => !/^([1-9]|10)$/.test(w))];
  $('wsgrid').innerHTML = names.map(ws => {
    const items = state.workspaces.filter(w => w.workspace === ws);
    return `<div class="box${items.length ? ' has' : ''}" data-ws="${esc(ws)}">` +
      `<div class="head"><kbd>${esc(ws)}</kbd><span>${items.length ? `${items.length} ${items.length === 1 ? 'app' : 'apps'}` : ''}</span></div>` +
      (items.length ? items.map(w => {
        const value = w.value || w.process || w.label;
        const isSel = sel?.kind === 'ws' && sel.index === w.index;
        return `<div class="chip${isSel ? ' sel' : ''}" data-kind="ws" data-index="${w.index}" data-ws="${esc(ws)}" data-value="${esc(w.value || '')}" data-label="${esc(w.label)}" title="${esc(w.label)}">` +
          `${ico(value)}<span>${esc(w.label)}</span><button class="x" data-wsdel="${w.index}" title="Não abrir no arranque">✕</button></div>`;
      }).join('') : '<div class="hint">vazio</div>') +
      '</div>';
  }).join('');
  drawIcons($('wsgrid'));
}

function render() {
  renderList();
  renderKeys();
  renderWorkspaces();
  $('undo').disabled = !state.undo;
}

// --- Pedidos ao bar_helper.py (um de cada vez, pela ordem) ---
let queue = Promise.resolve();
function request(args, okText) {
  queue = queue.then(async () => {
    document.body.classList.add('busy');
    try {
      const res = await call(args);
      if (res.state) state = res.state;
      if (res.ok) setStatus(okText ?? '✓ Guardado', 'ok');
      else setStatus(res.error || 'Erro desconhecido.', 'err');
    } catch (err) {
      setStatus(`Erro: ${err?.message ?? err}`, 'err');
    } finally {
      document.body.classList.remove('busy');
      render();
    }
  });
  return queue;
}
const op = (o, okText) => request(['do', b64(JSON.stringify(o))], okText);
const busy = () => document.body.classList.contains('busy');

async function loadAll() {
  await request(['state'], '');
  try {
    const res = await call(['apps']);
    if (res.ok) { startApps = res.apps; renderList(); }
  } catch (err) {
    setStatus(`Não consegui ler o menu Iniciar: ${err?.message ?? err}`, 'err');
  }
}

// --- Escolher e enviar (rato ou teclado; sem arrastar: o Zebar/Tauri não o deixa) ---
// 1) escolher: clique numa app da lista, numa tecla com app ou numa app de um workspace
//    (teclado: ↑ ↓ na lista e Enter); 2) destino: clique numa tecla ou num workspace
//    (teclado: letra = Alt+Shift+letra, 1–0 = workspace, Enter = Alt+Enter,
//    Shift+Enter = Alt+Shift+Enter, Del = tirar); Esc cancela.
function readSel(el) {
  return { kind: el.dataset.kind, value: el.dataset.value, label: el.dataset.label,
           key: el.dataset.key, ws: el.dataset.ws,
           index: el.dataset.index !== undefined ? Number(el.dataset.index) : undefined };
}
function select(s) {
  sel = s;
  document.body.classList.toggle('sending', !!sel);
  if (sel) {
    $('sendico').innerHTML = ico(sel.value || sel.label);
    $('sendname').textContent = sel.label || appLabel(sel.value);
    drawIcons($('send'));
    document.activeElement?.blur();
  } else {
    $('filter').focus();
  }
  render();
}
const expect = s => ({ expect_ws: s.ws, expect_label: s.label });

function sendToKey(key) {
  const s = sel;
  if (!s) return;
  if (state.fixed.includes(key)) return setStatus(`${keyLong(key)} é usado pelo sistema: escolha outra tecla.`, 'err');
  select(null);
  if (s.kind === 'key' && s.key === key) return;
  if (!s.value) return setStatus('Esta app não tem um nome do menu Iniciar: escolha-a na lista.', 'err');
  const o = { op: 'key', key, value: s.value };
  if (s.kind === 'key') o.from = s.key;  // vinha de outra tecla: muda-se de lá
  op(o, `✓ ${appLabel(s.value)} em ${keyLong(key)}`);
}
function sendToWorkspace(ws) {
  const s = sel;
  if (!s) return;
  select(null);
  if (s.kind === 'ws') {
    if (s.ws === ws) return;
    return op({ op: 'ws-move', index: s.index, ws, ...expect(s) }, `✓ Agora abre no workspace ${ws}`);
  }
  if (!s.value) return;
  op({ op: 'ws-add', ws, value: s.value, label: s.label || appLabel(s.value) }, `✓ ${s.label || appLabel(s.value)} abre no workspace ${ws}`);
}
function removeSel() {
  const s = sel;
  if (!s) return;
  select(null);
  if (s.kind === 'key') return op({ op: 'unkey', key: s.key }, '✓ Atalho tirado');
  if (s.kind === 'ws') return op({ op: 'ws-del', index: s.index, ...expect(s) }, '✓ Já não abre no arranque');
  const k = state.keys.find(k => k.value.toLowerCase() === s.value.toLowerCase());
  if (k) return op({ op: 'unkey', key: k.key }, `✓ ${s.label} já não tem atalho`);
  setStatus(`${s.label} não tem atalho para tirar.`, 'err');
}

document.addEventListener('click', e => {
  if (busy()) return;
  const un = e.target.closest?.('[data-unkey]');
  if (un) { select(null); return op({ op: 'unkey', key: un.dataset.unkey }, '✓ Atalho tirado'); }
  const del = e.target.closest?.('[data-wsdel]');
  if (del) {
    const chip = del.closest('.chip');
    select(null);
    return op({ op: 'ws-del', index: Number(del.dataset.wsdel), ...expect(readSel(chip)) }, '✓ Já não abre no arranque');
  }
  if (sel) {  // a escolher o destino
    const key = e.target.closest?.('.key');
    if (key) return sendToKey(key.dataset.key);
    const box = e.target.closest?.('.box');
    if (box) return sendToWorkspace(box.dataset.ws);
  }
  const item = e.target.closest?.('[data-kind]');
  if (item) {
    const s = readSel(item);
    if (sel && sel.kind === s.kind && sel.value === s.value && sel.key === s.key && sel.index === s.index) return select(null);
    return select(s);
  }
  if (sel && !e.target.closest?.('header, footer, #site')) select(null);  // clique no vazio cancela
});
$('cancel').addEventListener('click', e => { e.stopPropagation(); select(null); });
$('undo').addEventListener('click', () => { select(null); request(['undo'], '✓ Desfeito'); });

// Cursor do teclado na lista (setas): a linha fica marcada; Enter escolhe-a.
function paintCursor(scroll = true) {
  const items = [...$('list').querySelectorAll('.app')];
  items.forEach((el, i) => el.classList.toggle('cursor', i === cursor));
  if (scroll && items[cursor]) items[cursor].scrollIntoView({ block: 'nearest' });
}

// + site: o endereço vira um "app" web: que se escolhe como os outros.
$('site').addEventListener('submit', e => {
  e.preventDefault();
  let url = $('url').value.trim();
  if (!url) return;
  if (!/^https?:\/\//i.test(url)) url = `https://${url}`;
  try { new URL(url); } catch { return setStatus('Endereço inválido.', 'err'); }
  const value = `web: ${url}`;
  if (!extraSites.includes(value)) extraSites.push(value);
  $('url').value = '';
  $('filter').value = '';
  select({ kind: 'app', value, label: appLabel(value) });  // já fica escolhido: falta o destino
  setStatus(`${appLabel(value)}: escolha agora uma tecla ou um workspace.`, 'ok');
});
$('filter').addEventListener('input', () => { cursor = 0; renderList(); });

// --- Zebar ou navegador ---
let close = () => window.close();
if (location.protocol === 'file:' || new URLSearchParams(location.search).has('preview')) {
  document.body.classList.add('standalone', 'open');
  call = chamadaDeExemplo();
  loadAll();
} else {
  const CUP = { x: Math.round(screen.width / 2) - 72, y: 14 };
  const OPEN_MS = 480;
  const CLOSE_MS = 260;
  let win = null;
  let shown = 'hidden'; // hidden | open | closing
  let watch = null;
  let closeTimer = null;
  let hideWindow = () => {};
  try {
    const zebar = await import('../vendor/zebar-3.3.1.mjs');
    win = zebar.currentWidget().tauriWindow;
    // py.exe (com saída) para os pedidos; pyw.exe para esconder. Os argumentos
    // têm de bater com o argsRegex do widget "apps" no zpack.json (A8).
    const PY = 'C:\\Windows\\py.exe';
    const PYW = 'C:\\Windows\\pyw.exe';
    // O caminho vem do HTML (data-helper): o instalador só troca {{HOME}} em .html, não em .mjs.
    const HELPER = document.documentElement.dataset.helper;
    call = async args => JSON.parse((await zebar.shellExec(PY, ['-I', HELPER, 'panel', ...args])).stdout);
    // Esconder passa sempre pelo bar_helper.py (um só dono da visibilidade, A9).
    hideWindow = () => zebar.shellExec(PYW, ['-I', HELPER, 'panel-hide']).catch(console.error);

    const pos = await win.outerPosition();
    const scale = (await win.scaleFactor()) || 1;
    document.documentElement.style.setProperty('--ox', `${CUP.x - pos.x / scale}px`);
    document.documentElement.style.setProperty('--oy', `${CUP.y - pos.y / scale}px`);
    await win.hide(); // pré-carregado: o Alt+Esc, C (bar_helper.py panel) mostra-o
  } catch (err) {
    console.error('Zebar API indisponível:', err);
    setStatus(`Erro Zebar: ${err?.message ?? err}`, 'err');
  }

  close = () => {
    if (shown !== 'open') return;
    shown = 'closing';
    clearInterval(watch);
    document.body.classList.remove('open');
    closeTimer = setTimeout(() => { closeTimer = null; hideWindow(); shown = 'hidden'; }, CLOSE_MS);
  };

  window.addEventListener('focus', () => {
    if (shown === 'open') return;
    clearTimeout(closeTimer);
    closeTimer = null;
    shown = 'open';
    $('filter').value = '';
    setStatus('');
    sel = null;
    document.body.classList.remove('sending');
    cursor = 0;
    loadAll(); // apps.txt e layout.json podem ter mudado (Alt+Esc, G; outra app)
    $('filter').focus();
    document.body.classList.remove('open');
    void document.body.offsetWidth;
    requestAnimationFrame(() => document.body.classList.add('open'));

    // Clicar fora fecha (o WebView2 não dá "blur" fiável: pergunta-se à janela).
    // Enquanto um pedido está a correr, não fecha.
    clearInterval(watch);
    const since = performance.now();
    watch = setInterval(async () => {
      if (!win || document.body.classList.contains('busy') || performance.now() - since < OPEN_MS) return;
      if (!(await win.isFocused())) close();
    }, 150);
  });
}

$('close').addEventListener('click', () => close());
document.addEventListener('keydown', e => {
  if (e.ctrlKey && e.key.toLowerCase() === 'z') {
    e.preventDefault();
    if (!$('undo').disabled && !busy()) { select(null); request(['undo'], '✓ Desfeito'); }
    return;
  }
  // A escolher o destino: as teclas dizem para onde enviar.
  if (sel) {
    e.preventDefault();
    if (busy()) return;
    if (e.key === 'Escape') return select(null);
    if (e.key === 'Delete' || e.key === 'Backspace') return removeSel();
    if (e.key === 'Enter') return sendToKey(e.shiftKey ? 'alt+shift+enter' : 'alt+enter');
    if (/^[0-9]$/.test(e.key)) return sendToWorkspace(e.key === '0' ? '10' : e.key);
    if (/^[a-z]$/i.test(e.key)) return sendToKey(keyId(e.key));
    return;
  }
  if (e.key === 'Escape') {
    if (document.activeElement === $('url') && $('url').value) { $('url').value = ''; return; }
    if ($('filter').value) { $('filter').value = ''; cursor = 0; renderList(); return; }
    return close();
  }
  if (document.activeElement === $('url')) return;  // a escrever um site
  const items = [...$('list').querySelectorAll('.app')];
  if (e.key === 'ArrowDown' || e.key === 'ArrowUp') {
    e.preventDefault();
    cursor = Math.max(0, Math.min(items.length - 1, cursor + (e.key === 'ArrowDown' ? 1 : -1)));
    return paintCursor();
  }
  if (e.key === 'Enter' && items[cursor]) {
    e.preventDefault();
    return select(readSel(items[cursor]));
  }
  if (e.key.length === 1 && !e.ctrlKey && !e.altKey && document.activeElement !== $('filter')) {
    $('filter').focus(); // escrever em qualquer lado começa a procurar
  }
});
render();
drawIcons();
