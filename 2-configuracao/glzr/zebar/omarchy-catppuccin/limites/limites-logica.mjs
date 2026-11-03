// Modal dos limites do Claude (clique no ✻ da barra; limites.html): o que pôr nos campos e o que mostrar.
// Sem DOM: testa-se com node --test (tests/limites-logica.test.mjs). Ler e validar o que o dono escreve
// (14:30, 2h15, qui 16:00, %) é do bar_helper.py (morg_limites.py), um só sítio para essas regras.
import { fmtUntil } from '../partilhado/claude.mjs';
import { b64 } from '../painel/apps-logica.mjs';

export const CAMPOS = ['five_pct', 'five_reset', 'week_pct', 'week_reset'];

const pctDoCampo = janela => (janela ? String(Math.round(janela.pct)) : '');
const dicaDoReset = (janela, now, exemplo) => (janela ? `vazio: fica ${fmtUntil(janela.resets_at, now)}` : exemplo);

// Estado do `limites state` -> valores iniciais dos campos. O reset fica vazio (vazio mantém o atual) e o
// atual aparece na dica: escrever por cima de um "2h15" já velho gravaria uma hora errada.
export function valoresIniciais(estado) {
  return {
    five_pct: pctDoCampo(estado.five_hour),
    five_reset: '',
    week_pct: pctDoCampo(estado.seven_day),
    week_reset: '',
    five_reset_dica: dicaDoReset(estado.five_hour, estado.now, 'ex.: 14:30 ou 2h15'),
    week_reset_dica: dicaDoReset(estado.seven_day, estado.now, 'ex.: qui 16:00'),
  };
}

// De onde vêm os valores que estão guardados, e de quando.
export function origemDosValores(estado) {
  if (!estado.captured_at) return 'Ainda sem valores guardados.';
  const idade = fmtUntil(estado.now + (estado.now - estado.captured_at), estado.now);
  return estado.origem === 'manual' ? `Postos à mão há ${idade}.` : `Do Claude Code no terminal, há ${idade}.`;
}

// Campos do formulário -> argumento do `limites set` (JSON em base64url, como o `panel do`).
export function pedidoDeGravar(campos) {
  return b64(JSON.stringify(Object.fromEntries(CAMPOS.map(c => [c, String(campos[c] ?? '').trim()]))));
}

// Resposta do `limites set` -> { ok, porCampo: {campo: mensagem}, geral }.
export function errosDaResposta(r) {
  if (r?.ok) return { ok: true, porCampo: {}, geral: '' };
  return { ok: false, porCampo: r?.errors ?? {}, geral: r?.errors ? '' : (r?.error || 'Sem resposta do bar_helper.py.') };
}

// Pré-visualização no navegador (?preview): valores postos à mão há 5 minutos.
const AGORA = 1_800_000_000;
export const ESTADO_DE_EXEMPLO = {
  now: AGORA, captured_at: AGORA - 300, origem: 'manual',
  five_hour: { pct: 40, resets_at: AGORA + 8100 }, seven_day: { pct: 70, resets_at: AGORA + 2 * 86400 },
};
