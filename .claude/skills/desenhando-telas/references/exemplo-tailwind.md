# Exemplo: os papéis em Tailwind, tema escuro

Uma forma de aplicar os princípios da skill `desenhando-telas` com Tailwind CSS, num tema escuro de cinzas frios (`slate`). É um **exemplo**: troque as cores pelas do seu projeto e mantenha as **relações** (fronteira ≥ 1,2:1, um acento por tela, estado em tokens).

Os tamanhos abaixo de `text-xs` (`text-2xs`, `text-3xs`) são degraus extra, em `rem`, que se definem no tema do projeto.

## Superfícies

| Papel | Classe |
|---|---|
| Fundo da página | `bg-slate-950` |
| Cartão / painel | `bg-slate-900` |
| Elevado (modal) | `bg-slate-950 border border-slate-800 shadow-2xl` |
| Campo de entrada | `bg-slate-800` |
| Borda de cartão e de campo | `border-slate-700` |
| Divisória de lista | `divide-y divide-slate-800` |
| Cabeçalho de tabela | `bg-slate-800 border-b border-slate-700` |
| Fundo atrás do modal | `bg-slate-950/75 backdrop-blur-md` |

Calculado com as cores do Tailwind (fórmula de luminância do WCAG):

- a borda `slate-700` dá 1,72:1 sobre o cartão (`slate-900`) e 1,95:1 sobre o fundo (`slate-950`);
- a divisória `slate-800` dá 1,22:1 sobre o cartão;
- entre fundos, `slate-950 → slate-800` dá 1,38:1. Já `slate-950 → slate-900` dá só 1,13:1, que não chega para separar sem borda.

## Texto

| Papel | Classe | Nota |
|---|---|---|
| Número protagonista | `tabular-nums text-3xl font-extrabold tracking-tight` | |
| Título de seção | `text-sm font-bold text-slate-200` | |
| Rótulo pequeno (kicker) | `text-2xs font-semibold uppercase tracking-widest text-slate-400` | Só em rótulos de campo; nunca maior que o texto de dentro |
| Valor | `text-sm font-semibold text-slate-100` | |
| Texto de apoio | `text-2xs text-slate-400` | `slate-400` sobre `slate-900` dá 6,96:1 e passa; `slate-500` dá 3,75:1, não passa os 4,5:1, e fica só para o que está desativado |

## Estado e identidade

Defina tokens de estado no tema (`status-ok`, `status-danger`, `status-warning`, `status-neutral`) e remapeie-os num tema para daltonismo. Use opacidade para o fundo e o anel:

```txt
pílula ok:    inline-flex items-center gap-1 rounded-lg px-2 py-1 text-2xs font-semibold
              bg-status-ok/10 text-status-ok ring-1 ring-status-ok/30
pílula aviso: (igual, com status-warning)
```

## Receitas

```txt
// Cartão de seção
rounded-2xl border border-slate-700 bg-slate-900 p-5

// Linha de lista (dentro de um só contentor com divide-y divide-slate-800)
linha:    flex items-center gap-3 py-2.5
título:   truncate text-sm font-semibold text-slate-100
apoio:    truncate text-2xs text-slate-400
valor:    shrink-0 tabular-nums text-sm font-bold text-slate-100
ação:     sempre visível (ver "Hover não é affordance")

// Campo
input: w-full rounded-lg border border-slate-700 bg-slate-800 px-3 py-2 text-sm text-slate-100
       focus:border-<acento>-500 focus:outline-none

// Botões
principal:  inline-flex items-center gap-2 rounded-xl bg-<acento>-600 px-6 py-2.5 text-sm font-bold text-white
            hover:brightness-110 disabled:opacity-40
secundário: rounded-xl border border-slate-700 px-5 py-2.5 text-sm font-medium text-slate-300 hover:bg-slate-800
fantasma:   inline-flex items-center gap-1 rounded-lg border border-slate-700 px-3 py-1.5 text-xs font-medium
            text-slate-300 hover:bg-slate-800
ferramenta: inline-flex min-h-11 items-center gap-1 rounded-lg px-2 text-2xs font-semibold text-slate-300
            hover:bg-slate-800 aria-pressed:bg-slate-800   (sem borda, dentro do contentor em que age)

// Controle segmentado: o ativo por elevação, nunca pela cor da marca
ativo:  bg-slate-700 text-white ring-1 ring-slate-600
outro:  bg-slate-900 text-slate-300 ring-1 ring-slate-700 hover:bg-slate-800

// Modal (se não houver um componente pronto): sempre por portal
envoltório: fixed inset-0 z-[70] flex items-center justify-center p-4
fundo:      absolute inset-0 bg-slate-950/75 backdrop-blur-md
diálogo:    relative flex max-h-[90vh] w-full max-w-xl flex-col overflow-hidden rounded-3xl
            border border-slate-800 bg-slate-950 shadow-2xl

// Mostrar no hover, mas visível em ecrãs sem hover
opacity-0 group-hover:opacity-100 [@media(hover:none)]:opacity-100 transition-opacity
```

## Forma e espaço

- Arredondamento: `rounded-xl` em controles, `rounded-2xl` em cartões, `rounded-3xl` em modais, `rounded-full` em pontos e avatares.
- Espaço: `space-y-6` entre seções, no máximo `space-y-3` dentro delas.
- Alvo de toque: `py-2.5` com `text-sm` dá cerca de 40 px de altura. Com textos menores, aumente o padding e **meça**.

## Movimento

Use as variantes `motion-safe:` e `motion-reduce:` do Tailwind, que seguem o `prefers-reduced-motion` do sistema. O estado final aparece sempre, com ou sem animação.
