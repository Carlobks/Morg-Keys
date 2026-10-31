// Bateria na barra (bar.html): ícone, texto, cor e dica a partir do provider "battery" do Zebar.
// Sem DOM: testa-se com node --test (tests/bateria.test.mjs).
// O provider dá { chargePercent, isCharging, state, timeTillFull, timeTillEmpty } (tempos em ms);
// num PC sem bateria não há saída e a barra esconde o indicador.

// Ícones nf-md da JetBrainsMono NF (confirmados a desenhar, 2026-10-24): de 10 em 10 %.
const A_DESCARREGAR = [0xf0083, 0xf007a, 0xf007b, 0xf007c, 0xf007d, 0xf007e, 0xf007f, 0xf0080, 0xf0081, 0xf0082, 0xf0079];
const A_CARREGAR = [0xf089f, 0xf089c, 0xf0086, 0xf0087, 0xf0088, 0xf089d, 0xf0089, 0xf089e, 0xf008a, 0xf008b, 0xf0085];
export const DESCONHECIDA = 0xf0091;

// Cor do ícone e da percentagem (pedido de 2026-10-24): a carregar azul; sem carregar verde a partir de
// AVISO, amarela abaixo de AVISO e vermelha abaixo de BAIXA.
export const AVISO = 50;
export const BAIXA = 20;
export const COR = { carregar: 'var(--blue)', ok: 'var(--green)', aviso: 'var(--yellow)', baixa: 'var(--red)' };

// 75 min -> "1h15"; 5 min -> "5 min".
export function duracao(ms) {
  const mins = Math.round(ms / 60000);
  const h = Math.floor(mins / 60);
  return h ? `${h}h${String(mins % 60).padStart(2, '0')}` : `${mins} min`;
}

// Saída do provider -> { icone, texto, cor, dica } ou null (sem bateria).
export function bateria(b) {
  if (!b || typeof b.chargePercent !== 'number') return null;
  const pct = Math.max(0, Math.min(100, Math.round(b.chargePercent)));
  const carregar = !!b.isCharging || b.state === 'charging';
  const passo = Math.round(pct / 10);
  const icone = b.state === 'unknown' ? DESCONHECIDA : (carregar ? A_CARREGAR : A_DESCARREGAR)[passo];
  const cor = carregar ? COR.carregar : pct < BAIXA ? COR.baixa : pct < AVISO ? COR.aviso : COR.ok;
  const dica = [`Bateria: ${pct}%`];
  if (b.state === 'full') dica.push('cheia');
  else if (carregar) dica.push(b.timeTillFull ? `a carregar · cheia em ${duracao(b.timeTillFull)}` : 'a carregar');
  else if (b.timeTillEmpty) dica.push(`restam ${duracao(b.timeTillEmpty)}`);
  return { icone, texto: `${pct}%`, cor, dica: dica.join(' · ') };
}
