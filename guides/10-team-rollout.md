# Team Rollout

How to roll this out to a team of N engineers.

## Week 1: Foundation (1-2 people)

- Deploy KB server
- Install skills on 1-2 machines
- Seed KB with existing coding standards and architecture docs
- Run 2-3 features through the full cycle to validate

## Week 2: Early Adopters (3-5 people)

- Expand to willing early adopters
- Set up the session-compound hook (gap detection)
- Run `/compound` after each feature to build learnings
- Start measuring one-shot rate

## Week 3-4: Team-Wide

- Install skills for all engineers
- Set up the review bot
- Enable hooks (PR workflow, tool-miss detection)
- Begin non-engineer experiments (1-2 PMs or designers try the workflow)

## Month 2+: Scale

- Tune skills based on compound learnings
- Expand KB partitions
- Set up auto-compound GitHub Action
- Roll out Codespaces + Slack for non-engineers
- Track metrics weekly

## Common Resistance

| Objection | Response |
|-----------|----------|
| "AI code isn't trustworthy" | That's why every PR gets human review. Same bar as any other code. |
| "This will replace engineers" | It shifts engineers to higher-leverage work: architecture, guardrails, review. |
| "Our codebase is too complex" | Start with simple features. The KB compounds. Complexity becomes context. |
| "Non-engineers will break things" | CI + review bot + human review = three gates. Nothing merges without review. |
