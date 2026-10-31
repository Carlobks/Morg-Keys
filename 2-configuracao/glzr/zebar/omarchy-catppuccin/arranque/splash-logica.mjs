// Lógica do ecrã de arranque (arranque/splash.html) sem DOM: os tempos, os dados de exemplo, a saudação,
// o ícone e o estado de cada etapa e quando sair. Testa-se com node --test (tests/splash-logica.test.mjs);
// a cola com o DOM e o Zebar fica no splash.html (docs/validacao-manual.md).
//
// O progresso vem de progress.json, escrito pelo orquestrador
// (bar_helper.py boot, ou "animacao preview"):
// {boot_id, started, animacao, preview, nome, frase:{texto,personagem,anime}|null,
//  steps:[{id,label,state}], fim}.
export const MAX_MS = 70000;       // rede de segurança (o orquestrador sai aos 60 s no máximo)
export const MIN_ITEM_MS = 250;    // cada linha fica visível pelo menos isto
export const CYCLE_MS = 4500;      // período dos ciclos das animações
const MAX_IDADE_S = 60;            // um arranque mais velho do que isto já acabou
const FIM_PARADO_MS = 300;         // depois do fim, a lista fica assim um instante antes de sair
const MIN_NO_ECRA_MS = 1800;       // e o ecrã nunca sai antes disto

// No navegador (file: ou ?preview, servidor pack-preview) usa dados de exemplo em vez do Zebar.
export const emPreVisualizacao = (protocolo, pesquisa) =>
  protocolo === 'file:' || new URLSearchParams(pesquisa).has('preview');

export const EXEMPLO = {
  boot_id: 'exemplo', started: Date.now() / 1000, animacao: 'cafe', preview: true, nome: 'Ana', fim: false,
  frase: { texto: 'Uma pessoa só morre quando é esquecida.', personagem: 'Dr. Hiriluk', anime: 'One Piece' },
  steps: [{ id: 'barra', label: 'Barra', state: 'feito' }, { id: 'glazewm', label: 'Gestor de janelas', state: 'a_carregar' }],
};

// Guarda: só mostra se houver um arranque (ou pré-visualização) em curso
// (evita reaparecer, p.ex. se o Zebar relançar widgets ao mudar de monitor).
export const deveFechar = (progresso, agoraS) =>
  !progresso || !!progresso.fim || agoraS - progresso.started > MAX_IDADE_S;

// Nome da animação a usar: a do progresso se existir no registo, senão "cafe".
export const animacaoValida = (nome, existentes) => (existentes.includes(nome) ? nome : 'cafe');

// --- Saudação: "Muito bem-vindo, <nome>", a hora (pt-PT, como o relógio da barra) e a frase do dia ---
const fmtHora = new Intl.DateTimeFormat('pt-PT', { hour: '2-digit', minute: '2-digit' });
const fmtDia = new Intl.DateTimeFormat('pt-PT', { weekday: 'long', day: 'numeric', month: 'long' });
export const saudacao = nome => (nome ? `Muito bem-vindo, ${nome}` : 'Muito bem-vindo');
export const horaTexto = d => `${fmtHora.format(d)} · ${fmtDia.format(d)}`;

// Autor da frase ("— personagem, anime"), ou null se a frase não tiver nenhum dos dois.
export function autorDaFrase(f) {
  if (!f.personagem && !f.anime) return null;
  return `— ${[f.personagem, f.anime].filter(Boolean).join(', ')}`;
}

// --- Lista de etapas (progresso real) ---
// Ícone de cada etapa (Nerd Font nf-md / nf-oct, fonte JetBrainsMono NF),
// pelo id que o bar_helper.py lhe dá: barra, glazewm, app:<processo>, bat:<n>, fim.
export const APP_ICONS = {
  claude: 0xf06c4, chrome: 0xf02af, Arc: 0xf059f, msedge: 0xf01e9,
  Obsidian: 0xf0ebf, explorer: 0xf0256, WindowsTerminal: 0xf489,
};
export function iconFor(id) {
  if (id === 'barra') return 0xf035c;               // menu
  if (id === 'glazewm') return 0xf0574;             // mosaico
  if (id === 'fim') return 0xf012c;                 // visto
  if (id === 'anim') return 0xf03d8;                // paleta (pré-visualização)
  if (id === 'apps') return 0xf003b;
  if (id.startsWith('bat:')) return 0xf489;         // terminal
  if (id.startsWith('app:')) return APP_ICONS[id.slice(4)] ?? 0xf0614;
  return 0xf0614;                                   // janela genérica
}

// Classes a juntar à linha de uma etapa: só depois de ela estar visível MIN_ITEM_MS.
export function classesDaEtapa(estado, visivelHaMs) {
  if (visivelHaMs < MIN_ITEM_MS) return [];
  if (estado === 'feito') return ['done'];
  if (estado === 'falhou') return ['done', 'fail'];
  return [];
}

// Com o fim anunciado e todas as linhas feitas: sai quando o fim já dura FIM_PARADO_MS e o ecrã já esteve
// MIN_NO_ECRA_MS à vista.
export const podeSair = (desdeOFimMs, desdeOInicioMs) =>
  desdeOFimMs >= FIM_PARADO_MS && desdeOInicioMs > MIN_NO_ECRA_MS;
