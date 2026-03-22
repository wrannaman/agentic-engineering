# Measuring Success

How to know this is working.

## North Star: One-Shot Rate

The percentage of tasks where the agent's first implementation passes human review without changes.

```
one_shot_rate = PRs_merged_without_review_changes / total_PRs_created_by_agents
```

Target trajectory: 60% → 80% → 90% over 3-6 months.

## Supporting Metrics

| Metric | What It Measures | How to Collect |
|--------|-----------------|---------------|
| **KB growth** | Documents added/month | Count docs in KB partitions |
| **Compound velocity** | Learnings extracted/sprint | Count files in `.llm/learnings/` |
| **Session gap rate** | % sessions surfacing a gap | Session-compound hook telemetry |
| **Repeat-mistake rate** | Same gotcha hit twice | Compare learnings to review feedback |
| **Non-engineer PR rate** | % PRs from non-engineers | GitHub PR author analysis |
| **Review turnaround** | Time from PR creation to merge | GitHub PR metrics |
| **Skill usage** | Which skills are used most | Process OTEL telemetry |

## What "Good" Looks Like

**Month 1:** One-shot rate ~60%. KB has 20-50 seed docs. Team is using the cycle.

**Month 3:** One-shot rate ~75%. Compound loop has added 50+ learnings. First non-engineer PRs merging.

**Month 6:** One-shot rate ~85%. Review bot catches most mechanical issues. Human reviewers focus on judgment calls. Non-engineers shipping incremental features regularly.
