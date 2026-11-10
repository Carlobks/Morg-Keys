# Documentação do Morg Keys — índice

Ponto de entrada da documentação técnica (para quem mantém o projeto e para agentes de IA).
O guia de quem usa o PC é o `Tutorial.html`; as regras de trabalho dos agentes estão em `CLAUDE.md`.

| Ficheiro | Para quê |
|---|---|
| [arquitetura.md](arquitetura.md) | Arquitetura, mapa de ficheiros, o arranque passo a passo, como funciona cada funcionalidade (§2–§5) |
| [instalacao.md](instalacao.md) | Instalação automática e à mão, desinstalação, como o pacote foi montado (§6–§7) |
| [armadilhas.md](armadilhas.md) | Problemas encontrados (A1, A2, …) e a regra para os evitar (§8). **Ler antes de mudar** |
| [receitas.md](receitas.md) | Receitas de alteração: atalho novo, letra nova, animação nova, atualizar o Zebar… (§9) |
| [validacao-manual.md](validacao-manual.md) | O que só se verifica à mão e como (§10) |
| [decisoes/](decisoes/) | Decisões (ADR): uma por ficheiro, `NNNN-titulo.md`, nunca se reutiliza um número |
| [pesquisa/](pesquisa/README.md) | Pesquisas por tópico, com fontes e o que não foi verificado |
| [experiencias/](experiencias/) | Experiências medidas (plano, medidas, resultados): `0001-cobertura-a-vs-c.md` |
| [auditoria-2026-10-24.md](auditoria-2026-10-24.md) | Auditoria de segurança, código e regras de 2026-10-24: achados e o plano F0–F7 |
| [morg-laws/](morg-laws/) | Verificações contra as regras gerais do Morg Laws (`verificacao-01-2026-10-30.md`, `verificacao-02-2026-10-31.md`) e o plano que as cumpre (`plano-01.md`) |
| [pendentes.md](pendentes.md) | Trabalho combinado e ainda não feito, por ordem |
| [regras-e-barreiras.md](regras-e-barreiras.md) | Cada regra do `CLAUDE.md` e a barreira que a obriga (hook, git, teste, permissão, CI ou texto) |
| [planos/](planos/) | Planos aprovados depois do plano Morg Laws (cópia da aba Plano, com fora do escopo e prova): `0001-bug-painel-apps.md`, `0002-relatorio-de-erros.md`, `0003-tecla-do-aviso-de-erros.md`, `0004-versao-e-sistema-no-relatorio.md`, `0005-reinstalar-sem-esconder-janelas.md`, `0006-modal-limites-claude.md`, `0007-arrastar-abas.md`, `0008-morg-mais-leve.md` |
| [arquivo/](arquivo/) | Documentos cumpridos, guardados para consulta: `proposta-CLAUDE.md` (aplicada na ML6 do plano Morg Laws) |
| [painel-apps.md](painel-apps.md) | Plano do painel "Apps e arranque" (Alt+Esc, C) |

## Decisões

| N.º | Decisão | Estado |
|---|---|---|
| [0001](decisoes/0001-decisoes-de-design-iniciais.md) | Decisões de design iniciais (Alt = Super, sem Ctrl+Alt, …) | aceite |
| [0002](decisoes/0002-repositorio-publico-sem-marca.md) | Repositório público sem marca nem dados pessoais, GPL-3.0 | aceite |
| [0003](decisoes/0003-instaladores-descarregados.md) | Instaladores descarregados e verificados | aceite |
| [0004](decisoes/0004-um-so-pack-zebar.md) | Um só pack do Zebar | aceite |
| [0005](decisoes/0005-painel-escolher-e-enviar.md) | Painel "Apps e arranque": escolher e enviar | aceite |
| [0006](decisoes/0006-icones-em-svg.md) | Ícones em SVG em vez de canvas | aceite |
| [0007](decisoes/0007-foco-do-teclado-nos-paineis.md) | Foco do teclado pela janela de topo | aceite |
| [0008](decisoes/0008-regras-do-biome-desligadas.md) | Duas regras do Biome desligadas (cascata do CSS) | aceite |
| [0009](decisoes/0009-px-nas-paginas-do-zebar.md) | Tamanhos em `px` nas páginas do Zebar (o `rem` não se aplica) | aceite |
| [0010](decisoes/0010-historico-publicado-nao-se-reescreve.md) | O histórico já publicado não se reescreve (caminho pessoal em commits antigos) | aceite |
| [0011](decisoes/0011-versoes-semver-no-lancamento.md) | Versões SemVer, calculadas no lançamento | aceite |

## Mapa das secções antigas (§N do `COMO-FOI-FEITO.md`)

| § | Agora em |
|---|---|
| §1 Objetivo e decisões fixas | `decisoes/0001-decisoes-de-design-iniciais.md` |
| §2 Arquitetura · §3 Mapa de ficheiros · §4 Arranque · §5 Funcionalidades | `arquitetura.md` |
| §6 Instalação · §7 Como o pacote foi montado | `instalacao.md` |
| §8 Armadilhas | `armadilhas.md` |
| §9 Receitas | `receitas.md` |
| §10 Verificação | `validacao-manual.md` |

Regra: ficheiro `.md` novo → linha nesta tabela (e, se for pesquisa, em `pesquisa/README.md`).
