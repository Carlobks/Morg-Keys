// Os <script type="module"> em linha das páginas (bar.html, arranque/splash.html, guia/sistema.html): não se
// podem abrir fora do Zebar (armadilha A2), por isso confirma-se aqui que cada nome importado de um .mjs do
// pack existe mesmo no módulo. Um import errado deixaria a página em branco.
import assert from 'node:assert/strict';
import { spawnSync } from 'node:child_process';
import { mkdtempSync, readFileSync, rmSync, writeFileSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { test } from 'node:test';
import { fileURLToPath, pathToFileURL } from 'node:url';

const PACK = join(dirname(fileURLToPath(import.meta.url)), '..', '2-configuracao', 'glzr', 'zebar', 'omarchy-catppuccin');
const PAGINAS = ['bar.html', 'arranque/splash.html', 'guia/sistema.html'];

// Texto do <script type="module"> em linha da página.
export function scriptEmLinha(pagina) {
  const html = readFileSync(join(PACK, pagina), 'utf8');
  return html.match(/<script type="module">\n([\s\S]*?)\n\s*<\/script>/)[1];
}

// [{ nomes, de }] dos `import { a, b } from './x.mjs'` do script.
export function importsComNome(script) {
  return [...script.matchAll(/import\s*\{([^}]*)\}\s*from\s*'([^']+)'/g)]
    .map(([, nomes, de]) => ({ nomes: nomes.split(',').map(n => n.trim()).filter(Boolean), de }));
}

test('importsComNome: lê os nomes de imports numa ou em várias linhas', () => {
  assert.deepEqual(importsComNome("import { a } from './a.mjs';\nimport {\n  b, c,\n} from '../c.mjs';\nimport * as z from './z.mjs';"),
    [{ nomes: ['a'], de: './a.mjs' }, { nomes: ['b', 'c'], de: '../c.mjs' }]);
});

for (const pagina of PAGINAS) {
  test(`${pagina}: cada nome importado existe no módulo`, async () => {
    for (const { nomes, de } of importsComNome(scriptEmLinha(pagina))) {
      const modulo = await import(pathToFileURL(join(PACK, dirname(pagina), de)).href);
      for (const nome of nomes) assert.ok(nome in modulo, `${pagina}: ${nome} não existe em ${de}`);
    }
  });
}

// Catraca (ML11b): nas páginas fica só a cola com o DOM e o Zebar; a lógica vai para um .mjs testado. O
// tamanho de cada <script> em linha só desce: ao encolher, baixa-se o número aqui.
const LINHAS_MAXIMAS = { 'bar.html': 205, 'arranque/splash.html': 188, 'guia/sistema.html': 79 };

test('os <script> em linha não crescem (a lógica nova vai para um .mjs testado)', () => {
  for (const pagina of PAGINAS) {
    const linhas = scriptEmLinha(pagina).split('\n').length;
    assert.ok(linhas <= LINHAS_MAXIMAS[pagina], `${pagina}: ${linhas} linhas, máximo ${LINHAS_MAXIMAS[pagina]}`);
    assert.equal(linhas, LINHAS_MAXIMAS[pagina], `${pagina} encolheu para ${linhas}: baixe LINHAS_MAXIMAS`);
  }
});

// O Biome do projeto não lê o JS dentro do HTML: cada <script> vai para um .mjs numa pasta temporária e passa
// pelas regras recomendadas, mais nada por declarar (um import esquecido), nada por usar e funções até 35 linhas.
const BIOME = join(PACK, '..', '..', '..', '..', 'node_modules', '@biomejs', 'biome', 'bin', 'biome');
const GLOBAIS = ['document', 'window', 'location', 'console', 'getComputedStyle', 'performance', 'fetch', 'CSS',
  'setTimeout', 'setInterval', 'clearTimeout', 'clearInterval', 'requestAnimationFrame', 'URLSearchParams'];
const REGRAS = {
  correctness: { noUndeclaredVariables: 'error', noUnusedVariables: 'error', noUnusedImports: 'error' },
  complexity: { noExcessiveLinesPerFunction: { level: 'error', options: { maxLines: 35 } } },
};

test('os <script> em linha passam no Biome', () => {
  const pasta = mkdtempSync(join(tmpdir(), 'morg-em-linha-'));
  try {
    writeFileSync(join(pasta, 'biome.json'), JSON.stringify({ linter: { rules: REGRAS }, javascript: { globals: GLOBAIS } }));
    for (const pagina of PAGINAS) writeFileSync(join(pasta, `${pagina.replace('/', '_')}.mjs`), scriptEmLinha(pagina));
    const biome = spawnSync(process.execPath, [BIOME, 'lint', '--error-on-warnings', '.'], { cwd: pasta, encoding: 'utf8' });
    assert.equal(biome.status, 0, biome.stdout + biome.stderr);
  } finally {
    rmSync(pasta, { recursive: true, force: true });
  }
});
