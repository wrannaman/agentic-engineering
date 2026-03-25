# The People Process

The skills and the KB server are the easy part. The hard part is the people.

This guide covers who owns what, how to structure teams around agentic engineering, and how to avoid the failure modes that kill adoption.

## Who Owns What

### The Knowledge Base

Someone must own each partition. If nobody owns it, it rots.

**Option A: Pod-level ownership (recommended for most teams)**

Each pod/squad owns the partition that covers their domain. The frontend pod owns `frontend/`. The backend pod owns `backend/`. They write the docs, review KB PRs for their partition, and are accountable for quality.

**Option B: Top-down ownership (for smaller teams or early adoption)**

A senior engineer or tech lead owns the entire KB. They seed the initial docs, review every KB PR, and are the arbiter of quality. This works well for the first 30 days. It doesn't scale past ~50 docs or ~10 engineers.

**Option C: Hybrid (what most teams converge on)**

A senior engineer or DevEx role owns the *system* — the KB server, the skills, the hooks, the compound loop. Pods own their *partitions*. The system owner ensures the compound loop is running and the one-shot rate is trending up. Pod owners ensure their docs are accurate and current.

| Role | Owns | Accountable For |
|------|------|----------------|
| System owner (1 person) | KB server, skills, hooks, compound loop | One-shot rate trending up, system health |
| Partition owner (per pod) | Their partition's docs | Doc accuracy, staleness, compound PR review |
| Every engineer | Their own compound output | Running `/compound` after features, reviewing KB PRs |

### The One-Shot Metric

Someone must own the number. If nobody tracks it, nobody improves it.

**The metric:** PRs created through the plan-implement-review cycle that merge with zero additional human corrections. Not "zero review comments" — review comments that are informational or approving don't count. The metric is: **did the human reviewer request code changes?**

```
one_shot_rate = PRs_merged_without_changes_requested / total_agent_PRs
```

The system owner tracks this weekly. The One-Shot Tracker GitHub Action automates collection. The weekly Slack report shows the number, the trend, and the top rejection reasons with suggested KB additions.

If the number isn't going up, either the KB is stale or the compound loop isn't running. Both are fixable.

### The Compound Loop

The compound loop tends toward two failure modes:

**Failure mode 1: Nobody runs it.** Engineers finish a feature and move on. No `/compound`, no learnings extracted, no improvement. Fix: the auto-compound GitHub Action catches this. Every merged PR gets lightweight extraction automatically.

**Failure mode 2: It bloats.** The compound loop adds but never edits. Over time, the KB accumulates redundant, overlapping, or contradictory docs. The agent finds three docs about error handling, each saying something slightly different, and picks the wrong one.

**Fix: Tell the system to favor editing over adding.** This is a bias you must actively counteract. The compound skill should:
- Search the KB for existing docs on the topic BEFORE creating a new one
- If a related doc exists, propose an EDIT to that doc (add a section, update a paragraph)
- Only create a new doc if nothing related exists
- Favor surgical precision over comprehensive coverage

Think of it like a wiki, not a blog. A wiki has one page about error handling that gets refined over time. A blog has 12 posts about error handling that nobody can navigate.

The partition owner should review compound PRs with this lens: "Is this a new doc, or should this be an edit to an existing doc?"

## Where Do Plans Live?

Plans (`.plans/YYYY-MM-DD-feature.md`) and design docs are working artifacts. They have a short useful life.

**During development:** Plans live in `.claude/plans/` (or `.codex/plans/`, etc.), which is gitignored. They're local to the developer's session. The agent reads them. The human reads them. They don't need to be committed.

**After merge:** The plan's value has been consumed. The code exists. The learnings have been extracted by `/compound`. The plan itself is ephemeral.

**Exception: Design specs and ADRs.** These are different from plans. They document *why* a decision was made, not *how* to implement it. These should be committed to a `decisions/` directory and kept permanently. They're reference material, not instructions.

**The heuristic:** If someone would usefully read this document 6 months from now, commit it. If it's only useful during implementation, don't.

| Artifact | Commit? | Where |
|----------|---------|-------|
| Plan (`.plans/*.md`) | No | Local, gitignored |
| Design doc (from `/brainstorm`) | Maybe | If it captures decisions, commit to `decisions/` |
| Design spec (from `/spec`) | Yes | `decisions/YYYY-MM-DD-*.md` |
| KB docs | Yes (to KB docs repo) | Reviewed via PR |
| Learnings (`.llm/learnings/`) | Yes (to project repo) | Committed alongside code |

## Standardizing the Harness

**Don't mandate a single tool.** Mandating "everyone must use Claude Code" or "everyone must use Cursor" causes friction and resentment. Engineers have preferences. Those preferences don't affect the system.

**Do standardize the interface.** Everyone uses the same:
- KB server (one instance, shared)
- Skills (same SKILL.md files, installed for their agent of choice)
- CLAUDE.md / AGENTS.md (same instructions, adapted per agent format)
- GitHub workflow (same PR process, same review expectations)

The skills are markdown. They work with Claude Code, Cursor, Codex, Copilot — anything that supports instructions or skills. The KB server is MCP, which is agent-agnostic. The workflow is GitHub (or GitLab, or ADO).

An engineer using Cursor with the same KB and same skills produces the same quality output as an engineer using Claude Code. The system doesn't care which tool is underneath.

## Centralized Telemetry

As adoption scales, you want visibility into how agents are being used across the org. Not surveillance — operational awareness.

**What to collect (via OTEL hooks):**
- Session count and duration per engineer
- Skills activated (which skills are used, which are dead)
- Gap classifications from session-compound (missing_skill, missing_tool, etc.)
- One-shot rate per pod, per partition

**What NOT to collect:**
- Raw prompts or conversation content (privacy)
- Individual performance metrics (this kills adoption)

**Where it goes:** Honeycomb, Datadog, or any OTEL-compatible backend. The system owner watches the dashboards. If the frontend pod's one-shot rate is dropping, something changed in their codebase that the KB doesn't cover. If a skill is never used, it might need a better description or trigger.

This is the same telemetry pattern Intercom uses (14 agent lifecycle events flowing to Honeycomb, privacy-first).

## Minimizing Friction

The fastest way to kill adoption is to make it feel like overhead.

**Do:**
- Let engineers choose their own agent (Claude Code, Cursor, etc.)
- Make the cycle optional for trivial changes (typo fixes don't need `/plan`)
- Let the compound loop run automatically (GitHub Action) so engineers don't have to remember
- Celebrate when the one-shot rate goes up (it's a team win)

**Don't:**
- Mandate that every commit goes through the full cycle
- Require engineers to manually run `/compound` after every feature (automate it)
- Track individual engineer one-shot rates (track team/pod rates instead)
- Add process without removing process (if agents handle reviews pre-push, maybe you can relax human review for P3 issues)

**The mindset:** This is a tool that makes engineers' lives easier, not a process that makes their lives harder. If an engineer says "the plan skill is slower than just writing the code myself," either the KB is bad (fix it) or the task is too simple for the full cycle (let them skip brainstorm/plan for trivial changes).

## The Identity Shift

The hardest part isn't technical. It's psychological.

Engineers who've written code for 15 years are being told "your new job is reviewing code and writing documentation." That feels like a demotion. It's not — it's a promotion to a higher-leverage role. But it doesn't feel that way on day 1.

**How to manage this:**

1. **Frame it as leverage, not replacement.** "You're not writing less code. You're shipping more features. The agent is your 10x multiplier, but it needs your expertise to work."

2. **Start with enthusiasts.** Don't mandate org-wide adoption on day 1. Find the 2-3 engineers who are excited about this. Let them prove it works. Let others see the results.

3. **Make the KB feel like ownership, not documentation duty.** "You're the expert on this part of the codebase. The KB is how you scale your expertise to every agent and every engineer."

4. **Show the numbers.** When the one-shot rate goes from 60% to 85%, that's concrete. When review feedback volume drops 40%, that's visible. Numbers make the abstract real.

5. **Acknowledge the weirdness.** "Yes, it's strange that the PM is creating PRs now. Yes, it's strange that your job is reviewing code you didn't write. This is new for everyone."
