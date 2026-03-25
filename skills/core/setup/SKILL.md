---
name: setup
description: "Interactive guided setup. Detects your codebase, configures MCP, writes project-specific CLAUDE.md, seeds the KB, and verifies everything works."
---

# Setup

> From zero to working agentic engineering in one session.

Walk a new user through the entire stack: detect their codebase, deploy or connect to a KB server, write project-specific configuration, optionally seed the KB, and verify it all works.

The agent does the work. The user answers questions and confirms.

## Process

### Step 0: Quick or Full?

Before anything else, ask ONE question:

```
What are you looking to do?

  1. Just try it out — get a local KB running with the example docs in 2 minutes
  2. Set this up for real — connect to my codebase, configure everything properly
```

**If "just try it out" (the quick path):**

Skip everything and do this:

```bash
cd apps/kb-server
python -m venv .venv && source .venv/bin/activate
pip install -e .
REPOS="kb:../../examples/seed-kb" python -m src.server &
```

Then configure the agent to connect:
```bash
# For Claude Code:
claude mcp add --transport http kb http://localhost:8080/mcp
```

Done. Say:
```
KB server running at http://localhost:8080 with 5 example docs.
Try: list_documents() to see what's in the KB.

When you're ready to add your own docs, just drop markdown files into
examples/seed-kb/ (or any folder) and hit localhost:8080/api/sync.

Run /setup again and pick option 2 when you want the full configuration.
```

That's the entire quick path. No more questions. They're up and running.

**If "set this up for real":** Continue to Step 1.

### Step 1: Where Am I?

First, figure out if the user is in the agentic-eng repo or in their own project:

```bash
# Check if we're in the agentic-eng repo itself
ls apps/kb-server/src/server.py 2>/dev/null && ls skills/core/plan/SKILL.md 2>/dev/null
```

**If we're in the agentic-eng repo:**

They just cloned it. They need to:
1. Start the KB server (done in Step 0 quick path, or Step 2 full path)
2. Install skills into their agent
3. Then go to their actual project and configure it

```
It looks like you're in the agentic-eng repo itself — not a project you want to configure.

Let's get you set up:
  1. ✅ Start the KB server (done — or we'll do it in Step 2)
  2. Install skills: cd skills && ./install.sh
  3. Go to your project: cd /path/to/your/project
  4. Run /setup again from there to configure your project

What's the path to the project you want to configure?
```

If they give a path, `cd` there and continue to project detection. If they don't have a project yet or just want to explore, point them at `examples/sample-project/` — it's a minimal project with AGENTS.md and .mcp.json already configured.

**If we're in a real project:** Continue to project detection.

### Step 1b: Detect the Project

Scan the current directory:

```bash
# Detect language and framework
ls package.json 2>/dev/null      # Node/TypeScript/JavaScript
ls pyproject.toml 2>/dev/null     # Python
ls *.csproj *.sln 2>/dev/null     # .NET/C#
ls go.mod 2>/dev/null             # Go
ls Cargo.toml 2>/dev/null         # Rust
ls pom.xml build.gradle 2>/dev/null  # Java/Kotlin

# Detect build/test commands
cat package.json | jq '.scripts' 2>/dev/null   # npm/yarn scripts
cat Makefile 2>/dev/null | head -20             # Make targets
ls Dockerfile docker-compose.yml 2>/dev/null    # Docker

# Detect existing agent config
ls CLAUDE.md .cursorrules AGENTS.md .cursor/ .codex/ 2>/dev/null

# Detect git info
git remote get-url origin 2>/dev/null
git branch --show-current
```

**Present findings:**
```
## Project Detected

Language:   TypeScript (React + Node.js)
Build:      npm run build
Test:       npm test
Lint:       npm run lint
Framework:  Next.js 15
Git remote: github.com/yourorg/yourapp
Agent:      Claude Code (CLAUDE.md exists but is empty)

Is this correct? [Y/n]
```

If wrong, ask the user to correct. If no project is detected (empty directory), note that and continue — they may be setting up the KB server first.

### Step 2: KB Server Connection

Ask ONE question:

```
Do you have a KB server running?
  1. Yes — I'll give you the URL
  2. No, run it locally (recommended for solo / trying it out)
  3. No, deploy with Docker (for teams / production)
  4. Skip for now — I'll set it up later
```

**If yes (remote):**
- Ask for the URL
- Ask for the auth token (or help them set an env var)
- Verify: `curl -H "Authorization: Bearer $TOKEN" $URL/health`
- If healthy, continue. If not, debug.

**If local (the solo developer path):**

This is the zero-friction path. No Docker, no cloud, no auth token. Just Python and a folder of markdown files.

Most people will just use this repo itself as their KB — add docs to `examples/seed-kb/` or create a new folder. Walk them through it:

```
Where do you want to keep your KB docs?

  1. Right here in this repo (easiest — start adding to examples/seed-kb/)
  2. A separate folder I already have
  3. I'll create one later
```

**If "right here in this repo" (most common):**

The `examples/seed-kb/` folder already has starter docs. They can add their own alongside them, or create new partition folders:

```
examples/seed-kb/
├── coding-standards/     ← add your team's standards here
├── architecture/         ← add your architecture docs here
├── workflows/            ← add your workflow docs here
└── my-project/           ← create new folders for new partitions
```

Set up and start the server:
```bash
cd apps/kb-server
python -m venv .venv && source .venv/bin/activate
pip install -e .

# Point at the seed-kb folder in this repo
REPOS="kb:../../examples/seed-kb" python -m src.server
```

**If "a separate folder":**
```bash
cd apps/kb-server
python -m venv .venv && source .venv/bin/activate
pip install -e .

REPOS="kb:/path/to/their/docs" python -m src.server
```

**Either way:** Server runs at `localhost:8080`. No auth needed locally. SQLite. The agent connects to `http://localhost:8080/mcp`. Add or edit markdown files anytime — the server re-indexes every 5 minutes, or hit `localhost:8080/api/sync` to force it.

Help them start the server in the background so it persists:
```bash
REPOS="kb:../../examples/seed-kb" nohup python -m src.server > /tmp/kb-server.log 2>&1 &
echo "KB server running at http://localhost:8080"
```

To keep it running in the background:
```bash
REPOS="kb:$HOME/kb-docs" DATABASE_URL="sqlite:///kb.db" nohup python -m src.server &
```

Add docs to `~/kb-docs/` anytime. The server re-indexes every 5 minutes (configurable via `SYNC_INTERVAL_SECONDS`), or hit `/api/sync` to force it.

**If Docker (teams):**
```bash
cd apps/kb-server
cp .env.example .env
# Edit .env: set REPOS, optionally set KB_AUTH_TOKEN
docker-compose up -d
```
- Verify health endpoint

**If skip:**
- Continue without KB. Skills still work — they just don't load KB context. Note this in the summary.

### Step 3: Configure MCP Connection

If KB server is connected, write `.mcp.json` in the project root:

```json
{
  "mcpServers": {
    "kb": {
      "type": "http",
      "url": "KB_SERVER_URL/mcp",
      "headers": {
        "Authorization": "Bearer TOKEN"
      }
    }
  }
}
```

Use the actual URL and token from Step 2. Ask which env var name they want for the token (default: `KB_AUTH_TOKEN`).

Also check if they need to add the MCP server to their agent:
```bash
# For Claude Code
claude mcp add --transport http kb $KB_URL --header "Authorization: Bearer $TOKEN"
```

### Step 4: Write Project-Specific CLAUDE.md

Using the project detection from Step 1, generate a `CLAUDE.md` tailored to this project:

```markdown
# CLAUDE.md

## Build & Test
- Build: `[detected build command]`
- Test: `[detected test command]`
- Lint: `[detected lint command]`

## Knowledge Base
Use the `kb` MCP tools. Pass partition="[detected or asked partition]" for this repo.
Start by reading the index: `list_documents(partition="[partition]")`

## Workflow
- Use /plan before implementing any feature
- Use /review before pushing
- Use /compound after features are merged
- Never push to main directly
- All PRs are draft until a human publishes them
```

**If a CLAUDE.md already exists:**
- Read it
- Ask: "You have an existing CLAUDE.md. Want me to merge the KB instructions into it, or replace it?"

**If the user uses Cursor:**
- Also write equivalent `.cursorrules` or offer to

**If the user uses Codex:**
- Write `AGENTS.md` instead

### Step 5: Determine KB Partition

If KB is connected:

```
What should the KB partition be for this repo?

Your KB server has these partitions: [list from API]
  - frontend (42 docs)
  - backend (18 docs)
  - infra (5 docs)

Or create a new partition by naming it (partitions = folders in your KB docs repo).

Partition for this repo: [suggestion based on detected language/framework]
```

If no KB partitions exist yet, suggest one based on the project type.

### Step 5b: Configure the Compound Loop Target

The compound skill needs to know where to send team-wide learnings. Ask:

```
Where does your KB content live? (This is where /compound will create PRs)

  1. A GitHub repo — give me the org/repo (e.g., yourorg/kb-docs)
  2. Same repo as the code — KB docs live alongside the code
  3. I'll configure this later
```

**If a GitHub repo:**
- Record the repo as `KB_DOCS_REPO` (e.g., `yourorg/kb-docs`)
- Verify the user has push access: `gh repo view $KB_DOCS_REPO --json name`
- Write this to the project config so `/compound` knows where to PR:

Add to `CLAUDE.md`:
```markdown
## Compound Loop
When /compound finds team-wide learnings, create a PR to `KB_DOCS_REPO`.
Target the partition folder matching this repo (e.g., `frontend/`).
```

**If same repo:**
- Learnings go into a `kb/` directory in the project repo
- Compound creates PRs to the same repo

**Critical: also add the "edit not add" instruction to CLAUDE.md:**
```markdown
## KB Writing Rules
When adding to the knowledge base, ALWAYS search for existing docs on the topic first.
If a related doc exists, propose an EDIT (add a section, update a paragraph).
Only create a new doc if nothing related exists.
Favor surgical precision over comprehensive coverage. Think wiki, not blog.
```

This ensures the compound loop doesn't just pile on new docs forever.

### Step 6: Create Learnings Directory

```bash
mkdir -p .llm/learnings/gotchas
mkdir -p .llm/learnings/patterns
mkdir -p .llm/learnings/code-patterns
mkdir -p .llm/learnings/debug-patterns
```

Add to `.gitignore` if not already there:
```
# Agent plans (ephemeral)
.claude/plans/
```

Note: `.llm/learnings/` should be committed — these are project-specific patterns that persist.

### Step 7: Seed the KB (Optional)

If KB is connected and the partition is empty:

```
Your KB partition "[partition]" has 0 documents. Want to seed it?

  1. Run /seed — auto-generate KB docs from this codebase (recommended)
  2. Copy example docs — start with generic templates
  3. Skip — I'll add docs manually later
```

If they choose `/seed`, invoke it. If examples, copy from `examples/seed-kb/` and adapt the partition.

### Step 8: Verify Everything

Run checks in sequence:

```
## Verification

1. KB Server health............. ✅ healthy (https://kb.company.com)
2. MCP connection............... ✅ 3 tools available (list_documents, read_document, search_documents)
3. KB partition................. ✅ "frontend" — 42 documents indexed
4. CLAUDE.md.................... ✅ written with build/test/lint + KB config
5. .mcp.json.................... ✅ configured with KB URL + auth
6. .llm/learnings/.............. ✅ directory structure created
7. Skills installed............. ✅ 20 skills recognized
```

If any check fails, explain what went wrong and how to fix it.

### Step 9: Summary

```
## Setup Complete

Project:       yourorg/yourapp (TypeScript/React)
KB Server:     https://kb.company.com ✅
KB Partition:  frontend (42 docs)
MCP:           .mcp.json configured ✅
Agent Config:  CLAUDE.md written ✅
Learnings:     .llm/learnings/ created ✅
Skills:        20 installed ✅

### What's Ready
- /plan, /work, /review, /compound — the full cycle
- /ship — plan+implement+review+push in one shot
- /seed — generate more KB docs from your codebase
- /debug — parallel bug investigation

### Recommended First Steps
1. Run /plan on a small feature to test the cycle
2. After the PR merges, run /compound to extract learnings
3. Have your senior engineers review and add to the KB partition

### If the KB is empty
Run /seed to auto-generate starter docs from your codebase.
Your senior engineers should review the drafts before they go into the KB.
```

## When to Use

- First-time setup of agentic engineering in a project
- Configuring a new repo to use an existing KB server
- Onboarding a new team member (run `/setup` in each repo they work in)
- After cloning the agentic-eng repo for the first time

## Hard Rules

- Never skip verification (Step 8)
- Never hardcode tokens in files — use env vars
- If CLAUDE.md exists, ask before overwriting
- If .mcp.json exists, ask before overwriting
- Always detect the project before asking questions (Step 1 before Step 2)
- If a step fails, stop and fix it before continuing
