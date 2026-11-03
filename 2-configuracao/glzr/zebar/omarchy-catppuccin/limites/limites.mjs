// Modal dos limites do Claude (clique no ✻ da barra): a ligação à página (DOM) e ao Zebar.
// O que pôr nos campos e como ler a resposta está em limites-logica.mjs (testado com node --test); este ficheiro
// só liga os eventos; nenhum teste o carrega, por isso fica fora da cobertura (verifica-se à mão com ?preview,
// docs/validacao-manual.md).
import { ePreVisualizacao } from '../partilhado/paineis.mjs';
import { CAMPOS, errosDaResposta, ESTADO_DE_EXEMPLO, origemDosValores, pedidoDeGravar, valoresIniciais } from './limites-logica.mjs';

const $ = id => document.getElementById(id);
const USO = $('uso').href;
let call = async () => ({ ok: true, state: ESTADO_DE_EXEMPLO }); // pré-visualização: dados de exemplo
let close = () => {};
let abrirUso = () => window.open(USO);

function mostrarErros({ porCampo, geral }) {
  for (const c of CAMPOS) $(c).setAttribute('aria-invalid', porCampo[c] ? 'true' : 'false');
  $('five_erro').textContent = [porCampo.five_pct, porCampo.five_reset].filter(Boolean).join(' ');
  $('week_erro').textContent = [porCampo.week_pct, porCampo.week_reset].filter(Boolean).join(' ');
  $('geral').textContent = geral;
}

async function preencher() {
  mostrarErros({ porCampo: {}, geral: '' });
  const r = await call(['state']).catch(err => ({ ok: false, error: String(err) }));
  if (!r.ok) return mostrarErros(errosDaResposta(r));
  const v = valoresIniciais(r.state);
  for (const c of CAMPOS) $(c).value = v[c];
  $('five_reset').placeholder = v.five_reset_dica;
  $('week_reset').placeholder = v.week_reset_dica;
  $('origem').textContent = origemDosValores(r.state);
  $('five_pct').focus();
  $('five_pct').select();
}

$('form').addEventListener('submit', async e => {
  e.preventDefault();
  const campos = Object.fromEntries(CAMPOS.map(c => [c, $(c).value]));
  const r = await call(['set', pedidoDeGravar(campos)]).catch(err => ({ ok: false, error: String(err) }));
  const erros = errosDaResposta(r);
  if (erros.ok) return close();
  mostrarErros(erros);
  const primeiro = CAMPOS.find(c => erros.porCampo[c]);
  if (primeiro) $(primeiro).focus();
});
$('fechar').addEventListener('click', () => close());
$('uso').addEventListener('click', e => { e.preventDefault(); abrirUso(); close(); });
document.addEventListener('keydown', e => { if (e.key === 'Escape') close(); });

if (ePreVisualizacao(location)) {
  document.body.classList.add('standalone', 'open');
  preencher();
} else {
  try {
    const zebar = await import('../vendor/zebar-3.3.1.mjs');
    const win = zebar.currentWidget().tauriWindow;
    // py.exe (com saída) para os pedidos; pyw.exe para esconder. Os argumentos têm de bater com o
    // argsRegex do widget "limites" no zpack.json (A9). O caminho vem do data-helper do HTML.
    const PY = 'C:\\Windows\\py.exe';
    const PYW = 'C:\\Windows\\pyw.exe';
    const BAR_HELPER = document.documentElement.dataset.helper;
    call = async args => JSON.parse((await zebar.shellExec(PY, ['-I', BAR_HELPER, 'limites', ...args])).stdout);
    // A página de uso abre como na barra: pelo GlazeWM, sem privilégio novo.
    const providers = zebar.createProviderGroup({ glazewm: { type: 'glazewm' } });
    abrirUso = () => providers.outputMap.glazewm?.runCommand(`shell-exec explorer ${USO}`);
    let watch = null;
    let aberto = false;
    close = () => {
      if (!aberto) return;
      aberto = false;
      clearInterval(watch);
      document.body.classList.remove('open');
      zebar.shellExec(PYW, ['-I', BAR_HELPER, 'limites-hide']).catch(console.error);
    };
    window.addEventListener('focus', () => {
      if (aberto) return;
      aberto = true;
      document.body.classList.add('open');
      preencher();
      // Clicar fora fecha (o WebView2 não dá "blur" fiável: pergunta-se à janela).
      const desde = performance.now();
      clearInterval(watch);
      watch = setInterval(async () => {
        if (performance.now() - desde > 400 && !(await win.isFocused())) close();
      }, 150);
    });
    await win.hide(); // pré-carregado: o clique no ✻ (bar_helper.py limites) mostra-o
  } catch (err) {
    console.error('Zebar API indisponível:', err);
    $('geral').textContent = `Erro Zebar: ${err}`;
  }
}
