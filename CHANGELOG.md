# Changelog

As mudanças do Morg Keys que se notam por quem o instala. Segue o [Keep a Changelog 1.1.0][kac]: a versão
mais recente primeiro, as datas em AAAA-MM-DD e as mudanças agrupadas por categoria.

O que ainda não foi lançado está em `changelog.d/`, um ficheiro por mudança (formato em
`changelog.d/README.md`). Na hora de lançar uma versão, `py -I scripts/changelog/juntar_changelog.py` junta-os
aqui, calcula a versão seguinte pelo [SemVer 2.0.0][semver] (ADR 0011), escreve-a no `VERSION` e apaga-os; com
`--rascunho` só mostra a secção.

[kac]: https://keepachangelog.com/pt-BR/1.1.0/
[semver]: https://semver.org/lang/pt-BR/

## [0.1.0] - 2026-10-31

### Adicionado

- Bateria na barra, só em PCs com bateria: ícone de 10 em 10 %, cor por nível (azul a carregar, verde,
  amarela, vermelha) e o tempo que falta na dica.
- O Claude Code instalado pelo npm é reconhecido pelo atalho, pelo arranque e pelo instalador.
- Ecrã de boas-vindas no arranque: o ambiente de trabalho escurece aos poucos, com a chávena, a saudação,
  a hora e a frase do dia.
- Ecrã preto logo ao entrar na sessão, fechado pela cortina do arranque, para não se ver o ambiente de
  trabalho a montar-se.
- O ✻ da barra mostra o uso do plano Claude que o Claude Code dá pela statusLine oficial. Sem valores mostra
  só o ✻ com a explicação; "claude = esconder" no arranque.txt tira-o.
- Relatório de erros: quando um ajudante do Morg Keys falha, aparece um aviso com o resumo e a pergunta
  "Guardar o relatório?", para o juntar a uma issue no GitHub. O relatório não leva o nome da conta nem caminhos
  pessoais, e fica sempre uma cópia em `.glzr\erros` (os últimos 10). Desliga-se com `erros = esconder` no
  `arranque.txt`. Para ver como é: `bar_helper.py erro-de-teste`.
- Alt+Esc, V liga e desliga o aviso de erros. O painel do Alt+Esc mostra "Aviso de erros: ligado" ou "desligado",
  com um ícone de alerta, e o guia (Alt+K) também tem a tecla.

### Alterado

- Barra neutra: os ícones da direita ficam em cinzento; só a bateria tem cores.
- O arranque já não pisca na passagem da cortina para a animação, e o café da cortina fica nítido a 125 %.
- O instalador só reinicia o Explorador quando os ícones ou a barra mudam.
- Um "nome =" vazio no arranque.txt mantido conta como sem nome: o instalador pergunta e preenche.
- O desinstalador também move as pastas do Zebar.
- Com as animações desligadas no Windows (Acessibilidade > Efeitos visuais), as páginas do Zebar deixam de
  mexer: o estado final aparece logo.
- A hora, as percentagens e as contagens usam algarismos de largura fixa e não saltam ao mudar.

### Removido

- O `gerar-modelos.ps1`, que copiava a configuração do PC para o repositório: agora edita-se no repositório
  e o instalador leva para o PC.
- O atalho Alt+Esc G (gravar arranjo). Reescrevia o arranque só com as janelas abertas e apagava as apps postas
  no painel; agora o arranque configura-se só no painel Apps e arranque (Alt+Esc C).

### Corrigido

- Os exemplos do nome (arranque.txt e pré-visualização do ecrã de boas-vindas) usam um nome fictício.
- Uma app posta no arranque pelo painel já não fica com a janela de outra app que o Windows abriu sozinho ao
  mesmo tempo (ex.: o Claude ia parar ao workspace dela).
- Os botões ✕ dos painéis (fechar, tirar o atalho, não abrir no arranque) dizem o que fazem aos leitores
  de ecrã, e não só na dica do rato.
- O texto apagado das páginas (dicas, rodapés, campos de filtro, teclas livres) passa a ter contraste de
  pelo menos 4,5:1.
- A cortina preta do arranque e o ícone dos programas .bat passavam ao Windows um endereço cortado (hInstance a
  32 bits); o Windows dava 3 "access violation" em cada arranque e ignorava-os. Agora passa o endereço inteiro.
- O registo `.glzr\erros\rebentamentos.log` já não cresce sem fim: acima de 64 KB passa a `rebentamentos.antigo.log`.
- O relatório de erros dizia "Windows 10" num Windows 11 (o Windows 11 diz-se 10.0 por dentro). Agora escreve
  "Windows 11 (build 26200.9457, 25H2)", lido do registo.
- O relatório de erros dizia "Morg Keys: desconhecida". O instalador passa a gravar a versão instalada,
  com o ramo e o commit de onde se instalou (ex.: `0.1.0+exp-a.c3b57e3`).
