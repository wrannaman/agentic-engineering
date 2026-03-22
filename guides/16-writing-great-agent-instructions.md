# Writing Great Agent Instructions (CLAUDE.md / AGENTS.md)

The CLAUDE.md or AGENTS.md file is the single most important file in your repo for agentic engineering. It's loaded into the agent's context at the start of every session. Everything the agent does is shaped by what's in this file.

Get it right: the agent follows your patterns, uses your KB, and produces code that matches your team's style. Get it wrong: the agent ignores your KB, invents its own patterns, and you spend review cycles correcting the same issues.

## The Rules

### 1. Keep It Short

**Under 150 lines.** Ideally under 60.

Research shows frontier LLMs reliably follow [150-200 instructions](https://www.humanlayer.dev/blog/writing-a-good-claude-md). Since the agent's system prompt already contains ~50 instructions, your CLAUDE.md budget is about 100-150. If you exceed this, the agent starts ignoring things — and you can't predict which things.

### 2. Universally Applicable Only

Every line in CLAUDE.md should be relevant to **every task** the agent might do in this repo. If it's only relevant to database tasks, it shouldn't be in CLAUDE.md — it should be in the KB.

**Include:**
- How to build/test/lint (`npm test`, `dotnet build`, etc.)
- Which KB partition to use
- Workflow instructions ("always use /plan before implementing")
- Critical constraints ("never modify the auth middleware directly")

**Don't include:**
- Code style rules (that's what linters are for)
- Database schemas (put in KB)
- API documentation (put in KB)
- Task-specific instructions (put in KB or skill files)

### 3. Never Send an LLM to Do a Linter's Job

Don't put code style rules in CLAUDE.md. The agent will follow them inconsistently. Instead:
- Configure your linter/formatter
- Let CI enforce it
- The `/pr-push` skill auto-fixes lint failures

LLMs are in-context learners — they naturally follow the patterns they see in your codebase. If your code is consistently formatted, the agent matches it without being told.

### 4. Pointers, Not Copies

Don't paste code snippets into CLAUDE.md. Reference them:

```markdown
## Error Handling
See `src/utils/errors.ts` for the canonical error handling pattern.
Always use `AppError` from that file, not raw `throw new Error()`.
```

The agent can read the file when it needs to. Pasting the code into CLAUDE.md wastes context and goes stale.

### 5. Progressive Disclosure

Keep the root CLAUDE.md minimal. Put detailed docs in the KB or in `agent_docs/`:

```markdown
# CLAUDE.md

## Build & Test
- Build: `npm run build`
- Test: `npm test`
- Lint: `npm run lint`

## Knowledge Base
Use the `kb` MCP tools. Pass partition="frontend" for this repo.
Start by reading the index: `list_documents(partition="frontend")`

## Workflow
Use /plan before implementing. Use /review before pushing.
Never push to main directly.
```

That's it. 20 lines. Everything else lives in the KB where the agent can search for it when needed.

## The Template

```markdown
# CLAUDE.md

## Build & Test
- Build: `[your build command]`
- Test: `[your test command]`
- Lint: `[your lint command]`

## Knowledge Base
Use the `kb` MCP tools. Pass partition="[your partition]" for this repo.
Start by reading the index: `list_documents(partition="[your partition]")`

When working on [specific area], also check partition="[other partition]".

## Workflow
- Use /plan before implementing any feature
- Use /review before pushing
- Use /compound after features are merged
- Never push to main directly
- All PRs are draft until a human publishes them

## Critical Constraints
- [Anything the agent must NEVER do — e.g., "never modify auth middleware directly"]
- [Anything the agent must ALWAYS do — e.g., "always run migrations via the CLI, not raw SQL"]
```

## What Vercel Found

[Vercel tested AGENTS.md against skills-based RAG](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals) and found:

- A compressed 8KB index in AGENTS.md achieved **100% pass rate**
- Skills-based retrieval (on-demand RAG) achieved **53-79%**
- "With AGENTS.md, there's no moment where the agent must decide 'should I look this up?'"

The lesson: **always-available context beats on-demand retrieval.** But the context must be minimal and relevant. A 5000-line CLAUDE.md is worse than a 50-line one that points to a searchable KB.

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| 500+ line CLAUDE.md | Cut to <100 lines. Move details to KB. |
| Code style rules in CLAUDE.md | Delete them. Configure linter instead. |
| Pasted code snippets | Replace with file references. |
| Task-specific instructions | Move to KB. CLAUDE.md is for universal rules. |
| "When working on auth, do X" | Put auth patterns in KB under the right partition. |
| No mention of KB or skills | Add 3 lines pointing to KB + workflow. |

## Sources

- [Writing a Good CLAUDE.md](https://www.humanlayer.dev/blog/writing-a-good-claude-md) — HumanLayer
- [AGENTS.md Outperforms Skills](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals) — Vercel
- [Claude Code Best Practices](https://code.claude.com/docs/en/best-practices) — Anthropic
- [Effective Context Engineering](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — Anthropic
