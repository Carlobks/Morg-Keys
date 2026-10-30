---
name: desenhando-telas
description: Guia as decisões de interface de um agente para sistemas com muitos dados (ERPs, painéis, áreas administrativas) — que tela deve existir, o que mostrar e o que esconder, quantas abas e ações cabem, como separar superfícies e usar a cor sem depender dela, contraste e alvos de toque nos números da norma, botões, movimento e a checklist antes de entregar. Usar ao criar, redesenhar ou rever qualquer tela, modal, tabela, formulário, painel ou navegação, ou ao decidir se uma página deve existir. Não usar para a identidade visual de marca ou páginas de marketing, nem para provar no navegador que a tela ficou certa (é a testes-e-provas).
---

# Desenhando telas

**Os dados são o protagonista; a moldura some.** Na dúvida, tira-se moldura (bordas, cores, ornamentos), nunca dados. Esta skill descreve **papéis** ("superfície de cartão", "texto de apoio"), não classes, para valer em qualquer stack. Um exemplo de receita em Tailwind está em `references/exemplo-tailwind.md`, e os números com as fontes em `references/tetos-e-fontes.md`.

## 1. Filosofia

- **Design é como funciona.** Primeiro a clareza do uso, depois o polimento.
- **Menos, mas melhor** (Dieter Rams). Reduzir **e** melhorar o que fica. Simplificar tirando capacidade é regressão.
- **Foco é dizer não:** um número que responde à pergunta da tela, uma ação principal.
- **Quem paga a complexidade?** (lei de Tesler) Cada opção exposta é complexidade que o sistema se recusou a absorver e passou para a pessoa.
- **Consistência:** os mesmos papéis visuais em todo o lado. Profundidade comunica hierarquia; a cor é sotaque, não fundo.

## 2. Seis perguntas antes de desenhar

1. Que complexidade o sistema absorve, e qual fica para a pessoa?
2. Qual é o **único** número que responde à pergunta desta tela?
3. Qual é a **única** ação principal?
4. O que se esconde, e com que **frequência medida** é usado?
5. O que se agrupa?
6. Quem vê? O que se desativa e o que se explica?

Antes de desenhar, **escreva as suposições de volume**: quantos registros, o nome mais longo, itens por mês. Uma tela desenhada para 10 linhas quebra com 300.

## 3. Heurísticas

1. **Mostrar e esconder tem dois lados.** O que se usa com frequência fica à vista. Corta-se pela **frequência medida**, não pela importância percebida.
   - **Sinal de risco nunca se esconde:** vencido, em falta, bloqueado, por pagar.
   - **O que se esconde mostra um resumo** ("Documentos · 14"), nunca uma seta muda.
   - Se a pessoa comum abre mais de metade dos blocos recolhidos, recolher custa mais do que poupa.
2. **Uma ação principal.** No máximo uma ou duas em destaque, distinguidas pelo **estilo**, não pelo tamanho.
3. **Um número protagonista**, grande, com algarismos de largura fixa (`tabular-nums`). O resto é apoio. Nunca uma parede de indicadores iguais.
4. **Cartões por seção:** poucos cartões, poucas linhas cada, ordenados pela frequência de consulta.
5. **Permissões à vista:**
   - **ação** sem permissão fica **desativada, com o motivo em texto visível**. Um `title` não aparece num botão desativado nem num ecrã de toque;
   - **navegação** sem permissão ou vazia fica **visível e explica porquê**. Não se esconde nem se desativa sem explicação.

**Limites vêm de medição**, não de "7 ± 2" (isso é sobre memorizar, não sobre ver) nem da lei de Hick (que manda ordenar, não cortar).

## 4. Arquitetura de informação

1. **Uma página-índice ou carrega dados, ou não existe.** Se tem uma só filha, não precisa de índice. Se só repete nomes, apague. Um índice legítimo mostra contagens, estado ou pendências, e deixa começar a tarefa ali mesmo.
2. **O tipo de página decide o layout:**
   - **panorama** (ler o geral);
   - **detalhe** (ler uma entidade);
   - **transacional** (editar).

   Largura total para tabelas; largura fixa para texto e formulários. Não estique formulários.
3. **Tetos:** veja `references/tetos-e-fontes.md`. Os conferidos são: abas fixas, no máximo 4; uma só ação primária. Acima do teto de abas, use um menu de "mais", nunca um carrossel.
4. **A navegação nomeia a tarefa, não a tabela:** "Pagamentos", não "Eventos de cobrança".
5. **As abas carregam informação:** "Fornecedores (3) · Aluguéis (12)".
6. **A moldura do sistema não se repete no módulo:** a navegação de topo é uma só.
7. **A densidade é do público.** Quem usa a tela o dia inteiro quer mais dados por tela. "Na dúvida, tira" vale para a moldura; dados cortam-se só com medição.

## 5. Sistema visual, por papel

**Superfícies.** Fundo, cartão, elevado (modal), campo de entrada, cabeçalho de tabela. Cada papel tem um valor fixo, e as superfícies são **sólidas**: fundo translúcido deixa passar o que está atrás e apaga a hierarquia. Transparência só em fundos de modal e em estados.

**Fronteira entre superfícies: pelo menos 1,2:1.** Pode vir do fundo **ou** da borda. Num tema escuro, quase sempre vem da borda. O único erro é fundo fraco **e** borda fraca ao mesmo tempo. Nunca uma borda semitransparente.

**Orçamento de bordas.** Borda só em três coisas: o que se **edita**, os **contentores de topo** e o botão **fantasma**. Uma lista de registros vive num **só** contentor, com divisórias entre as linhas, nunca uma caixa com borda por item.

**Tipografia.**
- Hierarquia por peso, tamanho e cor, nunca por mais famílias de fonte.
- Nada de pesos finos (`light`, `thin`).
- `tabular-nums` em todo número.
- Tamanhos em `rem`, nunca em `px` fixo, para respeitar o tamanho que a pessoa escolhe.
- **O título de uma seção nunca é menor nem mais apagado do que o texto dentro dela.**

**Contraste (WCAG 2.2, critério 1.4.3, nível AA):**

| Texto | Mínimo |
|---|---|
| Normal | **4,5:1** |
| Grande: ≥ 18 pt (≈ 24 px), ou ≥ 14 pt em negrito (≈ 18,5 px) | **3:1** |

Fontes finas podem precisar de mais. Nunca esbata o texto "para parecer minimalista": reposicione, agrupe ou recolha.

**Camadas.** Antes de subir o `z-index`, veja se a camada está num portal: o portal resolve, subir o número não. Defina uma escala fixa (conteúdo, barra fixa, ícones globais, modais, sobre-modal, confirmação) e não use valores soltos como `9999`.

**Forma e espaço.**
- O arredondamento cresce com o tamanho: controles < cartões < modais.
- **Proximidade:** o espaço entre seções é pelo menos o **dobro** do maior espaço dentro delas.
- Separe primeiro por espaço; a linha vem depois.

## 6. Cor e daltonismo

Cada cor é **estado** ou **identidade**.

- **Estado** (ok, erro, aviso, inativo) usa sempre **tokens de estado**, que um tema para daltonismo pode remapear. Nunca escreva à mão um "verde" ou um "vermelho" para estado.
- **Identidade** (marca, dinheiro, categorias) usa uma cor fixa, que não se remapeia.
- **Teste de um segundo:** uma pessoa daltônica precisa desta cor para distinguir bom de mau? Se sim, é estado.
- **A cor nunca é o único sinal** (WCAG 1.4.1, nível A). O que a cor distingue leva também texto, ícone, forma ou posição. A cor vem por último, a reforçar.
- **O remapeamento não cobre a identidade:** cores de identidade podem colapsar com as de estado. Separe-as por rótulo.
- **Num tema escuro, elementos vizinhos não se separam só pela cor:** use borda, espaço ou claro contra escuro. Um controle segmentado mostra o item ativo por **elevação**, não pela cor da marca.
- **Verifique, não ache:** simule a deuteranopia nos pares de cores novos e, se puder, mostre a uma pessoa daltônica.

## 7. Hover não é affordance

Em tablets e celulares não há hover.

| Situação | Regra |
|---|---|
| Ação **principal** de uma linha | Sempre visível |
| Ação secundária que existe noutro lugar | Pode aparecer só no hover |
| Rótulo de um ícone | Sempre visível, nunca só no tooltip |
| Enriquecimento puro | Hover à vontade |

O que aparece no hover fica visível em ecrãs sem hover (`@media (hover: none)`).

## 8. Botões

1. **Parece um botão:** tamanho, contraste e estados de hover e de clique visíveis. São três níveis:
   - **fantasma:** ação solta, com borda;
   - **ferramenta:** age sobre o contentor onde está, sem borda, com rótulo escrito;
   - **chip:** um valor escolhido.
2. **Botão faz, link vai.**
3. **Rótulo = verbo + resultado**, em uma a três palavras ("Gerar contrato", "Marcar como pago"). Nunca "OK", "Submeter" ou "Confirmar" sozinhos. O destrutivo diz o que faz: **Arquivar** (volta atrás) é diferente de **Excluir** (some de vez).
4. **Alvo de toque.** O WCAG 2.2 pede pelo menos **24×24 px** (nível AA). A Apple usa **44×44 pt** como tamanho padrão em iOS e iPadOS, com um mínimo de 28×28 pt. Para telas de toque, mire nos 44. **Meça a caixa** depois de mexer no padding; não a deduza.
5. **Hierarquia:**
   - **principal:** uma cor de destaque. Escolha uma que não seja a dos valores na mesma tela; se o dinheiro é verde, a ação principal não é verde;
   - **secundária:** neutra, com borda;
   - **destrutiva:** a cor de erro;
   - **desativada:** com o motivo visível.
6. **Colocação:** a principal fica onde a tarefa acaba (no fim do modal, à direita). Um rodapé fixo só se não tapar conteúdo.
7. **Destrutivo pede atrito:** confirmação. Se for irreversível, a pessoa **escreve o identificador** (o número, o nome) antes de confirmar.

## 9. Movimento: leve, mas presente

- **Só quatro razões para mover algo:**
  - **retorno:** fui ouvido?
  - **relação:** de onde veio isto?
  - **continuidade:** estou na mesma página?
  - **estado:** está a acontecer.
- **Tempos:** 200–500 ms, com um teto de 700 ms. No máximo duas ou três coisas a mexer ao mesmo tempo, e nada de bounce.
- **Respeite o `prefers-reduced-motion`** do sistema. Com ele ligado, tira-se o movimento, mas o **sinal fica**: o estado final aparece sem a animação, nunca some.
- **Transição de página só com opacidade.** Um `transform` cria um novo contexto de empilhamento e parte elementos `fixed` e o arrastar e largar.
- **Navegação lenta pede retorno imediato** no elemento clicado.
- Uma animação verifica-se pelo que **pinta** (o valor resolvido ou os píxeis entre frames), não pela variável que a alimenta.

## 10. Componentes

- **Reutilize antes de criar.** Uma variante nova de botão ou de cartão é uma inconsistência nova.
- **Editar fica no cabeçalho do bloco que edita.** Um campo novo editável entra no formulário que já existe. Não duplique um dado só para o tornar editável.
- Modais: usam um portal, prendem o foco, fecham com Escape e avisam antes de descartar alterações.
- Sem emoji em títulos e na interface. Gráficos seguem as mesmas regras de cor (estado × identidade).

## 11. Checklist antes de entregar

- [ ] Que complexidade o sistema absorveu, e qual ficou para a pessoa?
- [ ] **Uma** ação principal, distinguida pelo estilo? Rótulos com verbo + resultado?
- [ ] O que está à vista foi escolhido pela frequência de uso? Nenhum sinal de risco escondido? O que está recolhido mostra um resumo?
- [ ] Um número protagonista, com `tabular-nums`?
- [ ] Estado com tokens de estado? Tudo o que a cor distingue tem outro sinal? Pares novos simulados para daltonismo?
- [ ] Fronteira entre superfícies ≥ 1,2:1? Superfícies sólidas? Bordas dentro do orçamento? Lista de registros num só contentor?
- [ ] Contraste ≥ 4,5:1 (ou 3:1 em texto grande, pela definição da norma)? Tamanhos em `rem`?
- [ ] Título de seção ≥ o texto de dentro? Espaço entre seções ≥ 2× o de dentro?
- [ ] Nada principal depende de hover? Ícones de ação com rótulo?
- [ ] Botão faz, link vai? Alvos de toque **medidos**? Destrutivo com atrito?
- [ ] Movimento com uma das quatro razões, ≤ 700 ms, com `prefers-reduced-motion` respeitado?
- [ ] Permissões: ação desativada com motivo visível; navegação visível e explicada?
- [ ] Os limites batem com os tetos? A página-índice carrega dados? O layout segue o tipo de página?
- [ ] A simplificação tirou ruído, e não capacidade?

**Beleza não é evidência.** Uma tela valida-se com uma pessoa real ou com um número medido (uma captura lida, uma caixa medida), nunca com um "parece limpo".

## 12. Segurança acima da estética

- Uma decisão de design nunca muda dados sozinha.
- A validação é no servidor. O botão fica desativado enquanto a ação corre.
- **Sem dados reais** (nomes, documentos, contas bancárias) em exemplos, placeholders, demos ou testes.

## Fontes

Ver `references/tetos-e-fontes.md` e `FONTES.md`.
