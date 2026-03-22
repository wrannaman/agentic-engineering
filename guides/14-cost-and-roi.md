# Cost and ROI

Rough numbers for budgeting. Your mileage will vary.

## LLM Costs

The biggest variable cost is LLM usage. Agents make many calls per task (planning, implementation, review, compound).

| Usage Level | Cost per Engineer/Month | Description |
|-------------|------------------------|-------------|
| Light | $30-80 | A few features/week, mostly small tasks |
| Moderate | $80-200 | Daily agent usage, mix of small and medium tasks |
| Heavy | $200-500 | Multiple agents running concurrently, complex tasks |

**Non-engineers** (designers, PMs) using the system typically fall in the "light" category — they're doing smaller, well-scoped changes.

These numbers are based on Claude/GPT-class model pricing as of early 2026. Costs are trending down. By the time you read this, they may be significantly lower.

## Infrastructure Costs

| Component | Self-Hosted | Cloud |
|-----------|------------|-------|
| KB Server (SQLite) | Free (runs on any VM) | $5-15/mo (Railway, Fly.io) |
| KB Server (Postgres) | Cost of your Postgres instance | $15-30/mo (managed DB) |
| Review Bot (CodeRabbit) | N/A | Free (OSS) or $15/seat/mo |
| Observability (LangFuse) | Free (self-hosted) | $0-50/mo depending on volume |

**Total infrastructure: $5-50/month** for most teams. This is negligible.

## Human Costs

The often-overlooked cost: someone needs to maintain this system.

| Role | Time Investment | Who |
|------|----------------|-----|
| Initial setup | 2-4 hours (one time) | Senior engineer |
| KB seeding | 2-4 hours (one time) | Tech leads |
| Ongoing KB maintenance | 1-2 hours/week | Rotating among team |
| Skill tuning | 1-2 hours/week | Platform/DevEx engineer |
| Compound loop triage | 30 min/week | Anyone (review compound PRs) |

For a team of 20+ engineers, this is easily a part-time or full-time DevEx role. For smaller teams, it's a shared responsibility.

## ROI Model

The value comes from three places:

### 1. Developer Velocity

If agents handle 60-90% of incremental feature work, engineers focus on architecture, review, and the hard 10-20%.

**Conservative estimate:** 20-30% increase in feature throughput per engineer. For a team of 20 engineers at $150k average salary, that's $600k-900k in effective capacity per year.

### 2. Non-Engineer Shipping

Designers and PMs creating their own PRs for small changes eliminates the "ticket → engineer → PR → review" latency.

**Typical saving:** 2-5 days of latency per small change. If your team has 10+ small changes per sprint that could be self-served, that's significant.

### 3. Knowledge Compound Effect

The KB reduces onboarding time, reduces repeated mistakes, and makes the whole org smarter over time. This is hard to quantify but very real.

**Typical sign:** New hires become productive faster. The same categories of review feedback stop recurring.

## Break-Even

For most teams, the math works if agents save each engineer **2-3 hours per week**. At moderate LLM costs ($100-200/engineer/month), you break even at roughly 1 hour of saved time per week — easily achievable.

## How to Track

See [guides/11-measuring-success.md](11-measuring-success.md) for metrics. The ones that matter for ROI:

- **One-shot rate** — directly measures agent effectiveness
- **Time-to-merge** — measures latency reduction
- **Non-engineer PR count** — measures self-service adoption
- **Review feedback volume per PR** — should decrease as KB compounds
