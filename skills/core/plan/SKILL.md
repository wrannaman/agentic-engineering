---
name: plan
description: Pattern lookup, research, and design phase. NO coding allowed - only research and planning.
version: 1.0.0
---

## Overview

Write comprehensive implementation plans assuming the engineer has zero context for our codebase and questionable taste. Document everything they need to know: which files to touch for each task, code, testing, docs they might need to check, how to test it. Give them the whole plan as bite-sized tasks. DRY. YAGNI. Frequent commits.

Assume they are a skilled developer, but know almost nothing about our toolset or problem domain. Assume they don't know good test design very well.

Announce at start: "I'm using the plan skill to create the implementation plan."

Save plans to: <harness-dir(.claude|.codex)>/plans/YYYY-MM-DD-<feature-name>.md

(User preferences for plan location override this default)

---

**CRITICAL: This skill is research-first, then informed questions.** Do exploration before asking questions so you can present trade-offs with clear recommendations. Don't ask questions you can answer through research.

## Scope Check
If the spec covers multiple independent subsystems, it should have been broken into sub-project specs during brainstorming. If it wasn't, suggest breaking this into separate plans — one per subsystem. Each plan should produce working, testable software on its own.

## Configuration

**Learnings Directory:** `<git-root>/.llm/learnings/`

If this directory does not exist in the current project, skip the learnings step entirely. Do NOT read `~/.agentic-eng/config.toml` or any other config files to find an alternative path.

## Process

**ALL steps below are MANDATORY and SEQUENTIAL.** Do NOT skip steps. Do NOT proceed to the next step until the current step is fully complete. Each step produces a required output — if a step has no output, the subsequent steps cannot succeed.

### Step 1: Prime Context

Load all available context before exploring the codebase. KB and local learnings can be checked in parallel:

1. **KB** (if `kb` MCP is available): `list_kb_documents` → `read_kb_document_by_path` for relevant docs → `read_kb_document_by_keywords` for missing topics (retry up to 3×). Skip if unavailable.

2. **Local learnings** (if `<git-root>/.llm/learnings/` exists): grep for task keywords, read all matching files. Skip entirely if directory missing.

3. **User-provided docs** (if any URLs in the request): WebFetch each one, extract exact API signatures, gotchas, and patterns before proceeding.

Note what was found:
```
Loaded Context:
- [KB] doc-name - relevance
- [GOTCHA] filename.md - relevance
- [PATTERN] filename.md - relevance
- [EXTERNAL] url - key finding
```
**DO NOT ask questions yet.**

### Step 2: Research Codebase (PARALLEL EXPLORATION)

**Use the Task tool with `subagent_type=Explore` for thorough codebase exploration.**

Launch multiple parallel explorations in a single message:

1. **Existing types check** (thoroughness: "very thorough") — Before proposing ANY new type, verify it doesn't already exist. Search for similar types across ALL locations.

2. **Library built-in APIs check** (thoroughness: "very thorough") — For any external library, search for built-in utilities before creating helpers. Check if existing framework/library API already handles the new case. Before designing custom handling for a new code path, check whether the existing API already covers it.

3. **Similar implementations** (thoroughness: "very thorough") — Find code that does similar things. Look for patterns, approaches, and existing utilities that could be reused or extended.

4. **Testing patterns** (thoroughness: "medium") — Find tests for similar features. How are they structured? What mocking patterns and test utilities are used?

5. **Conventions & architecture** (thoroughness: "medium") — What conventions does this codebase follow for the relevant area? How is similar code organized?

6. **Dependencies & services** (thoroughness: "quick") — What existing services, repositories, or utilities exist that this feature might use?

**If KB MCP is available**, also retrieve relevant conventions and coding standards.

**Synthesize findings:** What can be reused? What patterns to follow? What test patterns to match? What dependencies are available?

### Step 3: Ask Informed Questions with Recommendations

**NOW you ask questions — but with context and recommendations.**

After all research, you can identify genuine decision points, explain trade-offs, and make explicit recommendations.

**Question format — ALWAYS include recommendation:**
```
## Questions (with Recommendations)

### 1. [Decision Topic]
**Context:** [What you found in patterns/codebase]

**Options:**
- **Option A:** [Description] — Pro: X, Con: Y
- **Option B:** [Description] — Pro: X, Con: Y

**My recommendation:** Option A, because [specific reason from research].
```

Ask about: architecture decisions with multiple valid approaches, scope clarifications, trade-offs between consistency vs. better approaches.

**DO NOT ask:** questions answerable through research, questions with obviously correct answers, or questions just to "validate assumptions."

### Step 4: Design Validation Methodology

**Every plan MUST have at least one automated validation the agent can run during implementation.**

Based on your testing patterns research (Step 2), determine the appropriate validation approach. Do not ask the user how to validate — propose a method with a recommendation.

Choose the lowest validation layer that proves correctness (unit test → integration test → CLI invocation → API call → database query → script output). Be specific: exact command, exact expected result.

If the obvious validation is hard, consider reshaping the feature for testability (extracting pure functions, adding dry-run mode, creating test fixtures).

For the full validation hierarchy, decision framework, and examples, see `references/validation-methodology.md`.

### Step 5: Additional Design Considerations

**If creating 4+ new files**, propose a directory structure following project conventions. Group related types, separate concerns, match existing patterns.

**If the feature involves AI/LLM calls**, design with separation of inputs from instructions, domain-level typed parameters, observability, and follow existing AI patterns in the codebase.

### Step 6: Define PR Stack Boundaries

**Every plan defines how work will be split into PRs.** Even single-PR features get a PR Stack section (one row) for consistency.

Consider splitting when: different concerns can be reviewed independently, a single PR would exceed ~500 lines, later work depends on earlier work, or high-risk changes should be isolated for rollback.

```markdown
## PR Stack

| PR | Branch | Steps | Description |
|----|--------|-------|-------------|
| 1  | feat/[name] | 1-N | [What this PR accomplishes] |
```

Do not hardcode a specific stack client — later workflow skills detect the active client.

### Step 7: Create Plan

**Write the implementation plan** — save to `<harness-directory(.claude|.agents|.codex)>/plans/YYYY-MM-DD-<topic>-plan.md`

**CRITICAL: Use the current working directory (cwd), NOT paths from config.toml** — especially important in worktrees.

Load the plan template from `references/plan-template.md` and fill it in based on your research and the user's answers.

### Step 8: Plan Review Loop

After writing the complete plan:

1. Dispatch a single plan-document-reviewer subagent (see plan-document-reviewer-prompt.md) with precisely crafted review context — never your session history. This keeps the reviewer focused on the plan, not your thought process.
   - Provide: path to the plan document, path to spec document

2. If Issues Found: fix the issues, re-dispatch reviewer for the whole plan
3. If Approved: proceed to Step 9

**Review loop guidance**:

- Same agent that wrote the plan fixes it (preserves context)
- If loop exceeds 3 iterations, surface to human for guidance
- Reviewers are advisory — explain disagreements if you believe feedback is incorrect

### Step 9: Present Plan for Approval

After the plan passes review:

1. **Present the plan** to the user
2. **Highlight key decisions** made based on their answers
3. **Note any reviewer recommendations** that were advisory (not blocking)
4. **Wait for approval** before proceeding

## Transition to Work Phase

When the plan is approved, recommend the appropriate implementation skill **in a new session**:

**If the plan involves UI with existing Figma designs:**
```
Plan approved. Start a new session (or /clear this one) and use
`/ui-from-figma .plans/YYYY-MM-DD-feature-name.md` to implement
from Figma designs. A fresh context gives the worker full budget for
implementation.
```

**Otherwise:**
```
Plan approved. Start a new session (or /clear this one) and use
`/work .plans/YYYY-MM-DD-feature-name.md` to begin implementation.
A fresh context gives the worker full budget for implementation.
```

Do not invoke any skill. For the full workflow overview (Plan → Work → Review → PR → Compound), see `references/workflow-overview.md`.
