# Quota do Claude na barra: de onde vêm os dados

Pesquisa de 2026-10-24 (pedido do utilizador: ver o ai-usagebar do Fabio Akita). Código lido com `gh api`;
regras lidas nas páginas oficiais da Anthropic.

## O que o Morg Keys faz hoje
- A barra mostra `5h …% · sem …%`, lidos do `~/.claude/rate_limits.json` pelo `claude_usage.py`.
- Esse ficheiro é escrito pelo `~/.claude/statusline.py`. O Claude Code passa à `statusLine` o campo oficial
  `rate_limits` (`five_hour`/`seven_day` com `used_percentage` e `resets_at`).
- **Problema verificado neste PC (2026-10-24):** o `rate_limits.json` nunca foi criado. O utilizador usa o Claude
  Code na aplicação de ambiente de trabalho, que não corre a `statusLine`, e por isso a barra fica sempre em "—".

## Como o ai-usagebar obtém o uso (github.com/akitaonrails/ai-usagebar)
- **Projeto:** Rust, licença MIT, ativo (último envio a 2026-10-22).
- **No Windows:** só há o ícone na bandeja e a TUI. O widget da barra é só para Wayland.
- **Pedido:** `GET https://api.anthropic.com/api/oauth/usage` (`src/anthropic/fetch.rs`), que o próprio projeto
  marca como **não documentado**.
  - Cabeçalhos: `Authorization: Bearer <token OAuth>`, `anthropic-beta: oauth-2025-04-20` e um `User-Agent` que
    imita o CLI (`claude-cli/2.1.281 (external, cli)`); o código diz que sem ele o servidor responde 429.
  - Resposta: `five_hour` e `seven_day` com `utilization` (%) e `resets_at` (ISO 8601).
- **Credencial:** o token vem do `%USERPROFILE%\.claude\.credentials.json` (`claudeAiOauth.accessToken`,
  `expiresAt` em ms).
  - Quando o token expira, renova-o em `https://platform.claude.com/v1/oauth/token` com o `client_id` do Claude
    Code e **reescreve o ficheiro de credenciais** (`src/anthropic/oauth.rs`, `creds.rs`).
  - Também lê o token guardado pela aplicação de ambiente de trabalho (`desktop_creds.rs`).

## O que dizem as regras oficiais
`code.claude.com/docs/en/legal-and-compliance`, secção "Authentication and credential use":
- a autenticação OAuth destina-se ao uso normal do Claude Code e das aplicações da Anthropic;
- quem desenvolve produtos deve usar chaves de API;
- "developers may not collect, store, or intermediate Claude.ai credentials or session tokens";
- a Anthropic pode aplicar estas restrições "without prior notice".

Houve aplicação do lado do servidor em 2026: tokens recusados fora do Claude Code (GitHub anthropics/claude-code
#28089; notícias de fevereiro de 2026).

## Conclusão para o Morg Keys (público, GPL-3.0)
- **Via oficial:** só o `rate_limits` da `statusLine`, que só chega quando o Claude Code corre num terminal.
- **Via do ai-usagebar:** funciona também com a aplicação de ambiente de trabalho, mas tem três problemas:
  - lê o token da conta e usa um endpoint não documentado com um `User-Agent` que imita o CLI;
  - na renovação, reescreve as credenciais do Claude Code (pode deixar o Claude Code sem sessão se os dois
    renovarem ao mesmo tempo);
  - num projeto distribuído a outras pessoas, choca com a regra acima, e o risco recai sobre a conta paga de
    quem usa.
- **Recomendação:** ficar na via oficial e dar a opção de ocultar.
