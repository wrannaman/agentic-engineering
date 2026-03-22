# The Workflow: Brainstorm → Plan → Work → Review → Compound

This is the core cycle. Every feature, bug fix, and improvement goes through it.

## The Cycle

```
/brainstorm → /plan → /work → verify → /review → push → CI → review bot → human review → merge → /compound
```

**CI is part of the pipeline.** Every push triggers your existing CI suite (tests, linting, type checking, build). Nothing merges without CI green. This is your existing quality gate — the agentic workflow adds to it, not replaces it.

### 1. Brainstorm (`/brainstorm`)

**When to use:** You don't know what you don't know.

The brainstorm skill explores the problem space before committing to an approach. It asks clarifying questions, proposes 2-3 approaches with trade-offs, and produces a design document.

**Output:** `.plans/YYYY-MM-DD-<topic>-design.md`

### 2. Plan (`/plan`)

**When to use:** You know what you want to build, but not exactly how.

The plan skill researches the codebase, loads relevant patterns from the knowledge base, asks informed questions with recommendations, and produces a step-by-step implementation plan.

Key innovations:
- **Research-first:** Parallel codebase exploration before asking questions
- **Verification-aware:** Every plan defines how the feature will be verified (not just "tests pass")
- **PR-stack-aware:** Plans define how work will be split into stacked PRs

**Output:** `.plans/YYYY-MM-DD-<topic>-plan.md`

### 3. Work (`/work`)

**When to use:** You have an approved plan.

The work skill implements the plan step-by-step. One step at a time, with build verification after each step.

Key rules:
- Never skip verification
- Stop on failure (don't try to fix without guidance)
- Follow the plan exactly
- Run the primary validation from the plan after the final step

### 4. Verify

After implementation, the agent runs the verification strategy defined in the plan:
- **Automated checks:** curl endpoints, query databases, run CLI commands
- **Human-assisted:** "Paste a screenshot of X" or "Confirm Y happened in staging"

### 5. Review (`/review`)

**When to use:** After implementation and verification pass.

The review skill runs 8 parallel review passes:
1. API Design
2. Code Reuse
3. Performance
4. Idiomatic Code
5. Project Patterns
6. Clean Code
7. Simplicity / YAGNI
8. AI Slop Detection

### 6. CI (Your Existing Quality Gate)

After pushing, your existing CI pipeline runs: tests, linting, type checking, build. **This is not new.** The agentic workflow assumes you have CI and adds to it. If CI fails, the agent fixes and re-pushes (the `/pr-push` skill handles this automatically).

### 7. Review Bot (automated, post-push)

After pushing, an automated review bot (CodeRabbit, Ellipsis, etc.) runs on the PR. This catches style, convention, and obvious issues the skill might have missed.

### 8. Human Review (the gate)

A human engineer reviews the PR. This is the only gate that is never automated.

### 8. Compound (`/compound`)

**When to use:** After a feature is merged.

The compound skill extracts learnings from the completed work:
- What corrections were made during the session?
- What feedback came from code review?
- What patterns emerged?

Learnings are routed to the KB (for team-wide benefit) or local files (for project-specific patterns).

## Talk to Your Agent

An opinionated recommendation: use voice-to-text when working with agents. Tools like [Wispr Flow](https://wispr.flow) or Claude Code's native voice input cost ~$10/month and meaningfully improve output quality.

Why it works: when you speak, you give the agent more context than when you type. Nobody types three paragraphs of background on why a feature needs to work a certain way. But people naturally say it when talking. That additional context — the "why," the edge cases you're worried about, the thing you tried last week that didn't work — is exactly what the agent needs to produce better plans and better code.

Most people speak 3-4x faster than they type. That speed difference translates directly into richer prompts, which translates into better one-shot accuracy.

This isn't required. But the most productive engineers we've seen using agentic workflows are the ones talking to their agents, not typing at them.

## When to Skip Steps

- **Trivial fixes** (typo, config change): Skip brainstorm, but still plan → work → review
- **Emergency hotfixes:** Plan → work → review (skip brainstorm, compress review)
- **Exploration / spikes:** Brainstorm only (no plan/work needed)
- **Never skip review.** Never.
