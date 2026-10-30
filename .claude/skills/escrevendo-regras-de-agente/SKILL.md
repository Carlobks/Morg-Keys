---
name: escrevendo-regras-de-agente
description: Guia como escrever e manter as instruções que um agente de código lê (CLAUDE.md, AGENTS.md, regras por pasta e skills) — onde cada coisa deve ficar, quando uma lição vira regra, o formato curto com o motivo, os limites de tamanho e como transformar texto em barreira de máquina. Usar ao criar ou mudar um CLAUDE.md, AGENTS.md, arquivo de regras ou skill, ao promover uma lição a regra, ou quando o arquivo de instruções está crescendo e o agente começa a ignorá-lo. Não usar para escrever documentação do produto para pessoas, nem para o conteúdo técnico de uma regra (SQL, React, segurança), que tem as suas próprias skills.
---

# Escrevendo regras de agente

Uma instrução que o agente lê em todo turno custa contexto em todo turno. Escrita mal, ela é ignorada, aciona na hora errada ou dá falsa confiança. Esta skill diz onde cada coisa vai e como se escreve.

## 1. Onde cada coisa vai

| O que é | Onde vai | Por quê |
|---|---|---|
| Fato permanente que vale para todo o projeto | Arquivo lido sempre (`CLAUDE.md` / `AGENTS.md`) | Precisa estar presente em todo turno |
| Regra que só vale para uma pasta | Regra por pasta (no Claude Code: `.claude/rules/` com `paths`) | Só carrega quando o agente abre um arquivo daquela pasta |
| Procedimento com passos, checklist ou formato de saída | Skill | Só a descrição carrega no início; o corpo, quando o assunto aparece |
| Algo que **tem de** ser cumprido | Hook, teste ou CI | Texto é conselho; só a máquina obriga |
| Dado ou ação num sistema externo | Conector (MCP) | Nunca guardar dados numa regra ou skill |
| Preferência de uma pessoa | Memória do agente | Não é regra do projeto |

**Cuidado com regras por pasta no Claude Code:** elas carregam quando o agente usa Read, Write ou Edit num arquivo que casa com o `paths`. Um `grep` pelo terminal pode não carregar a regra. Para ler código, usar a ferramenta de leitura.

## 2. Quando uma lição vira regra

- Uma lição só muda o trabalho futuro quando é **promovida a regra**. Uma lição que fica na conversa ou num arquivo de notas não volta a ser lida.
- Promove-se quando o erro **custou caro** ou **se repetiu**. Não se promove o que o modelo já faz sozinho: meça antes, pedindo a tarefa sem a regra.
- Antes de criar, procure se já existe uma regra parecida e melhore essa. Duas regras sobre o mesmo assunto acabam por se contradizer.
- Ao fechar uma porta (proibir algo), pergunte qual é a porta seguinte: o que o agente vai fazer em vez disso?

## 3. Como se escreve

- **Forma curta** no arquivo lido sempre: um título único em maiúsculas, a regra numa linha, o motivo numa frase. Exemplo: `**SEM SILENCIAR ALARME:** nada de eslint-disable novo. · *Já se escondeu uma biblioteca vulnerável numa lista de exceções.*`
- **Texto integral** num arquivo à parte, com **o mesmo título**, para se achar com um `grep`. O arquivo lido sempre aponta para lá.
- O motivo é o que torna a regra aplicável a casos novos. Uma regra sem motivo é seguida à letra e falha no primeiro caso que não previu.
- Instrução concreta vence aspiração: "rode `npx tsc --noEmit` antes de commitar" funciona; "siga boas práticas" não muda nada.
- Uma regra que aponta para uma ferramenta que já não existe ensina o agente a saltar a regra inteira. Ao remover uma ferramenta, procure as regras que a citam.
- Uma decisão de projeto ("só usamos a branch `main`") escreve-se como escolha, com o custo e o benefício, não como lei universal.

## 4. Limites de tamanho

- O arquivo lido sempre deve ser **curto**. A documentação do Claude Code recomenda menos de 200 linhas. Num projeto real, um limite de **100 linhas e 160 caracteres por linha**, imposto por um teste, tirou o arquivo de 328 KB para menos de 10 KB.
- Importar outro arquivo (`@caminho`) organiza, mas **não economiza contexto**: o importado carrega junto.
- Estudos sobre arquivos de contexto mostram que arquivos longos podem **baixar** a taxa de acerto e subir o custo. Curto e concreto rende mais.
- Quando o arquivo cresce, a correção é **tirar** coisas: o que vale para uma pasta vai para a regra da pasta; o que é procedimento vai para uma skill.

## 5. Skills

- **Nome:** minúsculas, números e hífens, até 64 caracteres, sem "claude" nem "anthropic".
- **Descrição:** até 1024 caracteres, na terceira pessoa. Diz o que faz e quando usar, e termina com "Não usar…" para afastar os quase-acertos. Mesma língua do corpo.
- **Corpo:** menos de 500 linhas. O que for longo vai para arquivos de referência ao lado, que só se abrem quando preciso.
- **Skills de terceiros:** leia o `SKILL.md` e todos os scripts antes de instalar, e só instale com uma dor concreta que ela resolva. Uma skill instalada que ninguém usa só custa contexto.
- **Testes:** casos de gatilho (pedidos que devem e não devem acionar, com quase-acertos) e casos de execução com e sem a skill.

## 6. De texto para barreira

Pergunte, para cada regra: o que acontece se o agente a ignorar?

- **Pouco:** fica como texto.
- **Muito** (vazamento, dado apagado, produção fora do ar): vira barreira. Pode ser um hook que recusa o commit, um teste que falha, uma regra de negação nas permissões do agente ou um passo do CI.
- **Autorização permanente:** quando o dono deixa o agente fazer algo sem pedir a cada vez, escreva **qual classe de ação** está autorizada (por exemplo, "criar tarefas no quadro do projeto"), e não uma licença geral. Tudo o que fica fora dessa classe volta a pedir o "sim".
- **Catraca:** para o que já viola em grande quantidade, congele a contagem atual numa linha de base e falhe só se piorar. A linha de base desce no mesmo commit que corrige.

## 7. Registro

- Toda fonte citada num arquivo de regras vai para um arquivo único de fontes, com a data em que foi lida.
- Pesquisa que outra sessão vai reler vai num arquivo próprio, com estrutura fixa: pergunta, fontes, o que se mediu, o que não se verificou, conclusão.
- O texto do dono do projeto é fonte primária: guarde-o como ele escreveu e arrume só numa cópia.

## Fontes

Ver `FONTES.md`: documentação do Claude Code (memória e skills), AAIF (medição do AGENTS.md), ETH Zurich (avaliação de arquivos de contexto) e o livro *Competente o Suficiente*, de Fabio Akita (pp. 128–129, sobre skills de terceiros; p. 165, sobre listas de exceção).
