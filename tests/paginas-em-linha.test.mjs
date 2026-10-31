// Os <script type="module"> em linha das páginas (bar.html, arranque/splash.html, guia/sistema.html): não se
// podem abrir fora do Zebar (armadilha A2), por isso confirma-se aqui que cada nome importado de um .mjs do
// pack existe mesmo no módulo. Um import errado deixaria a página em branco.
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
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
