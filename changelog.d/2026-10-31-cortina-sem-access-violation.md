Categoria: Corrigido

- A cortina preta do arranque e o ícone dos programas .bat passavam ao Windows um endereço cortado (hInstance a
  32 bits); o Windows dava 3 "access violation" em cada arranque e ignorava-os. Agora passa o endereço inteiro.
- O registo `.glzr\erros\rebentamentos.log` já não cresce sem fim: acima de 64 KB passa a `rebentamentos.antigo.log`.
