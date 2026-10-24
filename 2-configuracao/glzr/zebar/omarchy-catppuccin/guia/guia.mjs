// Guia de atalhos (Alt+K): a ligação à página (DOM) e ao Zebar.
// A tabela dos atalhos, o HTML e o filtro estão em guia-logica.mjs (testados com node --test); este ficheiro
// só liga os eventos da página e por isso fica fora da cobertura (verifica-se à mão com ?preview,
// docs/validacao-manual.md, "Excluído da cobertura").
import { comecaAProcurar, drawIcons, ePreVisualizacao, origemDaChavena } from '../comum/comum.mjs';
import { bateNoFiltro, columnsHtml, consultaDoFiltro, parseApps, SECTIONS } from './guia-logica.mjs';

// Cola com o DOM e o Zebar (WebView2), sem página no node --test: fora da cobertura até ao fim.
/* node:coverage disable */
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
  const q = consultaDoFiltro(filter.value);
  for (const section of main.querySelectorAll('section')) {
    let visible = 0;
    for (const row of section.querySelectorAll('.row')) {
      const hit = bateNoFiltro(q, row.dataset.q);
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
if (ePreVisualizacao(location)) {
  document.body.classList.add('standalone');
} else {
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
    // é a posição da chávena relativa a esta janela (origemDaChavena, em comum.mjs).
    const { ox, oy } = origemDaChavena(screen.width, await win.outerPosition(), await win.scaleFactor());
    document.documentElement.style.setProperty('--ox', ox);
    document.documentElement.style.setProperty('--oy', oy);

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
  } else if (comecaAProcurar(e, document.activeElement === filter)) {
    filter.focus(); // escrever em qualquer lado começa a procurar
  }
});
filter.focus();
/* node:coverage enable */
