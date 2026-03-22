# Stack PR

> Create stacked PRs from a plan's PR Stack table.

## Purpose

Large features split into small, reviewable PRs that build on each other. This skill creates the stack: branches, draft PRs, and dependency links. Uses plain `git` + `gh` CLI — no special tooling required.

## Usage

```
/stack-pr                         # Create stack from current plan
/stack-pr .plans/2026-03-18-...   # Create stack from specific plan
```

## Process

### Step 1: Read the PR Stack

From the plan:
```markdown
| PR | Branch | Steps | Description |
|----|--------|-------|-------------|
| 1  | feat/add-model | 1-2 | User entity and repository |
| 2  | feat/add-api | 3-4 | API endpoints |
| 3  | feat/add-tests | 5-6 | Integration tests |
```

### Step 2: Create Branches

```
main ← feat/add-model ← feat/add-api ← feat/add-tests
```

Each branch is based on the previous one.

### Step 3: Push and Create Draft PRs

For each branch:
```bash
git push -u origin <branch>
gh pr create --base <parent-branch> --head <branch> --draft \
  --title "<conventional-commit-title>" \
  --body "PR N/M in stack. Depends on #<parent-PR>"
```

### Step 4: Report

```
Stack created:
  PR #101: feat/add-model → main (draft)
  PR #102: feat/add-api → feat/add-model (draft)
  PR #103: feat/add-tests → feat/add-api (draft)

Merge order: #101 → #102 → #103
```

## After a PR Merges

When PR 1 merges, update PR 2's base:
```bash
gh pr edit <PR2> --base main
git checkout feat/add-api && git rebase main && git push --force-with-lease
```

Use `/rebase-fix` if conflicts arise.

## Hard Rules

- All PRs are **drafts** — never auto-publish
- Include stack position in title or body ("PR 2/3")
- Link dependent PRs in description
- Merge in order
