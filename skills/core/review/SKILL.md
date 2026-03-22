---
name: review
description: Multi-perspective code review with 8 parallel passes. Language-agnostic — adapts to whatever your codebase uses via KB.
version: 1.3.2
---

# Review Skill

You are entering the **review phase**. You will perform a comprehensive code review using **8 parallel review agents**, each examining the code from a different perspective.

## Configuration

**Learnings Directory Lookup:**
1. First, check for project-local learnings at `<git-root>/.llm/learnings/`
2. If not found, fall back to `[paths.learnings_directory]` from `~/.agentic-eng/config.toml`

This allows each project to have its own learnings while maintaining backwards compatibility.

## Process

### Step 1: Detect Stack Structure

Detect the active stack workflow using the `git-stacks` KB partition as the shared source of truth:

1. `list_kb_documents` for partition `git-stacks`
2. `read_kb_document_by_path` for `/index.md`
3. Run the dedicated-client checks from `git-stacks/index.md`
   - If a dedicated client is detected, record `STACK_CLIENT` accordingly
   - If no dedicated client is detected, inspect the current branch, the plan's `PR Stack` section, and GitHub base refs to determine whether this repo is using a native git stack
   - If you confirm a native stack, record `STACK_CLIENT=native-git`
   - If you cannot confirm a stack, fall back to standard single-PR review

4. **Load the matching KB client doc before running any stack-specific command:**
   - `charcoal` → `read_kb_document_by_path` for `/charcoal.md`
   - `git-town` → `read_kb_document_by_path` for `/git-town.md`
   - `native-git` → `read_kb_document_by_path` for `/native-git.md`
   - Use the client doc as the source of truth for stack-specific commands. Never assume `gt` exists unless you detected it.

**If a stack is detected:**
- Parse the stack to get list of branches and their parent relationships
- Each branch in the stack is a separate PR to review

### Step 1.5: Choose Review Scope (Stacked PRs Only)

**If in a stack with multiple branches, ask the user:**

```
## Stack Detected

Your stack has N PRs:
| PR | Branch | Description |
|----|--------|-------------|
| 1  | feat/part-1 | [from commits] |
| 2  | feat/part-2 | [from commits] |
| 3  | feat/part-3 | [from commits] |

How would you like to review?
1. Review all PRs (recommended) - Reviews each PR against its parent
2. Review current PR only - Reviews only the current branch
3. Review entire stack as one diff - Reviews all changes from main to HEAD
```

**Recommendation:** Option 1 (review all PRs) because it matches how GitHub will show the changes and keeps reviews focused.

### Step 2: Identify Changes (Per-PR)

**For each PR to review, determine its diff:**

**Standard (non-stack) or single PR:**
```bash
# Get current branch
CURRENT=$(git branch --show-current)

# Find the parent branch: first branch ref in git log that isn't current branch
PARENT=$(git log --pretty=format:'%D' | grep -v '^$' | grep -v "^HEAD -> $CURRENT$" | head -1 | tr ',' '\n' | sed 's/^ *//' | grep -v "HEAD" | grep -v "origin/HEAD" | head -1)

# Diff against the parent branch
git diff $PARENT
```

**Stacked PRs (review each PR separately):**
```bash
# Use the detected stack workflow guidance from KB to enumerate
# each branch and its parent before diffing.
#
# Native git example:
# PR 1: git diff main..feat/part-1
# PR 2: git diff feat/part-1..feat/part-2
# PR 3: git diff feat/part-2..feat/part-3
```

### Step 2.5: Get the Full Diff

Run the git diff and capture the output. You'll pass this diff to each review agent.

**For stacked PRs:** Collect diffs for each PR separately. You'll review them one at a time or in parallel batches.

### Step 3: Launch 8 Parallel Review Agents

**CRITICAL: Launch all 8 Task tool calls in a SINGLE message to run them in parallel.**

Use `subagent_type=general-purpose` for each agent. Each agent receives:
1. The git diff output
2. Perspective-specific KB paths (listed below)
3. Instructions to return findings in the standard format

#### KB-Driven Review Context

Each review agent should load relevant KB docs for its perspective. The agent determines the right partition and docs dynamically based on the file types in the diff:

1. **Detect language** from the diff (file extensions: `.ts`/`.tsx`, `.py`, `.cs`, `.go`, `.java`, etc.)
2. **Determine partition** from the project's `CLAUDE.md` or `AGENTS.md` (which specifies the KB partition for this repo)
3. **Search KB** using `search_documents` with keywords relevant to the perspective:

| Reviewer | KB Search Keywords |
|----------|-------------------|
| Security | `security, validation, auth, injection, sanitization` |
| API Design | `api, endpoints, rest, dto, validation, response` |
| Code Reuse | `code reuse, shared, utilities, duplicate, abstraction` |
| Performance | `performance, optimization, memory, async, queries` |
| Idiomatic Code | `guidelines, conventions, idiom, style, best practices` |
| Project Patterns | `patterns, structure, architecture, conventions` |
| Clean Code | `clean code, readability, naming, responsibility` |
| Simplicity | `simplicity, yagni, over-engineering, abstraction` |
| AI Slop | `ai slop, verbose, unnecessary, boilerplate` |

If the KB is available, each agent loads the most relevant docs for its perspective. If no KB is configured, the agent reviews based on general best practices.

#### Agent Prompt Template

For each agent, use this prompt structure:

```
You are a code reviewer focused on [PERSPECTIVE].

## Step 1: Gather Context from KB (if available)

If KB MCP tools are available:
1. Call `list_documents` with the partition from this project's CLAUDE.md
2. Call `search_documents` with keywords: [PERSPECTIVE_KEYWORDS]
3. Read the most relevant docs for your review perspective

If no KB is available, review based on general best practices for the language.

## Step 2: Review the Diff

Review the git diff from your perspective. For each finding, report:
- Severity (P1/P2/P3)
- File and line
- Issue description
- Recommended fix

## Diff to Review
[INSERT GIT DIFF]
```

### Step 4: Aggregate Results

After all 8 agents return, aggregate their findings:

1. **Collect all findings** from each agent
2. **Deduplicate** - If multiple agents flag the same issue, keep the most detailed explanation
3. **Sort by severity** - P1 first, then P2, then P3
4. **Group by file** - Makes it easier to fix

---

## Output Format

For each finding:

```
[P1/P2/P3] file:line - Issue description
  -> Fix: Recommended solution with code example
```

**Severity Levels:**
- **P1**: Must fix - Breaks functionality, security issue, or violates critical pattern
- **P2**: Should fix - Best practice violation, maintainability concern
- **P3**: Consider - Style preference, minor improvement

---

## Final Report

**For stacked PRs, report per-PR:**

```
## Stack Review Summary

### PR 1: feat/part-1 (Add User model)

#### Findings by Category
- **API Design:** No issues found
- **Code Reuse:** No issues found
- **Performance:** [P2] UserRepository.cs:45 - Consider async enumeration
- **Project Patterns:** All patterns followed correctly

**PR 1 Verdict:** Ready to merge

---

### PR 2: feat/part-2 (Add User API)

#### Findings by Category
- **API Design:** [P1] UserController.cs:23 - Missing validation
- **Code Reuse:** [P2] UserService.cs:88 - Duplicate helper exists in shared module
- **Clean Code:** [P3] Consider renaming method

**PR 2 Verdict:** Needs fixes (1 P1)

---

### PR 3: feat/part-3 (Add tests)
...

---

## Stack Summary

| PR | Branch | P1 | P2 | P3 | Verdict |
|----|--------|----|----|----|---------|
| 1  | feat/part-1 | 0 | 1 | 0 | Ready |
| 2  | feat/part-2 | 1 | 0 | 1 | Needs fixes |
| 3  | feat/part-3 | 0 | 0 | 0 | Ready |

**Total Issues:** X (P1: Y, P2: Z, P3: W)

**Must Fix Before Merge:**
1. [P1 issue in PR 2]
```

**For single PR (standard report):**

```
## Code Review Summary

### 1. API Design
[Findings or "No issues found"]

### 2. Code Reuse
[Findings or "No issues found"]

### 3. Performance
[Findings or "No issues found"]

### 4. Idiomatic Code
[Findings or "No issues found"]

### 5. Project Patterns
[Findings or "All patterns followed correctly"]

### 6. Clean Code
[Findings or "No issues found"]

### 7. Simplicity/YAGNI
[Findings or "Code is appropriately simple"]

### 8. AI Slop
[Findings or "No AI artifacts detected"]

---

## Summary

**Total Issues:** X (P1: Y, P2: Z, P3: W)

**Must Fix Before Merge:**
1. [P1 issue 1]
2. [P1 issue 2]

**Recommended Improvements:**
1. [P2/P3 issues]

---

**Verdict:** [Ready to merge / Needs fixes / Major rework needed]
```

## When to Use

- After completing a feature with `/work`
- Before creating a PR with `/pr-push`
- When reviewing someone else's code
- After refactoring

## Integration with GitHub Review

**After PR is created and receives human review comments:**

Use `/github-review` to:
1. Pull unresolved review comments from the PR
2. Create a plan to address them
3. Execute fixes

The github-review skill will create a **review fix plan** that links back to the original implementation plan. This keeps all related work connected.

## Full Workflow

```
/plan → creates plan file
       ↓
/work .plans/plan.md → implements
       ↓
/review → AI code review (pre-PR)
       ↓
/pr-push → creates draft PR (pre-commit hooks verify build)
       ↓
[Human reviews PR on GitHub]
       ↓
/github-review → addresses review comments
       ↓
[Repeat review/fix cycle as needed]
       ↓
Publish PR when ready
```
