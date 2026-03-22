---
name: ship
description: "End-to-end: plan → implement → review → fix → push in one shot. No human feedback between steps. Use when you trust the system and just want the thing done."
---

# Ship

> Plan it. Build it. Review it. Fix it. Push it. One command.

## Purpose

Runs the full cycle — plan, implement, review, fix, push — without stopping for human feedback between steps. For well-understood incremental tasks where you trust the system and just want it done.

This is `/plan` + `/work` + `/review` + `/pr-push` composed into a single uninterrupted flow. The agent makes all intermediate decisions. You review the final PR on GitHub.

## Usage

```
/ship "add a /health endpoint that returns 200 with {status: ok}"
/ship "fix the date formatting bug in the orders page — dates show UTC instead of local time"
/ship "add pagination to the /api/users endpoint using cursor-based pagination"
```

## When to Use

- **Well-scoped incremental tasks** — new endpoint, bug fix, small feature
- **Tasks that follow existing patterns** — the KB has examples of similar work
- **When you trust the compound loop** — the KB is well-seeded, the one-shot rate is high
- **When you want to review the PR, not babysit the process**

## When NOT to Use

- **Novel architecture** — use `/brainstorm` then `/plan` separately
- **Ambiguous requirements** — if you're not sure what you want, `/brainstorm` first
- **High-risk changes** — auth, payments, data migrations — use the manual cycle with human checkpoints
- **Your first week** — until the KB is seeded and you trust the system, use the manual cycle

## Process

### Step 1: Plan (Silent)

Run the `/plan` skill's process internally:
1. Load KB context and learnings
2. Research codebase with parallel sub-agents (existing types, similar implementations, test patterns)
3. Design implementation steps with verification strategy
4. Define PR stack boundaries (single PR for `/ship` unless the task clearly needs multiple)

**Do NOT ask the user questions.** Make your best judgment call on any decision points. If something is genuinely ambiguous (two equally valid approaches with different trade-offs), pick the simpler one.

Save the plan to `.plans/` as usual — it's useful for the compound loop later even if the user never reads it.

### Step 2: Implement (Silent)

Run the `/work` skill's process internally:
1. Create a branch (derive name from the task description)
2. Implement step by step with build verification after each step
3. Run the plan's verification strategy
4. If CI fails: one retry with fix. Same error twice → stop and report to user.

### Step 3: Review (Silent)

Run the `/review` skill's process internally:
1. Launch 8 parallel review sub-agents
2. Collect and deduplicate findings
3. Auto-fix all P1 and P2 issues (don't ask — just fix them)
4. Re-run verification after fixes
5. If P1s remain after fix attempt → stop and report to user

### Step 4: Push

Run the `/pr-push` skill's process internally:
1. Push the branch
2. Create a draft PR with generated title and body
3. Auto-fix any pre-commit failures
4. Link back to the plan file in the PR body

### Step 5: Report

```
## Shipped

**PR:** #<number> — <title>
**URL:** <url>
**Branch:** <branch>

**What was done:**
- [Brief summary of implementation]

**Review findings fixed:**
- [P1/P2 issues that were auto-fixed, if any]

**Verification:**
- [What was verified and the result]

**Plan:** .plans/YYYY-MM-DD-<topic>.md

Ready for your review on GitHub.
```

## How It Differs from the Manual Cycle

| Step | Manual Cycle | `/ship` |
|------|-------------|---------|
| Plan | User reviews and approves | Agent makes all decisions silently |
| Implement | User monitors step-by-step | Agent runs uninterrupted |
| Review | User sees findings, picks what to fix | Agent auto-fixes P1 + P2 |
| Push | User triggers | Agent pushes automatically |
| Human review | On GitHub (same) | On GitHub (same) |

The human gate is still there — it's just moved to GitHub PR review instead of being at every step.

## Stopping Conditions

The agent stops and reports to the user if:
- The same CI error fails twice (bounded iteration)
- P1 review findings can't be auto-fixed
- The task is genuinely ambiguous and the agent can't make a reasonable decision
- Build verification fails after implementation

When stopped, the agent reports what was done, what failed, and suggests next steps.

## Hard Rules

- Always create a draft PR (never publish)
- Always save the plan file (feeds compound loop)
- Always run review (don't skip even for "simple" changes)
- Always run verification from the plan
- Stop on repeated failures — don't loop infinitely
- The human reviews the final PR on GitHub — that gate never moves
