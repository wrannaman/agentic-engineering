# Agentic Engineering — The AX Stack

> AX (Agent Experience) is the new DX. UX was for users. DX was for developers. AX is for agents. This is the complete AX stack for engineering teams.

A knowledge base server, 20 agent skills, 5 enforcement hooks, a compound learning loop, automated feedback pipelines, and 18 guides. Everything a team needs to get AI agents one-shotting 90% of incremental features within 30 days.

Works with any coding agent: Claude Code, Cursor, Codex, GitHub Copilot. GitHub-first, adaptable to GitLab/Bitbucket/ADO.

**[Read the blog post →](https://blog.andrewpierno.com/agentic-engineering-the-ax-stack/)** for the full story, evidence, and predictions.

## Quick Start

```bash
git clone <repo-url> agentic-eng && cd agentic-eng

# Install skills for your coding agent
cd skills && ./install.sh

# Run interactive setup in your project repo
/setup
```

`/setup` detects your project (language, framework, build commands), connects to a KB server, writes a project-specific `AGENTS.md`, and verifies everything works. See [SETUP.md](SETUP.md) for manual setup.

## What's in the Box

```
agentic-eng/
├── apps/kb-server/        # MCP knowledge base server (Python, ~700 lines)
├── skills/                # 20 agent skills + 5 enforcement hooks
├── guides/                # 18 guides (philosophy → ROI)
├── integrations/          # Review bot, OTEL, LangFuse, Datadog configs
├── templates/             # AGENTS.md, .mcp.json, 4 GitHub Actions
└── examples/              # Seed KB docs, sample project with compound learnings
```

### KB Server

Minimal MCP + REST knowledge base. Official MCP Python SDK, FastAPI, SQLAlchemy (SQLite or Postgres — one env var). Multi-repo support. Full-text search (no embeddings, no vector DB — [Vercel proved simple beats complex](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals)).

[Details →](apps/kb-server/README.md)

### Skills

| Skill | Output |
|-------|--------|
| `/setup` | Configured project (AGENTS.md, .mcp.json, KB connection) |
| `/seed` | Draft KB docs auto-generated from your codebase |
| `/brainstorm` | Design doc with 2-3 approaches and trade-offs |
| `/plan` | Step-by-step implementation plan with verification strategy |
| `/work` | Code, committed and build-checked step by step |
| `/review` | Prioritized findings from 8 parallel review sub-agents |
| `/compound` | Learnings + code patterns extracted and routed to KB |
| `/debug` | Diagnosis doc from parallel bug investigation |
| `/ship` | Plan → implement → review → fix → push in one shot |

Plus: `stack-pr`, `pr-push`, `worktree`, `rebase-fix`, `git-cleanup`, `deslop`, `simplify`, `github-review`, `gh-summary`, `tdd`, `adversarial`.

[Full catalog →](skills/README.md)

### Hooks

Skills are suggestions. Hooks are gates.

| Hook | Trigger | What It Does |
|------|---------|-------------|
| session-compound | SessionEnd | Analyze for gaps → Slack |
| pr-workflow | PreToolUse | Block `gh pr create` unless PR skill used |
| tool-miss | PostToolUse | Detect command-not-found → suggest fix |
| safety-gate | PreToolUse | Block production tools until safety docs loaded |
| permission-analyzer | PermissionRequest | Evidence-based permission defaults |

### Compound Loop

Every merged PR feeds learnings back into the KB. Two speeds:

- **Fast (every session):** Hook detects gaps → posts to Slack with pre-filled issue
- **Deep (every PR):** Extracts corrections, review feedback, code patterns → routes to KB or local learnings

Three GitHub Actions automate this: [review-to-kb](templates/.github/workflows/review-to-kb.yml), [one-shot-tracker](templates/.github/workflows/one-shot-tracker.yml), [compound-on-merge](templates/.github/workflows/compound-on-merge.yml).

## The Cycle

```
/brainstorm → /plan → /work → verify → /review → CI → human review → merge → /compound
```

Or for well-scoped tasks: `/ship` (runs the whole thing uninterrupted).

## Principles

1. **Product & design ship features. Engineering builds the system.**
2. **Anyone can ship.** No local dev environment required.
3. **Prove it works.** Verification strategy in every plan.
4. **Be review-constrained.** All code reviewed by a human.
5. **Deterministic + agentic.** [Stripe's model.](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2) Agents write code. Linters, CI, formatters run deterministically.
6. **Bounded iteration.** One retry, then human.
7. **Security at agent scale.** Default review perspective, not optional.

[Full philosophy →](guides/01-philosophy.md)

## Evidence

- [Stripe](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2): 1,300+ agent PRs/week
- [Intercom](http://x.com/brian_scanlan/status/2033978300003987527?s=20): 100+ skills, non-engineers as top users
- [TELUS](https://jellyfish.co/blog/2025-ai-metrics-in-review/): 500K hours saved, 30% faster
- [Vercel](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals): curated docs 100% vs RAG 53%
- [57% of orgs](https://www.langchain.com/state-of-agent-engineering) have agents in production

[Full proof with case studies →](guides/12-proof.md)

## Where This Falls Short

- **Cold start is real.** First 2 weeks = senior engineers writing KB docs.
- **Visual verification needs judges.** LLMs can evaluate screenshots, but you need to set up LLM-as-judge pipelines (LangFuse or similar) to make this automated and reliable.
- **Novel architecture is hard to one-shot.** Agents follow patterns, not create them.
- **Review bandwidth is the bottleneck.** Automate everything else, invest in reviewers.

## Guides

| Guide | Topic |
|-------|-------|
| [Philosophy](guides/01-philosophy.md) | Why this works, 7 principles |
| [Workflow](guides/02-workflow.md) | The brainstorm → compound cycle |
| [Knowledge Base](guides/03-knowledge-base.md) | Setup, seeding, search-aware writing |
| [Compound Loop](guides/04-compound-loop.md) | The flywheel |
| [Stacked PRs](guides/05-stacked-prs.md) | For reviewers, not for CI |
| [Review Bots](guides/06-review-bots.md) | CodeRabbit, Ellipsis, etc. |
| [Observability](guides/07-observability.md) | Process OTEL + product observability |
| [Anyone Can Ship](guides/08-anyone-can-ship.md) | Codespaces + Slack |
| [Review-Constrained](guides/09-review-constrained.md) | The correct bottleneck |
| [Team Rollout](guides/10-team-rollout.md) | Week-by-week plan |
| [Measuring Success](guides/11-measuring-success.md) | One-shot rate, compound velocity |
| [Proof](guides/12-proof.md) | Stripe, Intercom, TELUS, Vercel, SaaStr |
| [FAQ](guides/13-faq.md) | Platform support, troubleshooting |
| [Cost & ROI](guides/14-cost-and-roi.md) | LLM costs, break-even |
| [Sub-Agents](guides/15-sub-agents.md) | Parallelism, depth, consensus |
| [Agent Instructions](guides/16-writing-great-agent-instructions.md) | Writing a great AGENTS.md |
| [People Process](guides/17-people-process.md) | Ownership, team structure, identity shift |
| [Trust CI](guides/18-trust-ci.md) | Bulletproof CI, 5 tools you'll build |

## Sources

Every pattern has public domain prior art. See [SOURCES.md](SOURCES.md).

## License

MIT
