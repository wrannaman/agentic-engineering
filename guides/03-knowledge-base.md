# Knowledge Base: Setup and Seeding

The knowledge base (KB) is the team's shared brain. Agents connect to it via MCP to retrieve coding standards, architecture decisions, and compound learnings.

## Why Simple Search Beats RAG

You might wonder: why full-text keyword search instead of vector embeddings and RAG?

[Vercel tested this directly.](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals) They compared three approaches for teaching agents framework-specific knowledge:

| Approach | Pass Rate |
|----------|----------|
| Baseline (no docs) | 53% |
| Skills-based retrieval (on-demand RAG) | 53% |
| Skills with explicit instructions | 79% |
| **Compressed docs in AGENTS.md** | **100%** |

The key findings:

1. **RAG with no explicit instructions performed identically to having no docs at all.** The skill existed, the agent could use it, and the agent chose not to. Zero improvement.
2. **Passive context beats on-demand retrieval.** With AGENTS.md, there's no moment where the agent decides "should I look this up?" The information is always available.
3. **They compressed 40KB of docs down to 8KB (80% reduction) and maintained 100% pass rates.** A minimal, curated index beats a full retrieval system.

**What this means for our KB:**

You don't need embeddings. You don't need vector databases. You don't need semantic search over thousands of documents. What you need is:

- **Curated, concise documents** — not a dump of everything, but the 50-200 docs that actually matter
- **Full-text keyword search** — so the agent can find the right doc when it needs to
- **The CLAUDE.md/AGENTS.md pointing the agent to the KB** — so it knows to look

The KB server in this repo uses FTS5 (SQLite) or tsvector (Postgres). No embeddings, no vector DB, no API keys, no complexity. On a curated corpus of team documentation, keyword search is sufficient because the documents are written by humans with clear titles and keyword frontmatter. The agent doesn't need cosine similarity to find "React component testing patterns" — it needs `search_documents(query="react component testing")`.

If your KB grows to 10,000+ documents and keyword search starts returning noise, you can add embeddings later. But for most teams (50-500 docs), you'll never need to.

## Required Capabilities

Any KB server must support these 8 capabilities:

| # | Capability | Why |
|---|-----------|-----|
| C1 | MCP transport | Coding agents connect via MCP |
| C2 | Document listing | Agents browse available documents |
| C3 | Retrieval by path | Agents read specific documents |
| C4 | Keyword/semantic search | Agents find relevant docs by topic |
| C5 | Partitioning | Frontend docs don't pollute backend context |
| C6 | Git-backed content sync | PRs merged to main auto-sync to KB |
| C7 | Authentication | Bearer tokens at minimum |
| C8 | Remote deployment | HTTP server, not just local |

See [apps/kb-server/docs/capabilities.md](../apps/kb-server/docs/capabilities.md) for the full spec.

## The Git Interface

Content authoring happens through git:

1. Your team maintains a docs repo (or multiple, one per partition)
2. Anyone can create a PR adding or updating a document
3. PR gets reviewed (quality gate — bad docs don't get in)
4. On merge to main, KB server auto-syncs

This is intentionally simple. No special tooling. No manual uploads. Just git.

## Partitioning Strategy

Partitions prevent cross-pollination. An agent working on the frontend shouldn't get backend docs in its context.

**Partitions are URL paths.** Same MCP tools at every endpoint:

On disk, partitions are just **folders** in your docs repo:

```
kb-docs/
├── frontend/       → partition "frontend"
├── backend/        → partition "backend"
├── infra/          → partition "infra"
└── architecture/   → partition "architecture"
```

Adding a partition = creating a folder. Agents pass `partition="frontend"` to scope tool results. Leave empty to search everything.

**Recommended partitions:**

| Partition | Contents | Who Maintains |
|-----------|----------|--------------|
| `frontend` | Component patterns, styling, state management | Frontend team |
| `backend` | API conventions, database patterns, error handling | Backend team |
| `infra` | Deployment, CI/CD, monitoring | Platform team |
| `architecture` | System design, service boundaries, data flow | Tech leads |

**Where do compound learnings go?** Into the partition they belong to. A gotcha about React Query goes in `frontend/`. A gotcha about database migrations goes in `backend/`. Compound learnings are team knowledge — they live alongside the other docs in the relevant partition, not in a separate junk drawer.

Project-specific learnings (things that aren't team-wide) stay in `.llm/learnings/` in the project repo, not in the KB server.

## Seeding: Cold Start

An empty KB means agents fall back to pre-training knowledge, which defeats the purpose. Seed with:

1. **Coding standards** — How your team writes code (naming, error handling, testing patterns)
2. **Architecture docs** — Service boundaries, data flow, key design decisions
3. **Common patterns** — "Here's how we do X" for recurring tasks (new API endpoint, new React page, database migration)
4. **Gotchas** — Things that trip people up ("don't use X because Y")

See `examples/seed-kb/` for starter templates.

## Document Format

KB documents are markdown with YAML frontmatter:

```markdown
---
keywords: react, components, testing, jest
last_reviewed: 2026-03-01
owner: frontend-team
---

# React Component Testing Patterns

...
```

| Field | Required | Purpose |
|-------|----------|---------|
| `keywords` | Recommended | Improves search accuracy |
| `last_reviewed` | Recommended | Staleness detection (see below) |
| `owner` | Optional | Who to ping when doc needs review |

The first `# Heading` becomes the document title.

## Writing for Search (Not RAG)

The KB uses full-text keyword search, not vector embeddings or semantic similarity. This means how you write docs directly affects whether agents find them. A few principles:

**Titles should match how someone would search.** Not "Considerations for Client-Side Data Management" — use "React Query Data Fetching Patterns." An agent searching for "data fetching" will find the second title, not the first.

**Frontmatter keywords should include synonyms and related terms.** If the doc is about error handling, include: `error handling, exceptions, try catch, error boundary, AppError, error response`. Think about every term someone might search for when they have this problem.

**Section headings should contain the actual terms.** Not "The Approach" — use "## Using React Query for Server State." The search indexes headings along with content.

**Use the specific names from your codebase.** If your error utility is called `AppError`, include `AppError` in the keywords and body. If your data fetching wrapper is called `defineApi`, include `defineApi`. Agents search for the concrete things they see in code.

**Don't keyword-stuff.** The doc should read naturally. But when choosing between a vague heading and a specific one, always pick specific. When choosing whether to mention a related term, mention it. The goal is that any reasonable search query about this topic finds this doc.

```markdown
---
keywords: react query, data fetching, useQuery, staleTime, server state, cache, defineApi, rpc
---

# React Query Data Fetching Patterns

Use `defineApi()` from `@mycompany/rpc` for all API communication. Never use `fetch` directly.

## Query Configuration
...

## Mutation Patterns
...

## Cache Invalidation
...
```

An agent searching for "react query", "data fetching", "defineApi", "useQuery", "staleTime", or "cache invalidation" will all find this doc. That's the goal.

## Staleness Detection

KB docs go stale. Coding standards evolve. Libraries get upgraded. If the KB has outdated patterns, agents will confidently write outdated code.

**Every doc should have a `last_reviewed` date in frontmatter.** A simple periodic check (cron job, GitHub Action, or a skill) flags docs older than a configured threshold:

```bash
# Example: find docs not reviewed in 90+ days
find kb-docs/ -name "*.md" -exec grep -l "last_reviewed:" {} \; | while read f; do
  date=$(grep "last_reviewed:" "$f" | head -1 | cut -d: -f2 | tr -d ' ')
  if [[ $(date -d "$date" +%s 2>/dev/null || date -j -f "%Y-%m-%d" "$date" +%s) -lt $(date -d "90 days ago" +%s 2>/dev/null || date -v-90d +%s) ]]; then
    echo "STALE: $f (last reviewed: $date)"
  fi
done
```

**What to do with stale docs:**
1. Review and update the content
2. Update `last_reviewed` to today
3. If the doc is no longer relevant, delete it (the KB server will remove it on next sync)

**The compound loop helps:** When `/compound` detects that a KB doc led to incorrect guidance, it can flag the doc for review automatically.
