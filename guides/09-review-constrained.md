# Be Review-Constrained

Every PR gets human review. No exceptions. This is by design.

## Why Review Is the Right Bottleneck

Everything else can be automated:
- Writing code → agent
- Running tests → CI
- Checking style → linter + review bot
- Creating PRs → agent
- Extracting learnings → compound loop

Review is where humans add the most value:
- **Judgment** — "This technically works but it's the wrong approach"
- **Context** — "This will conflict with what team X is doing"
- **Taste** — "This API surface is confusing for consumers"

## The Review Funnel

```
Agent creates PR
    ↓
CI runs (tests, lint, build — your existing pipeline)
    ↓
Review bot (automated, instant)
    catches: style, conventions, obvious bugs
    ↓
Agent fixes CI failures + bot feedback (/github-review)
    ↓
Human reviewer (the real gate)
    catches: design, correctness, judgment
    ↓
Agent fixes human feedback (/github-review)
    ↓
Human re-reviews → CI green → Merge
    ↓
Compound extracts learnings → KB
(so this class of issue is caught earlier next time)
```

## Scaling Review

If you're bottlenecked on review:

1. **Invest in the compound loop.** Every review that catches something should feed a learning back into the KB. Next time, the agent avoids the issue entirely.
2. **Improve the review skill.** If the `/review` skill consistently misses a category of issues, tune it.
3. **Add more reviewers.** Not more writers — more reviewers. Writers are infinite (agents). Reviewers are the scarce resource.
4. **Use stacked PRs.** Smaller PRs review faster. Three 500-line PRs review faster than one 1500-line PR.
