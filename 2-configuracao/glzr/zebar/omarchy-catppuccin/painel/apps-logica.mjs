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
    `${has && !fixed ? '<button class="x" data-unkey="' + id + '" title="Tirar o atalho">✕</button>' : ''}</div>`;
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
