// Lógica da barra (bar.html) sem DOM: o HTML de cada zona, o relógio, o volume, a chávena e os comandos
// dos botões. Testa-se com node --test (tests/bar-logica.test.mjs); a cola com o DOM e o Zebar fica no
// bar.html (docs/validacao-manual.md). Os caminhos com {{HOME}} ficam no HTML: o instalador só troca os
// marcadores em .html, .css, .json, .py, .ps1, .txt e .yaml.

// Ícones Nerd Font (família nf-md / nf-oct da fonte JetBrainsMono NF).
export const ICON = {
  menu: 0xf003b, cpu: 0xf4bc, memory: 0xe266,
  volOff: 0xf0581, volLow: 0xf057f, volMed: 0xf0580, volHigh: 0xf057e,
  ethernet: 0xf0200, wifi: 0xf05a9, wifiOff: 0xf05aa, vpn: 0xf0ccc,
  coffee: 0xf0176, coffeeOutline: 0xf06ca, app: 0xf0614,
};

// Nome curto e ícone por processo, para as etiquetas das minimizadas.
export const APPS = {
  claude: { icon: 0xf06c4, name: 'Claude' },
  chrome: { icon: 0xf02af, name: 'Chrome' },
  Arc: { icon: 0xf059f, name: 'Arc' },
  msedge: { icon: 0xf01e9, name: 'Edge' },
  Obsidian: { icon: 0xf0ebf, name: 'Obsidian' },
  explorer: { icon: 0xf0256, name: 'Explorador' },
  WindowsTerminal: { icon: 0xf489, name: 'Terminal' },
};
export const SCRATCH = 'S'; // workspace "scratchpad" (Alt+º)

export const esc = s => String(s ?? '').replace(/[&<>"']/g, c => `&#${c.charCodeAt(0)};`);
export const ico = code => `<span class="ico" data-icon="${code}"></span>`;

export function workspacesHTML(workspaces) {
  return workspaces
    // O scratchpad só aparece quando está aberto.
    .filter(ws => ws.name !== SCRATCH || ws.isDisplayed)
    .map(ws => {
      const cls = [
        'workspace',
        ws.hasFocus ? 'focused' : '',
        ws.children.length === 0 ? 'empty' : '',
        ws.name === SCRATCH ? 'scratch' : '',
      ].join(' ');
      return `<button class="${cls}" data-ws="${esc(ws.name)}">${esc(ws.displayName ?? ws.name)}</button>`;
    })
    .join('');
}

// Janelas minimizadas do workspace visível (a árvore toda): uma etiqueta clicável cada.
export function minimizadas(workspace) {
  const lista = [];
  const walk = c => {
    if (c.type === 'window' && c.state?.type === 'minimized') lista.push(c);
    (c.children ?? []).forEach(walk);
  };
  if (workspace) walk(workspace);
  return lista;
}

export function minimizedHTML(janelas) {
  return janelas
    .map(w => {
      const app = APPS[w.processName] ?? { icon: ICON.app, name: w.processName };
      return `<button class="min-chip" data-restore="${esc(w.id)}" title="${esc(w.title)}\nClique para restaurar">` +
        `${ico(app.icon)}${esc(app.name)}</button>`;
    })
    .join('');
}

export function modesHTML(glazewm) {
  const modes = glazewm.bindingModes.map(
    m => `<button class="pill" data-mode="${esc(m.name)}">${esc(m.displayName ?? m.name)}</button>`,
  );
  if (glazewm.isPaused) {
    modes.unshift('<button class="pill paused" data-pause="1">PAUSADO</button>');
  }
  return modes.join('');
}

export function networkIcon(net) {
  const type = net?.defaultInterface?.type;
  if (type === 'ethernet') return ICON.ethernet;
  if (type === 'wifi') return ICON.wifi;
  if (type === 'proprietary_virtual') return ICON.vpn;
  return ICON.wifiOff;
}

export const networkHTML = net => `${ico(networkIcon(net))}${esc(net.defaultGateway?.ssid ?? '')}`;

export function cpuHTML(usage) {
  const v = Math.round(usage);
  return `${ico(ICON.cpu)}<span class="${v > 85 ? 'high' : ''}">${v}%</span>`;
}

export const memoryHTML = usage => `${ico(ICON.memory)}${Math.round(usage)}%`;

// --- Relógio: curto ou longo (botão direito), em pt-PT ---
// Peças separadas: o formato curto de pt-PT junta dia/mês em números
// ("20/10"); assim fica "ter. 20 out.".
const fmtWeekday = new Intl.DateTimeFormat('pt-PT', { weekday: 'short' });
const fmtMonth = new Intl.DateTimeFormat('pt-PT', { month: 'short' });
const fmtTime = new Intl.DateTimeFormat('pt-PT', { hour: '2-digit', minute: '2-digit' });
const fmtLong = new Intl.DateTimeFormat('pt-PT', { weekday: 'long', day: 'numeric', month: 'long' });

export function isoWeek(d) {
  const t = new Date(Date.UTC(d.getFullYear(), d.getMonth(), d.getDate()));
  const day = t.getUTCDay() || 7;
  t.setUTCDate(t.getUTCDate() + 4 - day);
  const yearStart = new Date(Date.UTC(t.getUTCFullYear(), 0, 1));
  return Math.ceil(((t - yearStart) / 86400000 + 1) / 7);
}

export function clockText(now, longo) {
  return longo
    ? `${fmtLong.format(now)} · semana ${isoWeek(now)} · ${fmtTime.format(now)}`
    : `${fmtWeekday.format(now)} ${now.getDate()} ${fmtMonth.format(now)}  ${fmtTime.format(now)}`;
}

// --- Volume: a roda acumula os passos (3 toques rápidos = +15) ---
export function volumeIcon(vol, muted) {
  if (muted || vol === 0) return ICON.volOff;
  return vol < 34 ? ICON.volLow : vol < 67 ? ICON.volMed : ICON.volHigh;
}

// `pendente`: o volume pedido pela roda enquanto o Windows ainda não o devolveu (null = o valor real).
export function audioVista(dev, pendente) {
  const vol = Math.round(pendente ?? dev.volume);
  return {
    html: `${ico(volumeIcon(vol, dev.isMuted))}<span class="${dev.isMuted ? 'muted' : ''}">${vol}%</span>`,
    title: `${dev.name}\nClique: definições rápidas · Roda: volume · Botão direito: silenciar`,
  };
}

// Um passo da roda: 5 % para cima (deltaY < 0) ou para baixo, entre 0 e 100.
export function proximoVolume(pendente, volumeReal, deltaY) {
  const base = pendente ?? Math.round(volumeReal);
  return Math.min(100, Math.max(0, base + (deltaY < 0 ? 5 : -5)));
}

// A cor vai no HTML (e não só no CSS): o ícone é pintado num canvas e só se repinta se o HTML mudar.
export const bateriaHTML = bat => `<span class="ico" data-icon="${bat.icone}" style="--c: ${bat.cor}"></span>` +
  `<span style="color: ${bat.cor}">${bat.texto}</span>`;

// --- Chávena: não suspender (resposta de "bar_helper.py awake status|toggle": "on" ou "off") ---
export function awakeVista(estado) {
  const on = estado.trim() === 'on';
  return {
    on,
    icon: on ? ICON.coffee : ICON.coffeeOutline,
    title: on
      ? 'PC mantido acordado — clique para voltar a permitir a suspensão (Alt+Esc, I)'
      : 'Suspensão permitida — clique para manter o PC acordado (Alt+Esc, I)',
  };
}

// Comandos do GlazeWM para um botão gerado (workspaces, modos, pausa); o restauro das minimizadas tem
// dois passos encadeados e fica na página.
export function comandosDoBotao(dataset) {
  const comandos = [];
  if (dataset.ws) comandos.push(`focus --workspace ${dataset.ws}`);
  if (dataset.mode) comandos.push(`wm-disable-binding-mode --name ${dataset.mode}`);
  if (dataset.pause) comandos.push('wm-toggle-pause');
  return comandos;
}
