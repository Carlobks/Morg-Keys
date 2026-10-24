// Quota do Claude na barra (bar.html): o que mostrar a partir da saída do claude_usage.py.
// Sem DOM: testa-se com node --test (tests/claude.test.mjs).
// Só a via oficial (rate_limits da statusLine, no terminal); sem valores fica só o ✻ e a dica explica
// porquê. `claude = esconder` no arranque.txt tira o indicador (docs/pesquisa/quota-claude.md).

export const STALE_AFTER_S = 15 * 60; // a partir daqui os valores ficam esbatidos

// Tempo até `epoch` (s): "2d3h", "1h05", "7m".
export function fmtUntil(epoch, now) {
  const mins = Math.max(0, Math.round((epoch - now) / 60));
  const h = Math.floor(mins / 60);
  if (h >= 24) return `${Math.floor(h / 24)}d${h % 24}h`;
  return h ? `${h}h${String(mins % 60).padStart(2, '0')}` : `${mins}m`;
}

export const level = pct => (pct >= 80 ? 'high' : pct >= 50 ? 'warn' : 'ok');

const CLIQUE = 'Clique: abre a página de uso com os números exatos.';
const ESCONDER = 'Para esconder: claude = esconder no arranque.txt (Documentos\\Guia de Atalhos).';

// Saída do claude_usage.py -> { mostrar, html, stale, dica } para o indicador da barra.
export function claudeVista(u) {
  if (u.mostrar === false) return { mostrar: false, html: '', stale: false, dica: '' };
  const five = u.five_hour;
  const week = u.seven_day;
  const age = u.captured_at ? u.now - u.captured_at : null;
  if (!five && !week) {
    const tips = ['Uso do Claude: sem valores.',
      'Só chegam quando usa o Claude Code num terminal; a aplicação de ambiente de trabalho não os dá.'];
    if (age !== null) tips.push(`Os últimos (de há ${fmtUntil(u.now + age, u.now)}) já expiraram.`);
    return { mostrar: true, html: '', stale: false, dica: [...tips, CLIQUE, ESCONDER].join('\n') };
  }
  const parts = [
    five ? `<span class="${level(five.pct)}">5h ${Math.round(five.pct)}%</span>` : '<span class="muted">5h —</span>',
    week ? `<span class="${level(week.pct)}">sem ${Math.round(week.pct)}%</span>` : '<span class="muted">sem —</span>',
  ];
  const tips = [];
  if (five) {
    parts.push(`<span class="muted">↺ ${fmtUntil(five.resets_at, u.now)}</span>`);
    tips.push(`Sessão (5h): ${five.pct}% — repõe em ${fmtUntil(five.resets_at, u.now)}`);
  }
  if (week) tips.push(`Semanal: ${week.pct}% — repõe em ${fmtUntil(week.resets_at, u.now)}`);
  tips.push(age === null
    ? 'Ainda sem a hora dos valores.'
    : `Valores de há ${fmtUntil(u.now + age, u.now)} (última sessão no terminal).`);
  return {
    mostrar: true,
    html: parts.join(' <span class="sep">·</span> '),
    stale: age === null || age > STALE_AFTER_S,
    dica: [...tips, CLIQUE, ESCONDER].join('\n'),
  };
}
