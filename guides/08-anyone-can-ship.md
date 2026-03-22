# Anyone Can Ship

Designers, PMs, and non-engineers creating meaningful PRs without a local dev environment.

## The Flow

```
Slack command ("fix the header color on /pricing")
    → GitHub Codespaces spins up (pre-configured)
    → Agent runs brainstorm → plan → work → review
    → Draft PR created
    → Engineer reviews and merges
```

## Requirements

1. **GitHub Codespaces** with a devcontainer pre-configured with:
   - Skills installed
   - MCP connected to KB
   - Agent runtime ready (Claude Code, Codex, etc.)

2. **Slack integration** (optional) — slash command or bot that:
   - Takes a text description of the change
   - Creates a Codespace
   - Runs the agent with the prompt
   - Posts back the PR link

3. **Guardrails:**
   - Non-engineer PRs are always draft
   - Always require engineer review
   - Always run CI

## Setting Up Codespaces

See `apps/codespaces/.devcontainer/` for the devcontainer configuration.

## Setting Up Slack

See `apps/slack-trigger/` for sample Slack app configurations.

## What Works Well

- Copy and content changes
- Styling tweaks
- Configuration changes
- Simple features that follow existing patterns
- Bug fixes with clear reproduction steps

## What Still Needs Engineers

- Novel architecture
- Performance-critical changes
- Security-sensitive code
- Complex integrations
- Changes with unclear requirements
