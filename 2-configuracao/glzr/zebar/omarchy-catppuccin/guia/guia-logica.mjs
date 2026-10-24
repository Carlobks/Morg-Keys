// Guia de atalhos (Alt+K): a tabela dos atalhos e o HTML que a desenha (sem DOM; testado com node --test).
import { appLabel, esc } from '../comum/comum.mjs';

// Uma linha por atalho: [descrição, teclas, ícone opcional]. "|" separa
// alternativas, "+" separa teclas da mesma combinação. `icon` (da secção
// ou da linha) = código Nerd Font da família nf-md (fonte JetBrainsMono NF).
// `col` = coluna do modal (1 a 4), distribuídas para ficarem equilibradas.
// Teclas iguais às do Omarchy 4, com Alt no lugar de Super.
export const SECTIONS = [
  {
    // As linhas das apps vêm de apps.txt (ver parseApps); estas ficam fixas.
    title: 'Abrir apps', accent: 'var(--green)', icon: 0xf003b, col: 1, apps: true,
    rows: [
      ['Raycast (lançador)', 'Win'],
      ['Todas as apps (Iniciar)', 'Ctrl+Esc'],
      ['Este guia', 'Alt+K'],
      ['Mudar estes atalhos (painel: Alt+Esc e depois C)', 'Alt+Esc'],
    ],
  },
  {
    title: 'Redimensionar', accent: 'var(--teal)', icon: 0xf0a68, col: 1,
    rows: [
      ['Mais estreita / larga', 'Alt+-|Alt++'],
      ['Mais baixa / alta', 'Alt+Shift+-|Alt+Shift++'],
      ['Modo fino (H J K L ou setas)', 'Alt+R'],
      ['Sair do modo fino', 'Esc|Enter'],
    ],
  },
  {
    title: 'Janelas', accent: 'var(--blue)', icon: 0xf05af, col: 2,
    rows: [
      ['Focar janela ao lado', 'Alt+← ↓ ↑ →'],
      ['Focar (estilo Vim, sem ↑)', 'Alt+H J L'],
      ['Mover janela (ou com setas)', 'Alt+Shift+H J K L'],
      ['Fechar', 'Alt+W|Alt+Q'],
      ['Ecrã inteiro', 'Alt+F'],
      ['Maximizar (mantém a barra)', 'Alt+E'],
      ['Flutuante ↔ mosaico', 'Alt+T'],
      ['Flutuante sempre por cima', 'Alt+O'],
      ['Alternar foco: mosaico / flutuantes', 'Alt+C'],
      ['Minimizar', 'Alt+M'],
      ['Restaurar última minimizada', 'Alt+Shift+M'],
      ['Dividir na outra direção', 'Alt+V'],
      ['Esconder / mostrar a barra', 'Alt+Shift+Space'],
    ],
  },
  {
    title: 'GlazeWM', accent: 'var(--pink)', icon: 0xf0574, col: 2,
    rows: [
      ['Pausar / retomar', 'Alt+Shift+P'],
      ['Recarregar config', 'Alt+Shift+R'],
      ['Redesenhar janelas', 'Alt+Shift+W'],
    ],
  },
  {
    title: 'Workspaces', accent: 'var(--mauve)', icon: 0xf0570, col: 3,
    rows: [
      ['Ir para o workspace', 'Alt+1 … 9|Alt+0'],
      ['Voltar ao anterior', 'Alt+(mesmo nº)|Alt+D'],
      ['Enviar janela e seguir', 'Alt+Shift+1 … 0'],
      ['Seguinte / anterior com janelas', 'Alt+S|Alt+A'],
      ['Scratchpad: mostrar / esconder', 'Alt+º'],
      ['Enviar janela para o scratchpad', 'Alt+Shift+º'],
    ],
  },
  {
    title: 'Sistema — Alt+Esc e depois…', accent: 'var(--red)', icon: 0xf0493, col: 3,
    rows: [
      ['Wi-Fi', 'W', 0xf05a9],
      ['Bluetooth', 'B', 0xf00af],
      ['Som', 'A', 0xf057e],
      ['Ecrã', 'D', 0xf0379],
      ['Luz noturna', 'N', 0xf0594],
      ['Não suspender (chávena)', 'I', 0xf0176],
      ['Gestor de Tarefas', 'T', 0xf0430],
      ['Energia', 'P', 0xf0241],
      ['Bloquear', 'L', 0xf033e],
      ['Apps e arranque (enviar apps para teclas e workspaces)', 'C', 0xf030c],
      ['Gravar arranjo dos workspaces', 'G', 0xf0193],
      ['Animação do arranque: tocar troca · segurar mostra', 'E', 0xf03d8],
      ['Sair do GlazeWM', 'Q', 0xf0206],
      ['Reiniciar (pede confirmação)', 'R', 0xf0709],
      ['Desligar (pede confirmação)', 'O', 0xf0425],
      ['Cancelar', 'Esc|Alt+Esc'],
    ],
  },
  {
    title: 'Barra (rato)', accent: 'var(--peach)', icon: 0xf037d, col: 4,
    rows: [
      ['Menu: Raycast · Terminal', 'Clique|Botão direito'],
      ['Nº do workspace: ir para ele', 'Clique'],
      ['Workspaces: seguinte / anterior', 'Roda'],
      ['Etiqueta tracejada: restaurar', 'Clique'],
      ['Chávena: não suspender', 'Clique'],
      ['Relógio: notificações · formato', 'Clique|Botão direito'],
      ['✻ Claude: página de uso · detalhes', 'Clique|Pairar'],
      ['Volume: definições rápidas', 'Clique'],
      ['Volume ±5 % · silenciar', 'Roda|Botão direito'],
      ['Wi-Fi: escolher rede', 'Clique'],
    ],
  },
  {
    title: 'Windows', accent: 'var(--yellow)', icon: 0xf05b3, col: 4,
    rows: [
      ['Captura de ecrã', 'Alt+Shift+S|Win+Shift+S'],
      ['Notificações', 'Alt+,|Win+N'],
      ['Definições rápidas', 'Win+A'],
      ['Saída de som', 'Win+Ctrl+V'],
      ['Histórico da área de transferência', 'Win+V'],
      ['Emojis', 'Win+.'],
      ['Conta-gotas (PowerToys)', 'Win+Shift+C'],
      ['Copiar texto de imagem (PowerToys)', 'Win+Shift+T'],
      ['Gestor de Tarefas', 'Ctrl+Shift+Esc'],
      ['Bloquear o PC', 'Win+L'],
    ],
  },
  {
    title: 'O Alt rouba às apps', accent: 'var(--overlay0)', icon: 0xf002a, col: 2,
    rows: [
      ['Voltar / avançar no browser', 'botões do rato'],
      ['Barra de endereço (era Alt+D)', 'Ctrl+L'],
      ['Menus das apps (Alt+F, Alt+E)', 'Alt sozinho'],
    ],
  },
];

// "Alt+Shift+-|Win+N" -> <kbd>Alt</kbd><kbd>Shift</kbd><kbd>-</kbd> ou <kbd>Win</kbd><kbd>N</kbd>.
export function keysHtml(spec) {
  return spec
    .split('|')
    .map(alt => alt
      .replace(/\+\+/g, '+\u0000') // "Alt++" = Alt e a tecla "+"
      .split('+')
      .map(k => `<kbd>${esc(k === '\u0000' ? '+' : k)}</kbd>`)
      .join(''))
    .join('<span class="or">ou</span>');
}

export const icoHtml = code => (code ? `<span class="ico" data-icon="${code}"></span>` : '');

// Uma secção; data-q = texto onde o filtro procura (título, descrição e teclas, em minúsculas).
export const sectionHtml = s =>
  `<section style="--accent:${s.accent}"><h2>${icoHtml(s.icon)}${esc(s.title)}</h2>${s.rows
    .map(
      ([what, keys, icon]) =>
        `<div class="row" data-q="${esc((`${s.title} ${what} ${keys}`).toLowerCase())}">` +
        `${icoHtml(icon)}<span class="what">${esc(what)}</span><span class="keys">${keysHtml(keys)}</span></div>`,
    )
    .join('')}</section>`;

// As 4 colunas do guia; as linhas do apps.txt entram no topo da secção "Abrir apps".
export const columnsHtml = (sections, appRows) => [1, 2, 3, 4]
  .map(c => `<div class="col">${sections.filter(s => s.col === c)
    .map(s => sectionHtml(s.apps ? { ...s, rows: [...appRows, ...s.rows] } : s))
    .join('')}</div>`)
  .join('');

// Filtro: o texto escrito (sem espaços nas pontas, minúsculas) e se uma linha (data-q) bate com ele.
export const consultaDoFiltro = valor => valor.trim().toLowerCase();
export const bateNoFiltro = (q, textoDaLinha) => !q || textoDaLinha.includes(q);

// Texto do apps.txt ("Alt+Shift+B = Google Chrome") -> linhas do guia [nome, teclas].
export const parseApps = text => text.split(/\r?\n/)
  .map(l => l.trim())
  .filter(l => l && !l.startsWith('#') && l.includes('='))
  .map(l => {
    const [keys, ...rest] = l.split('=');
    return [appLabel(rest.join('=')), keys.trim().replace(/\s*\+\s*/g, '+')];
  });
