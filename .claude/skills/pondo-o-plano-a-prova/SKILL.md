---
name: pondo-o-plano-a-prova
description: Conduz uma conversa de perguntas com o dono do projeto até um plano, uma decisão ou um pedido grande ficar claro o bastante para ser executado sem adivinhar — o que se quer, o que não se deve fazer, como se vai saber que deu certo, o que não tem volta e quem decide o quê. Usar quando um pedido grande chega sem limites ou sem forma de validar, quando o dono pede para "apertar", "pôr à prova" ou "fazer as perguntas" sobre um plano, ou antes de começar trabalho que custa caro desfazer. Não usar para uma tarefa pequena e clara (faz-se e diz-se o que se fez) nem para medir fatos que se podem consultar (lê-se o código ou os dados).
---

# Pondo o plano à prova

Um pedido grande com lacunas faz o agente preencher as lacunas sozinho, e cada palpite errado custa uma volta de retrabalho. Algumas perguntas bem escolhidas antes de começar saem mais baratas. Esta skill diz quais perguntas, como fazê-las e quando parar.

## 1. Antes de perguntar, ler

Não pergunte o que se pode descobrir. O código, os documentos, o histórico do git e os dados respondem a muitas dúvidas. Pergunte só o que **depende da vontade do dono**: objetivos, prioridades, limites, gosto, risco aceitável.

## 2. As cinco lacunas

Um pedido está pronto para executar quando tem resposta para estas cinco. Procure-as por esta ordem:

| Lacuna | Pergunta-guia | Por que importa |
|---|---|---|
| **Objetivo** | O que muda para quem usa, quando isto estiver pronto? | Sem isto, otimiza-se a coisa errada |
| **Fora do escopo** | O que **não** se deve tocar ou fazer? | O agente tende a fazer a mais |
| **Prova** | Como vamos saber que deu certo? Que comando, tela ou número? | Sem prova, "pronto" é opinião |
| **Sem volta** | O que, se der errado, não se desfaz? (dados, produção, algo publicado, dinheiro) | É onde vale parar e pedir o "sim" |
| **Quem decide** | Que decisões o dono quer tomar e quais pode deixar ao agente? | Evita perguntar demais e de menos |

## 3. Como perguntar

- **Em rondas curtas**, de no máximo quatro perguntas. Uma ronda só pergunta o que já se pode responder com o que se sabe. A resposta de uma pergunta pode mudar as seguintes.
- **Cada pergunta traz opções concretas** e uma delas marcada como recomendada, com o porquê numa frase. O dono pode aceitar a recomendação com uma palavra.
- **Explique o termo técnico** dentro da pergunta. Quem decide não precisa de saber o jargão para escolher bem.
- **Se a resposta for "explica melhor" ou "pesquisa antes",** pesquise ou explique e volte com a pergunta refeita. Não decida no lugar do dono.
- Use a ferramenta de perguntas do agente, quando houver, em vez de um formulário improvisado.

## 4. Quando parar

Pare quando as cinco lacunas tiverem resposta, ou quando o dono disser que chega. Não continue a perguntar por perguntar: cada ronda custa a atenção do dono.

## 5. O que entregar no fim

Um resumo curto, que o dono confirma antes de começar:

```
Objetivo: …
Fora do escopo: …
Prova de pronto: …
Pontos sem volta (pedem o "sim" na hora): …
Decisões do dono: …   Decisões deixadas ao agente: …
```

Guarde o resumo junto ao plano. Se a resposta do dono for um texto dele, guarde-o como ele escreveu.

## Fontes

Ver `FONTES.md`. Esta skill foi escrita do zero. A ideia de interrogar o dono antes de executar foi inspirada na skill "grill-me", de Matt Pocock, e no método de pedir com "o que não fazer" e "como validar", de Fabio Akita.
