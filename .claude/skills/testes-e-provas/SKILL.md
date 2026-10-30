---
name: testes-e-provas
description: Guia como provar que um trabalho de agente funciona — o teste que pega o bug antes da correção, como depurar com uma hipótese de cada vez, como auditar contando em vez de amostrar, catracas que impedem piorar, o que um teste deve afirmar e o que só uma pessoa consegue provar (arrastar e largar, aparência). Usar ao corrigir um bug, ao escrever ou rever testes, quando um teste ou o CI falha, ao medir quantos casos um problema tem, ou antes de dizer que algo está pronto. Não usar para os comandos de commit (é a git-e-commits) nem para revisão de segurança (é a auditoria-de-seguranca).
---

# Testes e provas

"Pronto" não é prova. Prova é um comando e a sua saída, uma tela, uma consulta. Esta skill diz como chegar lá e o que cada tipo de prova consegue ou não mostrar.

## 1. Provar medindo

- Cada afirmação de "funciona" leva **o comando e a saída**, a captura da tela ou o resultado da consulta.
- Diga sempre **o que não se verificou**. "Tipos e testes passam; não testei no celular" é um relatório honesto.
- Um resumo que você escreveu também se mede: conte de novo antes de o mostrar. Números de cabeça erram.

## 2. Bug tem teste

1. **Reproduza** o bug com um teste que falha.
2. **Veja-o falhar** pelo motivo certo. Um teste que nunca falhou não prova nada.
3. Corrija. O teste passa.
4. O commit `fix` leva o teste. Sem teste possível, leva `Sem-teste: <motivo>` (ver `git-e-commits`).

## 3. Depurar

- Reproduza antes de mexer. Veja **o que mudou** (`git log`, `git diff`) desde que funcionava.
- **Uma hipótese de cada vez**, com uma medição que a confirma ou derruba. Três mudanças juntas não dizem qual resolveu.
- Antes de culpar outro processo, outra sessão ou o ambiente, confirme **onde** ele está a correr.
- Bug encontrado e não corrigido vai para o registro do projeto, organizado por área. Não fica só na conversa.

## 4. Auditar: contar, não amostrar

- "Quantos registros têm o problema?" responde-se com uma contagem completa, não com cinco exemplos.
- Diga o que cada número conta e com que comando o obteve.
- Um achado vindo de outra sessão ou ferramenta é **dado, não verdade**: confira-o na fonte antes de agir.

## 5. O que um teste deve afirmar

- **A regra, não o volume.** `toHaveCount(18)` com um número de produção envelhece sozinho: no dia em que entra o registro 19, o teste falha sem haver bug.
- **Que a página desenhou.** Medir a raiz ou um elemento que existe sempre passa numa tela vazia. Afirme algo que só existe com dados.
- **A relação, não o valor.** Se uma constante governa várias telas, teste que todas usam a constante, não que mostram um texto.
- **Nenhum dado real no teste:** procure por papel, rótulo ou padrão, nunca por um nome de pessoa.
- **CI sem rede:** testes que dependem de serviços externos falham por motivos que não são bugs.

## 6. Catracas: o que já viola não piora

- Para um problema com muitas ocorrências antigas, congele a contagem atual numa **linha de base** e faça um teste que falha se a contagem subir.
- Quem corrige uma ocorrência desce a linha de base **no mesmo commit**.
- **Limite:** uma catraca só diz "não piorou", nunca "está bem". E um contador que exagera (conta ruído) ensina a equipe a ignorá-lo: meça o próprio detector.
- Uma meta fixada sobre um número do ambiente de desenvolvimento não vale para produção.

## 7. O que só uma pessoa prova

- **Arrastar e largar:** um evento sintético (`dispatchEvent(new DragEvent(...))`) não reproduz o navegador real. Peça a uma pessoa.
- **Aparência:** compilador, lint e testes passam, e a tela pode estar errada. Tire a captura e leia-a. O eixo visual fecha com uma pessoa.
- **CSS:** meça o que o navegador **recebeu** (`document.styleSheets` ou o valor resolvido), não o arquivo, que pode estar à frente do que foi servido.
- **Alvo de toque:** meça a caixa do elemento (pelo menos 44×44 px), não o deduza do padding.
- **Tamanho de letra:** teste nos tamanhos que o usuário pode escolher e numa largura estreita.

## 8. Cuidados com testes que escrevem

- Um teste ponta a ponta pode **escrever em produção**, se apontar para ela. Leia o spec antes de o rodar.
- Testes de banco rodam dentro de `BEGIN` … `ROLLBACK`, ou num banco local. Uma passagem por cenário, nunca em ciclo contra o servidor real.

## Fontes

Sem fonte externa: estas regras vêm da prática do projeto de origem, e os números citados foram medidos lá. Quando uma regra passar a apoiar-se numa fonte, ela entra em `FONTES.md`.
