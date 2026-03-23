# Agentic Engineering — The AX Stack

> AX (Agent Experience) is the new DX. UX was for users. DX was for developers. AX is for agents. This is the complete AX stack for engineering teams.

Your engineering team ships 50 features a month. 40 of them follow patterns you've already established — new endpoints that look like existing endpoints, pages that look like existing pages, bug fixes, config changes, copy updates. Your senior engineers spend most of their time on work that's beneath their skill level, not because it's easy, but because nobody else can do it.

That changes here.

**This system gets AI agents to one-shot 90% of new incremental features in existing codebases within 30 days.** Someone describes what they want — an engineer, a PM, a designer — and the agent plans it, implements it, verifies it, and reviews it. The resulting PR needs little to no human modification before merge. Your senior engineers review code instead of writing it. Your designers ship their own changes. Your PMs stop waiting in the ticket queue.

The 30 days are not passive. Your best engineers spend week 1-2 documenting how your team builds software — coding standards, architecture patterns, the "here's how we do X" guides that live in people's heads. That documentation feeds a knowledge base. The knowledge base feeds the agents. Every merged PR extracts learnings back into the KB. Each cycle gets better. That's the compound loop, and it's why this works where "just use Copilot" doesn't.

**This is not a tool. It's a system.** A knowledge base server, 18 agent skills, 5 enforcement hooks, a compound learning loop, automated feedback pipelines, and 16 guides covering everything from philosophy to ROI. It's opinionated — stacked PRs, retrieval-led reasoning, mandatory code review — and it works with any AI coding agent (Claude Code, Cursor, Codex, GitHub Copilot).

This isn't theory. The best engineering organizations in the world are already doing this:

- **Stripe** merges [1,300+ PRs per week](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2) with zero human-written code — agent-produced, human-reviewed
- **Intercom** runs [100+ skills](http://x.com/brian_scanlan/status/2033978300003987527?s=20) with design managers and PMs as their top power users — not engineers
- **TELUS** saved [500,000 engineering hours](https://jellyfish.co/blog/2025-ai-metrics-in-review/) and ships 30% faster
- **Zapier** hit [89% AI adoption](https://claude.com/blog/how-enterprises-are-building-ai-agents-in-2026) across their entire org with 800+ agents deployed
- **Dropbox** engineers using AI ship [20% more PRs while reducing failure rates](https://jellyfish.co/blog/2025-ai-metrics-in-review/)
- [57% of organizations](https://www.langchain.com/state-of-agent-engineering) already have agents running in production. 64% of CIOs plan to deploy agentic AI within 24 months.

If your team is still using AI as a fancy autocomplete — Copilot suggestions, one-off chat conversations, copy-pasting from ChatGPT — you're leaving 10x on the table. The gap between teams doing this well and teams not doing it at all is widening every month. The tools exist. The process is proven. What's missing is the system that ties it all together. That's what this repo is.

Everything here is open source. Deploy it in a day. See results in a week. Hit 90% in a month.

---

## What This Delivers

| Before | After |
|--------|-------|
| Senior engineers write incremental features | Senior engineers review and architect |
| Designers file tickets and wait | Designers ship their own changes via Codespaces |
| New hires take months to learn patterns | New hires get patterns from the KB on day 1 |
| Same review feedback given repeatedly | Compound loop eliminates recurring issues |
| AI agents produce generic code | AI agents follow your team's exact patterns |
| Tribal knowledge lives in people's heads | Tribal knowledge lives in the KB, accessible to agents and humans |

---

## The Goal

**90% one-shot accuracy on new incremental features within 30 days.**

To be specific about what this means: a new feature in an existing codebase where there are patterns to follow. A new API endpoint when you already have 12 endpoints. A new page when you already have 20 pages. A new component when you already have a component library. Bug fixes where the root cause can be identified from logs or reproduction steps. Config changes. Copy updates. Integrations that follow existing integration patterns.

This is the work that makes up 80% of day-to-day engineering. The agent sees your existing patterns (via the KB), follows them (via the skills), and produces code that matches how your team builds software (via the compound loop).

It does not work for greenfield architecture, performance-critical systems, or anything where there's no existing pattern to follow. Those still need senior engineers driving. Anthropic's own research shows developers can [fully delegate only 0-20% of tasks](https://claude.com/blog/eight-trends-defining-how-software-gets-built-in-2026). But the incremental 80% — new features that follow established patterns in a mature codebase — that's where this system delivers 90%.

### How 30 Days Breaks Down

| Week | What Happens | Expected One-Shot Rate |
|------|-------------|----------------------|
| **1** | Deploy KB server. Install skills. Run `/seed` to auto-generate draft KB docs from your codebase. Have senior engineers review and refine. Run 3-5 features through the full cycle. | ~60% |
| **2** | Run `/compound` after every feature. Fix the gaps it finds. Add 10-20 more KB docs based on what agents get wrong. Set up the review bot. | ~70% |
| **3** | Agents start loading learnings automatically during `/plan`. Review feedback volume drops. First non-engineer PR experiments. | ~80% |
| **4** | Compound loop is generating learnings faster than you consume them. Session-level gap detection catches issues within hours. | ~85-90% |

**The hard part is week 1-2.** Not the tooling — the knowledge base. Your most senior engineers need to write clear, specific documentation about how your team builds software. If you half-ass the KB, you get half-ass results. If you write excellent docs, agents follow them religiously.

---

## What This Is

```
agentic-eng/
├── apps/kb-server/        # MCP knowledge base server (Python, ~700 lines)
├── skills/                # 17 agent skills + 5 enforcement hooks
├── guides/                # 15 guides covering everything from philosophy to ROI
├── integrations/          # Review bot, OTEL, LangFuse, Datadog configs
├── templates/             # Starter CLAUDE.md, AGENTS.md, .mcp.json, GitHub Actions
└── examples/              # Seed KB docs and sample project
```

### The Knowledge Base Server

A minimal MCP server that gives your coding agents access to your team's documentation. Built with the official MCP Python SDK, FastAPI, and SQLAlchemy (SQLite for local dev, Postgres for production — one env var to switch).

- **3 tools:** `list_documents`, `read_document`, `search_documents`
- **Partitions:** Top-level folders in your docs repo. Agents pass a `partition` parameter to scope results so frontend docs don't pollute backend context.
- **Git sync:** Clones your docs repo and re-indexes on a configurable interval. PRs merged to main automatically appear in the KB.
- **Auth:** Bearer token. No config beyond one env var.
- **Full-text search:** FTS5 (SQLite) or tsvector (Postgres). No embeddings, no vector DB, no API keys.

### The Skills

Markdown files that guide agents through structured workflows. They work with any agent that supports skills/instructions (Claude Code, Cursor, Codex, Copilot, etc.).

**Core cycle:**
| Skill | What It Does |
|-------|-------------|
| `/setup` | Interactive guided setup of the entire stack |
| `/seed` | Auto-generate KB docs from your existing codebase (the cold start killer) |
| `/brainstorm` | Explore unknowns when you don't know what you don't know |
| `/plan` | Research codebase + KB, design approach, define verification strategy |
| `/work` | Implement step-by-step with build verification after each step |
| `/review` | 8 parallel review perspectives (API design, performance, patterns, YAGNI, AI slop, etc.) |
| `/compound` | Extract learnings AND code patterns → feed back into KB |
| `/debug` | Parallel bug investigation → diagnosis doc |
| `/ship` | Plan → implement → review → fix → push in one shot (no human feedback between steps) |

Plus git workflow skills (stacked PRs, worktrees, rebase), quality skills (deslop, simplify), and analysis skills (tech design docs, adversarial critique).

### The Hooks

Skills are suggestions. Hooks are gates. They intercept agent lifecycle events and enforce the workflow:

- **session-compound:** On session end, analyze for gaps → post to Slack with pre-filled issue
- **pr-workflow:** Block `gh pr create` unless the PR skill was used first
- **tool-miss:** Detect "command not found" errors → suggest fix → update agent config
- **safety-gate:** Block production tools until safety docs are loaded from KB

### The Compound Loop

The core differentiator. Two feedback loops running simultaneously:

**Session-level (fast):** Every agent session is analyzed for improvement gaps — missing skills, missing tools, repeated failures, wrong information. Gaps post to Slack. Your team triages and fixes.

**PR-level (deep):** Every merged PR gets compound extraction. Learnings route to the KB (team-wide) or local files (project-specific). Next time `/plan` runs, it loads those learnings. The agent avoids the same mistakes.

This is what turns 60% into 90%. Not better prompts. Not a better model. *Better context, accumulated over time.*

### Automated Feedback Loops

Three GitHub Actions that close the loop without manual effort:

| Action | Trigger | What It Does |
|--------|---------|-------------|
| **Review-to-KB** | PR merges | Extracts corrections from review comments → proposes KB update PRs |
| **One-Shot Tracker** | Weekly (Monday) | Computes one-shot rate, top rejection reasons, suggests KB additions → posts to Slack |
| **Compound on Merge** | PR merges | Runs lightweight compound extraction → proposes learnings to KB |

These are in `templates/.github/workflows/`. Copy them into your repos.

---

## Thinking Is Not Dead

Agents write code. You make decisions. This system amplifies your judgment — it doesn't replace it. If you stop thinking, the agent produces code that looks right and is subtly wrong in ways you won't catch until production. Everything here exists to keep humans where they add the most value: judgment, context, taste.

---

## What This Is NOT

- **Not a replacement for engineers.** Engineers shift from writing features to building the system that lets everyone ship. That's harder, not easier.
- **Not a magic wand.** An empty KB means agents fall back to generic pre-training knowledge. The quality of your output is bounded by the quality of your documentation.
- **Not zero effort.** The first two weeks require your best engineers actively writing KB docs. If you skip this, nothing else works.
- **Not for greenfield without a KB.** An agent building a new system with no knowledge base, no patterns to follow, and no examples to reference will produce code that compiles but is hard to maintain, inconsistent, and full of decisions nobody agreed on. Agents are pattern-followers, not pattern-creators. The patterns need to exist first — either in your codebase or in your KB. Novel architecture, performance optimization, and complex distributed systems still need senior engineers driving.
- **Not vendor-locked.** Works with any MCP-compatible agent (Claude Code, Cursor, Codex, Copilot). GitHub-first, but adaptable to GitLab, Bitbucket, Azure DevOps.

---

## Quick Start

```bash
# 1. Clone
git clone <repo-url> agentic-eng && cd agentic-eng

# 2. Run the setup skill
/setup
```

The `/setup` skill walks you through deploying the KB server, installing skills, configuring your repos, seeding the knowledge base, and verifying everything works.

For manual setup, see [SETUP.md](SETUP.md).

### The Cycle

Once set up, every task follows this cycle:

```
/brainstorm    → Explore unknowns (skip for well-understood tasks)
/plan          → Research codebase + KB, design approach, define how to verify it works
/work          → Implement step-by-step, build-check each step
verify         → Run automated checks, ask human for what can't be automated
/review        → 8-perspective AI code review
push           → CI runs (your existing test suite), review bot runs
human review   → The one gate that is never automated
merge          → PR merges
/compound      → Extract learnings → KB → next cycle is better
```

---

## The Pipeline (Visual)

```
Anyone on the team has an idea
    ↓
/brainstorm — "I don't know what I don't know; help me figure it out"
    ↓
/plan — Research codebase, load KB context, design approach, DEFINE VERIFICATION
    ↓
/work — Agent implements step-by-step with build checks
    ↓
VERIFY — Agent runs automated checks, asks human for what it can't verify alone
    ↓
/review — 8-perspective AI code review pre-push
    ↓
CI — Your existing test suite, linter, type checker, build
    ↓
Review bot — Automated post-push check (CodeRabbit, Ellipsis, etc.)
    ↓
Human reviews — The one gate that stays. All code gets reviewed. No exceptions.
    ↓
Merge
    ↓
/compound — Extract learnings → knowledge base → next cycle is better
```

---

## Principles

### 1. Product & Design Ship Features. Engineering Builds the System.

The translation step — designer creates mockup, engineer interprets, engineer implements — is the bottleneck. With a well-seeded KB, the person who knows what they want tells the agent, and the agent builds it. Engineering's job becomes the infrastructure: the KB, the skills, the guardrails, the review process.

### 2. Anyone Can Ship.

No local dev environment required. For well-scoped changes, the agent is the engineer; the human is the requester.

### 3. Prove It Works.

Every plan defines how the feature will be verified — not just "tests pass," but "we can observe the thing actually does the thing."

### 4. Be Review-Constrained.

All code gets reviewed by a human. Everything else is automated. This is the correct bottleneck.

### 5. Deterministic + Agentic.

[How Stripe builds agents.](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2) Agents handle the creative work. Linters, formatters, CI, test runners run deterministically — never through the agent.

### 6. Bounded Iteration.

Agent gets one CI loop + one retry. If the same error fails twice, it stops and asks a human. Not infinite loops. The failure feeds the compound loop.

### 7. Security at Agent Scale.

1,000 PRs/week × 1% vulnerability rate = 10 new vulnerabilities weekly. Security is a default review perspective, not optional. Input validation is framework-enforced, not agent-remembered.

See [guides/01-philosophy.md](guides/01-philosophy.md) for the full reasoning behind each principle.

---

## Where This Falls Short (Honest Assessment)

- **Cold start is real.** The first 2 weeks require intentional effort from senior engineers writing KB docs. Most teams underinvest here.
- **Visual verification is a gap.** Agents can't reliably judge UI quality from screenshots (yet). Human-in-the-loop for visual stuff.
- **Novel architecture is hard to one-shot.** Agents are best at incremental work that follows existing patterns.
- **Review bandwidth is the true bottleneck.** If you automate everything except review, you need enough reviewers. See [guides/09-review-constrained.md](guides/09-review-constrained.md).
- **KB quality determines output quality.** Garbage in, garbage out. Stale docs produce confidently wrong code.

See [guides/12-proof.md](guides/12-proof.md) for real-world evidence from teams doing this at scale, including what doesn't work.

---

## Guides

| Guide | What It Covers |
|-------|---------------|
| [Philosophy](guides/01-philosophy.md) | The bet: product ships features, engineering builds the system |
| [Workflow](guides/02-workflow.md) | The brainstorm-plan-work-review-compound cycle |
| [Knowledge Base](guides/03-knowledge-base.md) | Setting up, seeding, partitioning, staleness detection |
| [Compound Loop](guides/04-compound-loop.md) | How the flywheel works (session-level + PR-level) |
| [Stacked PRs](guides/05-stacked-prs.md) | Why stacked PRs, how to use them |
| [Review Bots](guides/06-review-bots.md) | Setting up automated code review |
| [Observability](guides/07-observability.md) | Process OTEL + product observability (LangFuse, Datadog) |
| [Anyone Can Ship](guides/08-anyone-can-ship.md) | Codespaces + Slack for non-engineers |
| [Review-Constrained](guides/09-review-constrained.md) | Why review is THE bottleneck (and that's good) |
| [Team Rollout](guides/10-team-rollout.md) | Week-by-week rollout plan for teams of any size |
| [Measuring Success](guides/11-measuring-success.md) | Metrics: one-shot rate, compound velocity, adoption |
| [Proof](guides/12-proof.md) | Real-world evidence from teams in the wild |
| [FAQ](guides/13-faq.md) | Common questions, platform support, troubleshooting |
| [Cost & ROI](guides/14-cost-and-roi.md) | LLM costs, infrastructure costs, break-even analysis |
| [Sub-Agents](guides/15-sub-agents.md) | Parallelism, depth, and consensus with sub-agents |
| [Writing Agent Instructions](guides/16-writing-great-agent-instructions.md) | How to write a great CLAUDE.md (under 60 lines) |
| [People Process](guides/17-people-process.md) | Who owns what, team structure, the identity shift |
| [Trust CI](guides/18-trust-ci.md) | Why bulletproof CI is the foundation, 5 tools you'll build |

---

## Sources & Prior Art

Every core pattern in this architecture has prior art in the public domain. See [SOURCES.md](SOURCES.md) for the full list of research, blog posts, and case studies that inform this work.

## License

MIT
