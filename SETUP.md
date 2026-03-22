# Setup Guide

Step-by-step deployment of the agentic engineering stack.

## Prerequisites

- Docker and Docker Compose
- A GitHub account
- A coding agent: Claude Code, Cursor, Codex, GitHub Copilot, or similar
- (Optional) A Slack workspace for the "anyone can ship" workflow

## Day 1: Deploy the Stack (2-4 hours)

### 1. Clone This Repo

```bash
git clone <repo-url> agentic-eng
cd agentic-eng
```

### 2. Deploy the Knowledge Base Server

The KB server is the team's shared brain. Agents connect to it via MCP to retrieve coding standards, architecture decisions, and learnings.

```bash
cd apps/kb-server
cp .env.example .env
# Edit .env with your configuration (see below)
docker-compose up -d
```

**Required environment variables:**

| Variable | Purpose |
|----------|---------|
| `KB_AUTH_TOKEN` | Bearer token for MCP/API authentication |
| `DATABASE_URL` | PostgreSQL connection string |
| `GH_TOKEN` | GitHub PAT for repo sync (read access to docs repos) |

**Verify it's running:**

```bash
curl -H "Authorization: Bearer $KB_AUTH_TOKEN" https://your-server/health
# Expected: {"status": "healthy"}
```

See [apps/kb-server/README.md](apps/kb-server/README.md) for deployment options (Railway, Fly.io, Render, self-hosted).

### 3. Install Skills

```bash
cd skills
./install.sh
```

The installer detects your coding agent (Claude Code, Cursor, Codex) and symlinks or copies skills into the appropriate directory.

### 4. Configure Your Project Repos

For each repo where you want agents to use the KB:

```bash
# Copy and customize templates
cp templates/CLAUDE.md.template your-repo/CLAUDE.md
cp templates/.mcp.json.template your-repo/.mcp.json
```

Edit the templates to:
- Point to your KB server URL
- Map file types and paths to KB partitions (e.g., `*.tsx` → `frontend-kb`)
- Set your bearer token (via environment variable, not hardcoded)

## Day 2-3: Seed the Knowledge Base

### 5. Create a Docs Repo

Create a GitHub repo for your KB content. This is where your team's knowledge lives:

```
your-org/kb-docs/
├── frontend/
│   ├── coding-standards.md
│   ├── component-patterns.md
│   └── testing-strategy.md
├── backend/
│   ├── api-conventions.md
│   ├── database-patterns.md
│   └── error-handling.md
└── architecture/
    ├── service-boundaries.md
    └── data-flow.md
```

Use the examples in `examples/seed-kb/` as a starting point.

### 6. Configure the KB Server to Sync

Add your docs repo as a partition in the KB server:

```bash
curl -X POST https://your-server/repo \
  -H "Authorization: Bearer $KB_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "frontend-kb",
    "url": "https://github.com/your-org/kb-docs.git",
    "branch": "main",
    "inclusionFilter": "frontend/*.md"
  }'
```

The server will clone and index the docs. New content syncs automatically when PRs merge to main.

### 7. Test the Connection

Ask your agent to list the KB:

```
List the knowledge base documents in the kb knowledge base.
```

The agent should connect via MCP and return your indexed documents.

## Week 1: First Full Cycle

### 8. Run the Workflow

Pick a small feature and run the full cycle:

```
/brainstorm <feature>     # Explore unknowns
/plan <feature>           # Research-first design (loads KB context)
/work .plans/...          # Step-by-step implementation
/review                   # Multi-perspective AI review
/compound                 # Extract learnings → KB
```

### 9. Verify the Compound Loop

After running `/compound`, check that learnings were created:

```bash
ls your-repo/.llm/learnings/
# Should contain new .md files with extracted patterns
```

## Week 2+: Scale

### 10. Set Up the Review Bot

See [integrations/review-bot/README.md](integrations/review-bot/README.md) for setting up CodeRabbit, Ellipsis, or similar.

### 11. Set Up Hooks

Copy hooks from `skills/hooks/` into your agent's hooks configuration. Start with:
- `session-compound` — auto-detect gaps after every session
- `pr-workflow` — enforce the PR skill before `gh pr create`

### 12. Enable "Anyone Can Ship" (Optional)

See [guides/08-anyone-can-ship.md](guides/08-anyone-can-ship.md) for setting up:
- GitHub Codespaces with pre-configured devcontainer
- Slack integration for non-engineer PR creation

## Troubleshooting

### Agent can't connect to KB server

1. Verify the server is running: `curl https://your-server/health`
2. Check your MCP config: the URL should end in `/mcp`
3. Check your auth token is set correctly
4. Run `/mcp list` (Claude Code) to verify the connection

### Skills not recognized

1. Re-run `./install.sh` and check the output
2. Restart your coding agent to reload skills
3. Check that the skill files are in the correct directory for your agent

### Compound loop not generating learnings

1. Ensure `.llm/learnings/` directory exists in your project
2. Check that the agent has write access to the directory
3. Try running `/compound` manually after a completed feature

See [guides/13-faq.md](guides/13-faq.md) for more.
