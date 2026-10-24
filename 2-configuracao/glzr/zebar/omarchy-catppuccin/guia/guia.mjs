// Guia de atalhos (Alt+K): desenho, filtro e a ligação ao Zebar.
// A tabela dos atalhos e o HTML estão em guia-logica.mjs (testados com node --test).
import { drawIcons } from '../comum/comum.mjs';
import { columnsHtml, parseApps, SECTIONS } from './guia-logica.mjs';

const main = document.getElementById('sections');
let appRows = [];

// Atalhos das apps: lidos de apps.txt ("Alt+Shift+B = Google Chrome"),
// o mesmo ficheiro que o Alt+Shift+R aplica ao GlazeWM.
async function loadApps() {
  try {
    const res = await fetch(`./apps.txt?t=${Date.now()}`, { cache: 'no-store' });
    appRows = parseApps(await res.text());
  } catch {
    appRows = [];
  }
  render();
}

function render() {
  main.innerHTML = columnsHtml(SECTIONS, appRows);
  filter.dispatchEvent(new Event('input'));
  drawIcons(main);
}

// Filtro: esconde linhas (e secções vazias) que não batem com o texto.
const filter = document.getElementById('filter');
filter.addEventListener('input', () => {
  const q = filter.value.trim().toLowerCase();
  for (const section of main.querySelectorAll('section')) {
    let visible = 0;
    for (const row of section.querySelectorAll('.row')) {
      const hit = !q || row.dataset.q.includes(q);
      row.classList.toggle('hidden', !hit);
      visible += hit;
    }
    section.classList.toggle('hidden', visible === 0);
  }
});
loadApps();

// No navegador (file: ou ?preview) é uma página normal. No Zebar o guia arranca com o
// Zebar, fica carregado e escondido; o Alt+K (bar_helper.py) mostra-o e
// a página anima: sai da chávena da barra e volta para ela ao fechar.
let close = () => window.close();
if (location.protocol === 'file:' || new URLSearchParams(location.search).has('preview')) {
  document.body.classList.add('standalone');
} else {
  // Centro da chávena da barra, em px lógicos do ecrã (a 100% = px reais):
  // fica à esquerda do relógio, no centro da barra (72 px antes do meio).
  const CUP = { x: Math.round(screen.width / 2) - 72, y: 14 };
  const OPEN_MS = 480;
  const CLOSE_MS = 260;
  let win = null;
  let state = 'hidden'; // hidden | open | closing
  let watch = null;
  let closeTimer = null;
  let hideWindow = () => {};

  try {
    // Cliente do Zebar guardado no pack (vendor/): funciona sem internet.
    const zebar = await import('../vendor/zebar-3.3.1.mjs');
    win = zebar.currentWidget().tauriWindow;
    // Esconder passa sempre pelo bar_helper.py (o mesmo que o Alt+K usa
    // para mostrar): um só dono do estado visível/escondido.
    // pyw.exe = lançador oficial do Python: o caminho não muda com atualizações.
    const PYW = 'C:\\Windows\\pyw.exe';
    // O caminho vem do HTML (data-helper): o instalador só troca {{HOME}} em .html, não em .mjs.
    const HELPER = document.documentElement.dataset.helper;
    hideWindow = () => zebar.shellExec(PYW, ['-I', HELPER, 'guide-hide']).catch(console.error);

    // A animação cresce a partir da chávena: a origem da transformação
    // é a posição da chávena relativa a esta janela. outerPosition vem
    // em px físicos; a chávena e o CSS estão em px lógicos.
    const pos = await win.outerPosition();
    const scale = (await win.scaleFactor()) || 1;
    document.documentElement.style.setProperty('--ox', `${CUP.x - pos.x / scale}px`);
    document.documentElement.style.setProperty('--oy', `${CUP.y - pos.y / scale}px`);

    // Só no arranque o Tauri esconde a janela: fica pré-carregada.
    await win.hide();
  } catch (err) {
    console.error('Zebar API indisponível:', err);
    const box = document.getElementById('error'); // só aparece se algo falhar
    box.textContent = `Erro Zebar: ${err?.message ?? err}`;
    box.classList.remove('hidden');
  }

  close = () => {
    if (state !== 'open') return;
    state = 'closing';
    clearInterval(watch);
    document.body.classList.remove('open');
    closeTimer = setTimeout(() => {
      closeTimer = null;
      hideWindow();
      state = 'hidden';
    }, CLOSE_MS);
  };

  // Aparecer: o foco chega quando o Alt+K mostra a janela. Recomeça do
  // estado "dentro da chávena" e anima para fora no frame seguinte.
  window.addEventListener('focus', () => {
    if (state === 'open') return;
    // Esc e logo a seguir Alt+K: cancela o fecho que estava a meio.
    clearTimeout(closeTimer);
    closeTimer = null;
    state = 'open';
    loadApps(); // apps.txt pode ter mudado desde a última vez
    filter.value = '';
    filter.dispatchEvent(new Event('input'));
    main.scrollTop = 0;
    filter.focus();
    document.body.classList.remove('open');
    void document.body.offsetWidth; // aplica o estado inicial antes de animar
    requestAnimationFrame(() => document.body.classList.add('open'));

    // Clicar fora (ou Alt+K, que devolve o foco à janela anterior):
    // o WebView2 não recebe "blur" de forma fiável, por isso pergunta-se
    // à janela se ainda está focada.
    clearInterval(watch);
    const since = performance.now();
    watch = setInterval(async () => {
      if (!win || performance.now() - since < OPEN_MS) return;
      if (!(await win.isFocused())) close();
    }, 120);
  });
}

document.getElementById('close').addEventListener('click', () => close());

document.addEventListener('keydown', e => {
  if (e.key === 'Escape') {
    if (filter.value) {
      filter.value = '';
      filter.dispatchEvent(new Event('input'));
    } else {
      close();
    }
  } else if (e.key.length === 1 && document.activeElement !== filter && !e.ctrlKey && !e.altKey) {
    filter.focus(); // escrever em qualquer lado começa a procurar
  }
});
filter.focus();
