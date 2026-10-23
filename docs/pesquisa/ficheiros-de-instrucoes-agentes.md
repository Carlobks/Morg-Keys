# Ficheiros de instruções para agentes (AGENTS.md, Copilot, Cursor, Codex)

Pesquisa de 2026-10-23.

| Ferramenta | Ficheiro | Tamanho recomendado | Fonte |
|---|---|---|---|
| Claude Code | `CLAUDE.md` (+ `.claude/rules/` com `paths`) | < 200 linhas | https://code.claude.com/docs/en/memory |
| Padrão aberto | `AGENTS.md` ("a README for agents"), sem campos obrigatórios; o mais próximo do ficheiro editado vence | sem limite | https://agents.md/ |
| OpenAI Codex | `AGENTS.md` da raiz até à pasta atual | 32 KiB (`project_doc_max_bytes`) | https://learn.chatgpt.com/docs/agent-configuration/agents-md |
| GitHub Copilot | `.github/copilot-instructions.md`, `*.instructions.md` com `applyTo`; aceita AGENTS.md e CLAUDE.md | "no longer than 2 pages" | https://docs.github.com/en/copilot/how-tos/configure-custom-instructions/add-repository-instructions |
| Cursor | regras em `.cursor/rules` | < 500 linhas, "focused, actionable, and scoped" | https://cursor.com/docs/context/rules |
| HumanLayer | CLAUDE.md da raiz < 60 linhas; total < 300 | modelos seguem ~150–200 instruções (afirmação deles) | https://www.humanlayer.dev/blog/writing-a-good-claude-md |

## Pontos comuns
- Curto, imperativo, com os **comandos exatos**; ligar a documentos em vez de colar.
- "Never send an LLM to do a linter's job" (HumanLayer): o que uma ferramenta verifica não vai para o ficheiro.
- Birgitta Böckeler (Thoughtworks): construir as regras aos poucos; contexto a mais baixa a eficácia.
  https://martinfowler.com/articles/exploring-gen-ai/context-engineering-coding-agents.html

## Relação AGENTS.md ↔ CLAUDE.md neste projeto
O Claude Code ignora AGENTS.md se houver CLAUDE.md. Se outra ferramenta precisar de AGENTS.md, o CLAUDE.md
importa-o com `@AGENTS.md` (no Windows, ligações simbólicas pedem o modo de programador).
