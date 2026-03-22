# The Compound Loop: How the Flywheel Works

The compound loop is the core differentiator of this architecture. It's what makes each cycle better than the last.

## The Problem

AI agents make the same categories of mistakes repeatedly. Each developer discovers the same gotchas independently. Knowledge doesn't compound. One-shot accuracy plateaus.

## The Solution

A structured extraction process that turns every completed feature into reusable knowledge.

## Two Loops, Two Speeds

### Loop 1: Session-Level (Fast)

Every agent session generates signal. The `session-compound` hook fires on SessionEnd:

```
Session ends
    → Hook analyzes transcript with lightweight LLM
    → Classifies gaps:
        missing_skill   — agent couldn't do something it should
        missing_tool    — command not found, missing MCP tool
        repeated_failure — same error hit multiple times
        wrong_info      — KB had stale/incorrect information
    → Posts to Slack with pre-filled GitHub issue URL
    → Team triages: fix skill, update KB, add hook
```

This catches problems fast. Every session generates signal, not just merged PRs.

### Loop 2: PR-Level (Deep)

After a feature merges, the `/compound` skill (or auto-compound GitHub Action) runs:

```
PR merges
    → Extract user corrections from session history
    → Extract review feedback from PR comments
    → Extract structural changes (renames, refactors)
    → Synthesize into learnings
    → Route each learning:
        Reusable knowledge    → PR to KB docs repo (auto-indexed on merge)
        Project-specific      → .llm/learnings/ in project repo
        Skill gaps            → Issue filed for skill improvement
        Recurring mistakes    → Hook creation
```

This catches patterns that only emerge from completed features.

## How It Feeds Forward

1. `/compound` creates a learning file (e.g., `.llm/learnings/gotchas/redis-ttl-mismatch.md`)
2. Next time `/plan` runs, it scans `.llm/learnings/` and loads relevant patterns
3. The plan accounts for known gotchas and patterns
4. The agent produces better code on the first try
5. One-shot accuracy improves measurably

## Measuring Success

| Metric | What It Measures | Target Trend |
|--------|-----------------|-------------|
| **One-shot rate** | % of tasks that pass review without changes | Increasing |
| **Compound velocity** | Learnings extracted per sprint | Steady (shows the loop is running) |
| **KB growth** | Documents added per month | Increasing, then plateau |
| **Repeat-mistake rate** | Same gotcha hit twice | Decreasing |
| **Session gap rate** | % of sessions that surface a gap | Decreasing |
| **Non-engineer PR rate** | % of merged PRs from non-engineers | Increasing |

## Three Compound Modes

1. **Session compound** — After completing a feature (most common)
2. **Code compound** — Extract patterns from existing code (useful for onboarding)
3. **Past-PR compound** — Batch-analyze historical merged PRs (useful for bootstrapping)

## The Auto-Compound GitHub Action

For teams that want the loop to run without manual intervention:

```yaml
# .github/workflows/compound-on-merge.yml
on:
  pull_request:
    types: [closed]
    branches: [main]
```

The action extracts learnings and creates a follow-up PR to the KB docs repo. A human reviews before merge — bad learnings poisoning the KB would be worse than no learnings.
