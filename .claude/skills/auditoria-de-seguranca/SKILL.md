---
name: auditoria-de-seguranca
description: Guia a revisão de segurança que um agente faz antes de enviar código — segredos nos commits que vão subir, bibliotecas com falhas conhecidas (com linha de base, para só travar o que é novo), armadilhas documentadas de Next.js, React e Supabase, e a medida por achados e cobertura em vez de uma nota única. Usar antes de um push ou de uma release, ao mexer em rotas de API, Server Actions, autenticação, políticas RLS, chaves ou dependências, e quando alguém pergunta "isto é seguro?", "tem brecha?" ou pede uma pontuação de segurança. Não usar para escrever a política RLS ou a migração em si (é a supabase ou a sql-postgres) nem para provar que uma funcionalidade funciona (é a testes-e-provas).
---

# Auditoria de segurança

Um push manda o código para onde outras pessoas o leem. Num repositório público, isso acontece no momento do push. Por isso, a verificação tem de correr **antes** do push. O CI corre depois e já chega tarde para um segredo.

## 1. As quatro camadas antes do push

| Camada | O que procura | Como | Se encontrar |
|---|---|---|---|
| Segredos | Chave, token ou senha nos commits que vão subir | `gitleaks git --log-opts="<remoto>..<local>"` (sai com 1 se encontrar) | Trava sempre |
| Bibliotecas | Versões com falha conhecida | `npm audit --json`, comparado com a linha de base | Trava se aparecer uma falha **nova** crítica ou alta |
| Armadilhas | Erros que a própria biblioteca documenta (seção 3) | Versão mínima travada e testes do projeto | Trava se aparecer uma nova |
| Banco | RLS desligado, função sem `search_path`, chave exposta | O verificador do fornecedor, só em modo leitura | Entra no relatório, e roda no CI, não no push |

Há um modelo de hook pronto em `modelos/pre-push`. O push deve continuar rápido: o que demora vai para o CI.

## 2. A linha de base: o passivo só encolhe

Um projeto antigo nunca começa com zero avisos. Se o portão travasse tudo, alguém acabaria por desligá-lo. A solução:

1. Na primeira corrida, grave os **IDs** dos avisos que já existem (o `source` de cada aviso no `npm audit --json`) num arquivo versionado.
2. Depois disso, só trava o aviso cujo ID **não** está na lista.
3. Quando um aviso some, ele sai da lista no mesmo commit. A lista só diminui.

Nunca acrescente um aviso novo à lista para conseguir passar no portão. Esconder uma biblioteca vulnerável numa lista de exceções é exatamente o erro que o portão existe para impedir. As dependências de desenvolvimento também contam: elas rodam na máquina de quem programa e no CI.

O `npm audit --audit-level=high` só decide quando o comando falha e não filtra o relatório. O osv-scanner sai com 1 em **qualquer** falha e não tem um limiar de gravidade. Para travar só crítico e alto, leia o JSON. A alternativa é deixá-lo só a informar.

## 3. Armadilhas conhecidas que viram verificação

- **Server Components com execução remota (React2Shell, CVSS 10):** React 19.0–19.2.0 e Next 15–16 sem o patch. Trave a versão mínima no portão das bibliotecas.
- **O middleware não é a única barreira:** um cabeçalho interno já permitiu saltar o middleware do Next. Toda rota e toda Server Action confere o usuário **dentro** dela.
- **Uma Server Action é um endpoint público:** qualquer pessoa a pode chamar, sem passar pela tela. Um teste lista as funções exportadas de cada arquivo `'use server'` e exige que cada uma confira a permissão.
- **Supabase:** tabela sem RLS, função `SECURITY DEFINER` sem guarda de papel e chave de serviço em código de cliente. O detalhe está na skill `supabase`.

## 4. Como investigar

1. **Âmbito.** Diga se é a revisão de uma mudança (só o que o diff toca) ou uma auditoria completa (todas as categorias da seção 6).
2. **Siga o dado.** De onde vem o valor? Há validação no caminho? Quem chama: o cookie do usuário ou a chave de serviço?
3. **Prove pelo efeito.** Compare duas contas, uma com permissão e outra sem: a que não tem recebe `42501` ou zero linhas. Uma rota pública prova-se com um pedido sem cookie. Os testes de banco correm numa transação que termina em `ROLLBACK`, nunca escrevem em produção.
4. **Classifique pela confiança.**

| Confiança | Critério | O que fazer |
|---|---|---|
| Alta | Padrão vulnerável + entrada controlada por quem ataca, confirmado | Reportar com gravidade |
| Média | Padrão vulnerável, origem da entrada por confirmar | "Por verificar", com a pergunta exata |
| Baixa | Teórico ou boa prática | Não reportar |

## 5. Cinco regras que as listas genéricas deixam passar

1. **Ter login não é uma barreira.** `USING (true)` ou "qualquer autenticado" fica aberto a todas as contas, incluindo as de quem só usa o celular. Diga quantas contas são e de quem.
2. **Uma defesa só conta se estiver ligada.** Um limitador de pedidos que ninguém chama não protege nada, e uma política antiga esquecida soma-se à nova por OR. Prove a defesa a funcionar: o quarto pedido recebe 429.
3. **A correção vai para onde a tela lê.** Antes de fechar uma tabela, procure no código qual tabela a tela consulta. Fechar a tabela errada deixa a certa aberta.
4. **Procure pelo efeito, não por uma forma.** Quem procura só `USING (true)` não vê `auth.uid() IS NOT NULL`, que tem o mesmo efeito. O nome de uma política não prova nada.
5. **A superfície vai além do código:** planilhas publicadas na web, buckets públicos, o canal de tempo real, variáveis `NEXT_PUBLIC_*` e dados pessoais em URLs. Nada disto aparece num diff.

## 6. A medida: achados e cobertura, nunca uma nota única

Uma nota de 0 a 100 dá uma sensação de segurança que o código não tem, e uma soma sem pesos definidos não serve de catraca. Meça duas coisas:

```
Achados: 1 crítico · 2 altos · 0 médios · 3 baixos
Cobertura: 8 de 12 categorias com prova · 2 sem prova · 2 por ver
```

Cada categoria tem um de três estados: **com prova** (medida), **sem prova** (lida no código, mas não exercitada) e **por ver**. A cobertura só sobe com prova. Uma categoria "por ver" nunca conta como "ok".

As 12 categorias:
1. Guarda nas Server Actions.
2. Sessão nas rotas de API.
3. RLS de leitura.
4. RLS de escrita.
5. Funções com privilégio.
6. Grants aos papéis do cliente.
7. Arquivos e buckets.
8. Tempo real.
9. Segredos.
10. Entrada não confiável (validação, uploads).
11. Dados pessoais em URLs e logs.
12. Dependências.

| Gravidade | Quando |
|---|---|
| Crítico | Dados pessoais, dinheiro ou documentos legíveis ou alteráveis sem login, ou por qualquer conta |
| Alto | O mesmo, mas exige uma condição (conhecer um id, chamar a API à mão) |
| Médio | Vazamento parcial ou indireto |
| Baixo | Endurecimento (cabeçalho em falta, mensagem de erro verbosa) |

## 7. Relatório

```
## Segurança: <âmbito> — <data>
Achados: … · Cobertura: …

### [SEG-001] <tipo> (Crítico) — confiança alta
- Onde: arquivo:linha ou tabela.política
- Quem consegue: (anônimo / qualquer conta / só com um id)
- Prova: <consulta ou pedido> → <resultado>
- Correção: … (escrita no banco só com o "sim" do dono)
```

## Fontes

Ver `FONTES.md`, na seção "Segurança": gitleaks, `npm audit`, osv-scanner, os avisos do React e do Next e o postmortem da Vercel. A ideia de "investigar antes de reportar, por confiança" foi inspirada nos guias de segurança abertos citados ali, mas o texto aqui é próprio. A lista de exceções que escondia uma biblioteca vulnerável está no livro do Akita, p. 165.
