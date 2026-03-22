---
keywords: pull request, pr, review, conventions, git, workflow
last_reviewed: 2026-03-18
owner: engineering
---

# PR Conventions

> Example KB seed document. Customize for your team.

## PR Size

- Aim for <500 lines changed per PR
- If larger, split into stacked PRs
- Each PR should be independently reviewable

## PR Title

Use conventional commit format:

```
feat: add user profile page
fix: correct date formatting in orders
refactor: extract shared auth middleware
docs: update API documentation
```

## PR Description

Include:
1. **What** — Brief description of the change
2. **Why** — Motivation (link to issue/ticket if applicable)
3. **How** — Key implementation decisions (especially non-obvious ones)
4. **Testing** — How the change was verified

## Review Process

1. Author creates draft PR
2. Review bot runs (automated check)
3. Author marks as "ready for review"
4. Reviewer assigned (round-robin or by expertise)
5. Reviewer provides feedback
6. Author addresses feedback
7. Reviewer approves
8. Author merges (squash for single-commit PRs, merge for stacks)

## Review Expectations

- Review within 4 hours during business hours
- Focus on correctness, design, and maintainability
- Don't bikeshed style (that's what linters are for)
- Approve with optional suggestions when the code is good enough
