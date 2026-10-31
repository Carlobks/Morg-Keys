// Lógica do painel do sistema (guia/sistema.html, Alt+Esc) sem DOM: os grupos e o seu HTML, o nome da
// animação e o estado do aviso de erros lidos do arranque.txt e se a camada "sistema" está ativa. Testa-se com node --test
// (tests/sistema-logica.test.mjs); a cola com o DOM e o Zebar fica no sistema.html (docs/validacao-manual.md).
import { esc } from '../partilhado/paineis.mjs';

// Igual à camada "sistema" do config.yaml do GlazeWM (lá estão as ações).
// Ícones: códigos Nerd Font (fonte JetBrainsMono NF), família nf-md.
export const GROUPS = [
  { title: 'Ligações', color: 'var(--blue)', items: [
    ['W', 0xf05a9, 'Wi-Fi'],
    ['B', 0xf00af, 'Bluetooth'],
    ['A', 0xf057e, 'Som'],
  ] },
  { title: 'Ecrã', color: 'var(--yellow)', items: [
    ['D', 0xf0379, 'Ecrã'],
    ['N', 0xf0594, 'Luz noturna'],
    ['I', 0xf0176, 'Não suspender'],
  ] },
  { title: 'Sistema', color: 'var(--green)', items: [
    ['T', 0xf0430, 'Gestor de Tarefas'],
    ['P', 0xf0241, 'Energia'],
    ['L', 0xf033e, 'Bloquear'],
  ] },
  { title: 'Personalizar', color: 'var(--mauve)', items: [
    ['C', 0xf030c, 'Apps e arranque'],
    ['E', 0xf03d8, 'Animação: <b id="anim">…</b>', true],
    ['V', 0xf0028, 'Aviso de erros: <b id="erros">…</b>', true],
  ] },
  { title: 'Sessão', color: 'var(--red)', wide: true, items: [
    ['Q', 0xf0206, 'Sair do GlazeWM'],
    ['R', 0xf0709, 'Reiniciar'],
    ['O', 0xf0425, 'Desligar'],
  ] },
];

// HTML dos grupos; o 4.º campo de um item diz que a etiqueta já é HTML (o <b id="anim"> da animação).
export function gruposHTML(grupos) {
  return grupos.map(g => `
        <section class="group${g.wide ? ' wide' : ''}" style="--c:${g.color}">
          <h2>${esc(g.title)}</h2>
          <ul>${g.items.map(([k, icon, label, html]) => `
            <li><span class="ico" data-icon="${icon}"></span><span class="lb">${html ? label : esc(label)}</span><kbd>${esc(k)}</kbd></li>`).join('')}
          </ul>
        </section>`).join('');
}

// Animação escolhida no arranque.txt (linha "animação = …", com ou sem acentos): o nome a mostrar.
export const NOMES = { cafe: 'Café' };
export function animacaoDoArranque(texto) {
  const line = texto.split(/\r?\n/).find(l => /^\s*anima[cç][aã]o\s*=/i.test(l));
  const key = (line?.split('=')[1] ?? 'cafe').trim().toLowerCase().replace('é', 'e');
  return NOMES[key] ?? key;
}

// Aviso de erros (arranque.txt, "erros = mostrar | esconder"): as mesmas palavras do morg_relatorio_erros.py.
const ESCONDER = new Set(['esconder', 'ocultar', 'nao', 'não', 'off']);
export function avisoDeErros(texto) {
  const line = texto.split(/\r?\n/).find(l => /^\s*erros\s*=/i.test(l));
  return line && ESCONDER.has(line.split('=')[1].trim().toLowerCase()) ? 'desligado' : 'ligado';
}

// Os rótulos lidos do arranque.txt, com o id do elemento de cada um (o painel atualiza-os juntos).
export const rotulosDoArranque = texto => [['anim', animacaoDoArranque(texto)], ['erros', avisoDeErros(texto)]];

// O painel mostra-se enquanto o GlazeWM estiver na camada "sistema".
export const camadaAtiva = bindingModes => (bindingModes ?? []).some(m => m.name === 'sistema');
