# CLAUDE.md

This repo is an agentic engineering architecture. Part docs, part code, part skills.

## Build & Test (KB Server)
```bash
cd apps/kb-server
python -m venv .venv && source .venv/bin/activate
pip install -e .
pytest tests/
```

## Repo Structure
- `apps/kb-server/` — Python MCP knowledge base server
- `skills/` — 18 agent skills + 5 hooks (markdown)
- `guides/` — documentation (markdown)
- `integrations/` — review bot, OTEL configs
- `templates/` — starter configs for client repos
- `examples/` — seed KB docs and sample project

## Rules
- No vendor or company-specific branding — this repo is open source and tool-agnostic
- Skills should work with any coding agent, not just Claude Code
- Keep guides concise — Hemingway, not Tolstoy
- KB server must stay under 1000 lines of Python
- Every claim needs evidence (link to source)
