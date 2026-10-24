// Pré-visualização do painel no navegador (file: ou ?preview): dados de exemplo, sem gravar nada.
// Imita as respostas do "bar_helper.py panel …" (morg_painel.py) só em memória.
import { unb64 } from './apps-logica.mjs';

export function chamadaDeExemplo(demoraMs = 150) {
  const sample = {
    keys: [{ key: 'alt+enter', value: 'terminal' }, { key: 'alt+shift+enter', value: 'claude-code' },
           { key: 'alt+shift+b', value: 'Google Chrome' }, { key: 'alt+shift+c', value: 'Claude' },
           { key: 'alt+shift+n', value: 'Notepad++' }, { key: 'alt+shift+y', value: 'web: https://www.youtube.com' }],
    fixed: ['alt+shift+h', 'alt+shift+j', 'alt+shift+k', 'alt+shift+l', 'alt+shift+q', 'alt+shift+m', 'alt+shift+p',
            'alt+shift+r', 'alt+shift+s', 'alt+shift+w', 'alt+shift+e'],
    workspaces: [{ index: 0, workspace: '1', label: 'Terminal', value: 'terminal' },
                 { index: 1, workspace: '2', label: 'Google Chrome', value: 'Google Chrome' },
                 { index: 2, workspace: '2', label: 'web.whatsapp.com', value: 'web: https://web.whatsapp.com' },
                 { index: 3, workspace: '3', label: 'Spotify', value: 'Spotify' }],
    undo: 0,
  };
  const apps = ['Arc', 'Calculadora', 'Claude', 'Discord', 'Excel', 'Google Chrome', 'Microsoft Edge', 'Notepad++',
                'Obsidian', 'Outlook', 'PowerPoint', 'Spotify', 'Steam', 'Visual Studio Code', 'Word']
    .map(n => ({ name: n, value: n }));
  return async args => {
    await new Promise(r => setTimeout(r, demoraMs));
    if (args[0] === 'apps') return { ok: true, apps };
    if (args[0] === 'state') return { ok: true, state: sample };
    if (args[0] === 'do') {
      aplicar(sample, JSON.parse(unb64(args[1])));
      return { ok: true, state: sample };
    }
    return { ok: false, error: 'Na pré-visualização não há desfazer.', state: sample };
  };
}

function aplicar(s, o) {
  if (o.op === 'key' || o.op === 'unkey') {
    s.keys = s.keys.filter(k => k.key !== o.key && k.key !== o.from);
    if (o.op === 'key') s.keys.push({ key: o.key, value: o.value });
  } else if (o.op === 'ws-add') {
    s.workspaces.push({ index: s.workspaces.length, workspace: o.ws, label: o.label, value: o.value });
  } else if (o.op === 'ws-del') {
    s.workspaces = s.workspaces.filter(w => w.index !== o.index).map((w, i) => ({ ...w, index: i }));
  } else if (o.op === 'ws-move') {
    s.workspaces.find(w => w.index === o.index).workspace = o.ws;
  }
  s.undo++;
}
