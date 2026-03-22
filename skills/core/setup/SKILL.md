# Setup

> Interactive guided setup for the entire agentic engineering stack.

**Status:** Skeleton — full skill content coming in a later phase.

## Purpose

Walk a new user through deploying and configuring everything — KB server, skills, repo configuration, KB seeding, and verification — interactively. The agent does the work; the user answers questions and confirms.

SETUP.md is the reference. This skill is what you actually run.

## Process

### Step 1: Prerequisites Check

Verify required tools are installed:
- [ ] Docker / Docker Compose
- [ ] GitHub CLI (`gh`)
- [ ] Git
- [ ] Coding agent (Claude Code, Cursor, Codex)

Report what's missing with install instructions.

### Step 2: Deploy KB Server

Ask: "Where do you want to deploy the KB server?"
- **Local (docker-compose)** — Run `docker-compose up -d` in `apps/kb-server/`
- **Cloud (Railway/Fly.io)** — Guide through deploy steps
- **Already deployed** — Ask for URL and verify health

Verify: `curl $KB_SERVER_URL/health` returns healthy.

### Step 3: Authentication

Generate a strong auth token. Save to `.env`. Configure the KB server.

### Step 4: Install Skills

Run `skills/install.sh` — auto-detects agent runtime.

Verify: Skills are recognized by the agent.

### Step 5: Configure Project Repos

Ask: "Which repos do you want to set up?"

For each repo:
- Write `CLAUDE.md` (or `AGENTS.md`) from template
- Write `.mcp.json` from template, configured with KB server URL and token
- Create `.llm/learnings/` directory structure

### Step 6: Seed the Knowledge Base

Ask: "Do you have existing docs, or start with examples?"

- **Examples** — Copy `examples/seed-kb/` into a new partition
- **Existing docs repo** — Configure KB server to sync it
- **Start empty** — Skip (not recommended)

### Step 7: Configure Hooks (Optional)

Ask: "Set up enforcement hooks?"

If yes, install:
- session-compound (recommended)
- pr-workflow (recommended)
- Others as desired

### Step 8: Verification

Run end-to-end check:
1. List KB documents via MCP — confirm docs are indexed
2. Confirm skills are loaded — list available skills
3. Run a test brainstorm — verify KB context is loaded

### Step 9: Summary

```
=== Setup Complete ===

KB Server:     https://your-server:8080 ✅
Skills:        16 installed ✅
Repos:         2 configured ✅
KB Documents:  12 indexed ✅
Hooks:         2 active ✅

Try: /brainstorm <your first feature>
```

## When to Use

- First-time setup of the agentic engineering stack
- Adding a new team member
- Configuring a new project repo
- Re-running after upgrading

## Hard Rules

- Never skip the verification step
- Always generate strong auth tokens (not "password123")
- Always verify KB connectivity before declaring success
- If any step fails, stop and help the user fix it before continuing
