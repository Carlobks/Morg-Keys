// Painel "Apps e arranque" (Alt+Esc, C): a ligação à página (DOM) e ao Zebar.
// O que decidir e desenhar está em apps-logica.mjs (testado com node --test); este ficheiro só liga os
// eventos da página a essas funções e por isso fica fora da cobertura (verifica-se à mão com ?preview,
// docs/validacao-manual.md, "Excluído da cobertura").
import { appLabel, comecaAProcurar, drawIcons as drawIconsComum, ePreVisualizacao, origemDaChavena } from '../comum/comum.mjs';
import { chamadaDeExemplo } from './apps-exemplo.mjs';
import {
  b64, destinoDaTecla, enviarParaTecla, enviarParaWorkspace, escolhaDosDados, estadoDaResposta, ico, keyboardHtml,
  listaHtml, mesmaEscolha, moverCursor, siteDoEndereco, textoDoErro, tirarDoWorkspace, tirarEscolha, tirarTecla,
  workspacesHtml,
} from './apps-logica.mjs';

// Cola com o DOM e o Zebar (WebView2), sem página no node --test: fora da cobertura até ao fim.
/* node:coverage disable */
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

// --- Desenho (o HTML vem de apps-logica.mjs) ---
function renderList() {
  const { html, count } = listaHtml(state, startApps, extraSites, sel, $('filter').value);
  $('list').innerHTML = html;
  $('count').textContent = count;
  cursor = Math.min(cursor, $('list').querySelectorAll('.app').length - 1);
  paintCursor(false);
  drawIcons($('list'));
}

function renderKeys() {
  $('kb').innerHTML = keyboardHtml(state, sel);
  drawIcons($('kb'));
}

function renderWorkspaces() {
  $('wsgrid').innerHTML = workspacesHtml(state, sel);
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
      setStatus(...estadoDaResposta(res, okText));
    } catch (err) {
      setStatus(`Erro: ${textoDoErro(err)}`, 'err');
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
    setStatus(`Não consegui ler o menu Iniciar: ${textoDoErro(err)}`, 'err');
  }
}

// --- Escolher e enviar (rato ou teclado; sem arrastar: o Zebar/Tauri não o deixa) ---
// 1) escolher: clique numa app da lista, numa tecla com app ou numa app de um workspace
//    (teclado: ↑ ↓ na lista e Enter); 2) destino: clique numa tecla ou num workspace
//    (teclado: letra = Alt+Shift+letra, 1–0 = workspace, Enter = Alt+Enter,
//    Shift+Enter = Alt+Shift+Enter, Del = tirar); Esc cancela.
const readSel = el => escolhaDosDados(el.dataset);
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

// Aplica a decisão de apps-logica.mjs ({limpar, erro, op, ok} ou null).
function fazer(r) {
  if (!r) return;
  if (r.limpar) select(null);
  if (r.erro) setStatus(r.erro, 'err');
  if (r.op) op(r.op, r.ok);
}
const sendToKey = key => fazer(enviarParaTecla(sel, key, state));
const sendToWorkspace = ws => fazer(enviarParaWorkspace(sel, ws));
const removeSel = () => fazer(tirarEscolha(sel, state));

document.addEventListener('click', e => {
  if (busy()) return;
  const un = e.target.closest?.('[data-unkey]');
  if (un) return fazer(tirarTecla(un.dataset.unkey));
  const del = e.target.closest?.('[data-wsdel]');
  if (del) return fazer(tirarDoWorkspace(Number(del.dataset.wsdel), readSel(del.closest('.chip'))));
  if (sel) {  // a escolher o destino
    const key = e.target.closest?.('.key');
    if (key) return sendToKey(key.dataset.key);
    const box = e.target.closest?.('.box');
    if (box) return sendToWorkspace(box.dataset.ws);
  }
  const item = e.target.closest?.('[data-kind]');
  if (item) {
    const s = readSel(item);
    return select(mesmaEscolha(sel, s) ? null : s);
  }
  if (sel && !e.target.closest?.('header, footer, #site')) select(null);  // clique no vazio cancela
});
$('cancel').addEventListener('click', e => { e.stopPropagation(); select(null); });
$('undo').addEventListener('click', () => { select(null); request(['undo'], '✓ Desfeito'); });

// Cursor do teclado na lista (setas): a linha fica marcada; Enter escolhe-a.
function paintCursor(scroll = true) {
  const items = [...$('list').querySelectorAll('.app')];
  items.forEach((el, i) => { el.classList.toggle('cursor', i === cursor); });
  if (scroll && items[cursor]) items[cursor].scrollIntoView({ block: 'nearest' });
}

// + site: o endereço vira um "app" web: que se escolhe como os outros.
$('site').addEventListener('submit', e => {
  e.preventDefault();
  const site = siteDoEndereco($('url').value);
  if (!site) return;
  if (site.erro) return setStatus(site.erro, 'err');
  const { value } = site;
  if (!extraSites.includes(value)) extraSites.push(value);
  $('url').value = '';
  $('filter').value = '';
  select({ kind: 'app', value, label: appLabel(value) });  // já fica escolhido: falta o destino
  setStatus(`${appLabel(value)}: escolha agora uma tecla ou um workspace.`, 'ok');
});
$('filter').addEventListener('input', () => { cursor = 0; renderList(); });

// --- Zebar ou navegador ---
let close = () => window.close();
if (ePreVisualizacao(location)) {
  document.body.classList.add('standalone', 'open');
  call = chamadaDeExemplo();
  loadAll();
} else {
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

    const { ox, oy } = origemDaChavena(screen.width, await win.outerPosition(), await win.scaleFactor());
    document.documentElement.style.setProperty('--ox', ox);
    document.documentElement.style.setProperty('--oy', oy);
    await win.hide(); // pré-carregado: o Alt+Esc, C (bar_helper.py panel) mostra-o
  } catch (err) {
    console.error('Zebar API indisponível:', err);
    setStatus(`Erro Zebar: ${textoDoErro(err)}`, 'err');
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
    const [acao, alvo] = destinoDaTecla(e.key, e.shiftKey) ?? [];
    if (acao === 'cancelar') return select(null);
    if (acao === 'tirar') return removeSel();
    if (acao === 'tecla') return sendToKey(alvo);
    if (acao === 'workspace') return sendToWorkspace(alvo);
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
    cursor = moverCursor(cursor, items.length, e.key);
    return paintCursor();
  }
  if (e.key === 'Enter' && items[cursor]) {
    e.preventDefault();
    return select(readSel(items[cursor]));
  }
  if (comecaAProcurar(e, document.activeElement === $('filter'))) {
    $('filter').focus(); // escrever em qualquer lado começa a procurar
  }
});
render();
drawIcons();
/* node:coverage enable */
