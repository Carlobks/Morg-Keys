// Painel "Apps e arranque": funções puras (sem DOM), testadas com node --test.
import { appLabel, esc, SPECIAL } from '../comum/comum.mjs';

// --- Ícones (Nerd Font nf-md; confirmados na fonte JetBrainsMono NF) ---
// [palavra no nome, ícone, cor]
export const ICONS = [
  ['claude-code', 0xf489, 'var(--peach)'], ['terminal', 0xf489, 'var(--text)'], ['powershell', 0xf489, 'var(--blue)'],
  ['claude', 0xf06c4, 'var(--peach)'], ['chrome', 0xf02af, 'var(--yellow)'], ['edge', 0xf01e9, 'var(--teal)'],
  ['firefox', 0xf0239, 'var(--peach)'], ['arc', 0xf059f, 'var(--pink)'], ['explor', 0xf024b, 'var(--yellow)'],
  ['visual studio code', 0xf0a1e, 'var(--blue)'], ['vs code', 0xf0a1e, 'var(--blue)'], ['code', 0xf0a1e, 'var(--blue)'],
  ['spotify', 0xf04c7, 'var(--green)'], ['steam', 0xf04d3, 'var(--sky)'], ['discord', 0xf066f, 'var(--lavender)'],
  ['whatsapp', 0xf05a3, 'var(--green)'], ['youtube', 0xf05c3, 'var(--red)'], ['word', 0xf022c, 'var(--blue)'],
  ['excel', 0xf021b, 'var(--green)'], ['powerpoint', 0xf0227, 'var(--peach)'], ['outlook', 0xf0d22, 'var(--sky)'],
  ['teams', 0xf02bb, 'var(--lavender)'], ['calcul', 0xf00ec, 'var(--teal)'], ['defini', 0xf0493, 'var(--subtext0)'],
  ['settings', 0xf0493, 'var(--subtext0)'], ['notepad', 0xf0219, 'var(--green)'], ['bloco de notas', 0xf0219, 'var(--green)'],
  ['obsidian', 0xf0ebf, 'var(--mauve)'], ['github', 0xf02a4, 'var(--text)'], ['git', 0xf02a2, 'var(--peach)'],
  ['gmail', 0xf02ab, 'var(--red)'], ['mail', 0xf01ee, 'var(--sky)'], ['calend', 0xf00ed, 'var(--sky)'],
  ['slack', 0xf04b1, 'var(--pink)'], ['docker', 0xf0868, 'var(--blue)'], ['python', 0xf0320, 'var(--yellow)'],
  ['node', 0xf0399, 'var(--green)'], ['store', 0xf0110, 'var(--blue)'], ['loja', 0xf0110, 'var(--blue)'],
  ['câmara', 0xf0100, 'var(--subtext0)'], ['camera', 0xf0100, 'var(--subtext0)'], ['foto', 0xf02e9, 'var(--pink)'],
  ['photo', 0xf02e9, 'var(--pink)'], ['music', 0xf075a, 'var(--pink)'], ['música', 0xf075a, 'var(--pink)'],
  ['vídeo', 0xf0567, 'var(--red)'], ['video', 0xf0567, 'var(--red)'], ['pdf', 0xf0226, 'var(--red)'],
  ['acrobat', 0xf0226, 'var(--red)'], ['game', 0xf0297, 'var(--mauve)'], ['xbox', 0xf0297, 'var(--green)'],
  ['riot', 0xf0297, 'var(--red)'], ['segur', 0xf0483, 'var(--teal)'], ['onedrive', 0xf015f, 'var(--sky)'],
  ['impress', 0xf042a, 'var(--subtext0)'], ['print', 0xf042a, 'var(--subtext0)'], ['sql', 0xf01bc, 'var(--yellow)'],
  ['monitor', 0xf0379, 'var(--teal)'], ['raycast', 0xf0349, 'var(--red)'], ['windows', 0xf05b3, 'var(--blue)'],
];

// [código do ícone, cor] para uma app do apps.txt (sites: pelo nome do domínio).
export function iconFor(value) {
  const v = String(value).toLowerCase();
  if (v.startsWith('web:')) {
    const host = appLabel(value).toLowerCase();
    const hit = ICONS.find(([w]) => host.includes(w));
    return hit ? [hit[1], hit[2]] : [0xf059f, 'var(--sky)'];
  }
  const name = (SPECIAL[v] ?? v).toLowerCase();
  const hit = ICONS.find(([w]) => (v === w) || name.includes(w));
  return hit ? [hit[1], hit[2]] : [0xf003b, 'var(--lavender)'];
}

export const ico = value => {
  const [code, color] = iconFor(value);
  return `<span class="ico" data-icon="${code}" style="--ic:${color}"></span>`;
};

// --- Teclas ---
export const KEY_ROWS = ['QWERTYUIOP', 'ASDFGHJKL', 'ZXCVBNM'];
export const SPECIAL_KEYS = [['alt+enter', 'Alt Enter'], ['alt+shift+enter', 'Alt Shift Enter']];
export const keyId = l => `alt+shift+${l.toLowerCase()}`;
// "alt+shift+b" -> "Alt+Shift+B" (como no apps.txt e no guia).
export const keyLong = id => id.split('+').map(p => ({ alt: 'Alt', shift: 'Shift', enter: 'Enter', space: 'Space' })[p] ?? p.toUpperCase()).join('+');

// Uma tecla do teclado desenhado: do sistema (fixed), com app (has) ou livre; sel = escolhida para enviar.
export function keyHtml(id, cap, wide, state, sel) {
  const fixed = state.fixed.includes(id);
  const has = state.keys.find(k => k.key === id);
  const isSel = sel?.kind === 'key' && sel.key === id;
  const cls = ['key', wide && 'wide', fixed ? 'fixed' : has ? 'has' : 'free', isSel && 'sel'].filter(Boolean).join(' ');
  const what = fixed ? '<span class="ico" data-icon="983870" style="--ic:var(--overlay0)"></span><span>sistema</span>'
    : has ? `${ico(has.value)}<span>${esc(appLabel(has.value))}</span>` : '';
  const data = has && !fixed ? ` data-kind="key" data-value="${esc(has.value)}" data-label="${esc(appLabel(has.value))}"` : '';
  return `<div class="${cls}" data-key="${id}"${data} title="${esc(has ? `${cap}: ${appLabel(has.value)}` : fixed ? `${cap}: usado pelo sistema` : `${cap}: livre`)}">` +
    `<span class="cap">${esc(cap)}</span><span class="what">${what}</span>` +
    `${has && !fixed ? `<button class="x" data-unkey="${id}" title="Tirar o atalho">✕</button>` : ''}</div>`;
}

// Teclado inteiro: 3 filas de letras + Alt Enter, Alt Shift Enter e os atalhos do apps.txt que não
// estão no teclado desenhado (ex.: Alt+B sem Shift).
export function keyboardHtml(state, sel) {
  const drawn = new Set([...KEY_ROWS.join('')].map(keyId).concat(SPECIAL_KEYS.map(([id]) => id)));
  const extra = state.keys.filter(k => !drawn.has(k.key)).map(k => [k.key, keyLong(k.key).replace(/\+/g, ' ')]);
  return KEY_ROWS.map(r => `<div class="krow">${[...r].map(l => keyHtml(keyId(l), l, false, state, sel)).join('')}</div>`).join('') +
    `<div class="krow special">${[...SPECIAL_KEYS, ...extra].map(([id, cap]) => keyHtml(id, cap, true, state, sel)).join('')}</div>`;
}

// --- Pedidos ao bar_helper.py: a operação vai em base64 "url-safe" (sem + / =) para passar no argsRegex ---
export const b64 = s => btoa(String.fromCharCode(...new TextEncoder().encode(s)))
  .replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
export const unb64 = s => new TextDecoder().decode(Uint8Array.from(atob(s.replace(/-/g, '+').replace(/_/g, '/')), c => c.charCodeAt(0)));

// --- Desenho da lista e dos workspaces (o apps.mjs só põe o HTML na página) ---
// Lista da esquerda (Especiais, Sites, Menu Iniciar) filtrada pelo texto do filtro: {html, count}.
// Todos os elementos escolhíveis têm data-kind (app | key | ws), data-value e data-label.
export function listaHtml(state, startApps, extraSites, sel, filtro) {
  const q = String(filtro).trim().toLowerCase();
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
    return `<div class="group">${esc(title)}</div>${shown.map(it => {
      const k = used.get(it.value.toLowerCase());
      const isSel = sel?.kind === 'app' && sel.value === it.value;
      return `<div class="app${isSel ? ' sel' : ''}" data-kind="app" data-value="${esc(it.value)}" data-label="${esc(it.label)}">` +
        `${ico(it.value)}<span class="lb">${esc(it.label)}</span>` +
        `${k ? `<span class="used">${esc(keyLong(k))}</span>` : ''}</div>`;
    }).join('')}`;
  }).join('');
  return {
    html: html || `<div class="empty">${startApps.length ? 'Nenhuma app com esse nome.' : 'A carregar as apps do menu Iniciar…'}</div>`,
    count: startApps.length ? `${startApps.length} no menu Iniciar` : '',
  };
}

// As caixas dos workspaces: 1–10 sempre; outros (ex.: o scratchpad S, gravado com Alt+Esc G) só se tiverem apps.
export function workspacesHtml(state, sel) {
  const names = [...Array.from({ length: 10 }, (_, i) => String(i + 1)),
                 ...[...new Set(state.workspaces.map(w => w.workspace))].filter(w => !/^([1-9]|10)$/.test(w))];
  return names.map(ws => {
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
}

// --- Respostas do bar_helper.py e mensagens ---
export const textoDoErro = err => err?.message ?? err;
// Resposta de um pedido -> [texto, tipo] para a linha de estado.
export const estadoDaResposta = (res, okText) =>
  (res.ok ? [okText ?? '✓ Guardado', 'ok'] : [res.error || 'Erro desconhecido.', 'err']);

// --- Escolher e enviar: o que fazer, sem mexer na página ---
// Cada função devolve null (nada escolhido) ou {limpar, erro?, op?, ok?}: limpar = largar a escolha;
// erro = mensagem; op = pedido ao bar_helper.py (com o texto `ok` a mostrar quando correr bem).
export const escolhaDosDados = d => ({ kind: d.kind, value: d.value, label: d.label, key: d.key, ws: d.ws,
                                       index: d.index !== undefined ? Number(d.index) : undefined });
export const mesmaEscolha = (a, b) => !!a && a.kind === b.kind && a.value === b.value && a.key === b.key && a.index === b.index;
const expect = s => ({ expect_ws: s.ws, expect_label: s.label });

export function enviarParaTecla(s, key, state) {
  if (!s) return null;
  if (state.fixed.includes(key)) return { limpar: false, erro: `${keyLong(key)} é usado pelo sistema: escolha outra tecla.` };
  if (s.kind === 'key' && s.key === key) return { limpar: true };
  if (!s.value) return { limpar: true, erro: 'Esta app não tem um nome do menu Iniciar: escolha-a na lista.' };
  const o = { op: 'key', key, value: s.value };
  if (s.kind === 'key') o.from = s.key;  // vinha de outra tecla: muda-se de lá
  return { limpar: true, op: o, ok: `✓ ${appLabel(s.value)} em ${keyLong(key)}` };
}

export function enviarParaWorkspace(s, ws) {
  if (!s) return null;
  if (s.kind === 'ws') {
    if (s.ws === ws) return { limpar: true };
    return { limpar: true, op: { op: 'ws-move', index: s.index, ws, ...expect(s) }, ok: `✓ Agora abre no workspace ${ws}` };
  }
  if (!s.value) return { limpar: true };
  const label = s.label || appLabel(s.value);
  return { limpar: true, op: { op: 'ws-add', ws, value: s.value, label }, ok: `✓ ${label} abre no workspace ${ws}` };
}

export function tirarEscolha(s, state) {
  if (!s) return null;
  if (s.kind === 'key') return { limpar: true, op: { op: 'unkey', key: s.key }, ok: '✓ Atalho tirado' };
  if (s.kind === 'ws') return { limpar: true, op: { op: 'ws-del', index: s.index, ...expect(s) }, ok: '✓ Já não abre no arranque' };
  const k = state.keys.find(k => k.value.toLowerCase() === s.value.toLowerCase());
  if (k) return { limpar: true, op: { op: 'unkey', key: k.key }, ok: `✓ ${s.label} já não tem atalho` };
  return { limpar: true, erro: `${s.label} não tem atalho para tirar.` };
}

// Botões ✕: tirar a tecla, ou tirar a app de um workspace (com os dados do chip, para o painel desatualizado).
export const tirarTecla = key => ({ limpar: true, op: { op: 'unkey', key }, ok: '✓ Atalho tirado' });
export const tirarDoWorkspace = (index, chip) =>
  ({ limpar: true, op: { op: 'ws-del', index, ...expect(chip) }, ok: '✓ Já não abre no arranque' });

// A escolher o destino: a tecla diz para onde enviar. Devolve [ação, alvo] ou null (tecla sem efeito).
export function destinoDaTecla(key, shiftKey) {
  if (key === 'Escape') return ['cancelar'];
  if (key === 'Delete' || key === 'Backspace') return ['tirar'];
  if (key === 'Enter') return ['tecla', shiftKey ? 'alt+shift+enter' : 'alt+enter'];
  if (/^[0-9]$/.test(key)) return ['workspace', key === '0' ? '10' : key];
  if (/^[a-z]$/i.test(key)) return ['tecla', keyId(key)];
  return null;
}

// Setas na lista: a linha seguinte ou a anterior, sem sair da lista.
export const moverCursor = (cursor, total, key) =>
  Math.max(0, Math.min(total - 1, cursor + (key === 'ArrowDown' ? 1 : -1)));

// "+ site": o endereço escrito -> valor "web: …" (sem esquema, assume https). null = vazio.
export function siteDoEndereco(texto) {
  let url = String(texto).trim();
  if (!url) return null;
  if (!/^https?:\/\//i.test(url)) url = `https://${url}`;
  try { new URL(url); } catch { return { erro: 'Endereço inválido.' }; }
  return { value: `web: ${url}` };
}
