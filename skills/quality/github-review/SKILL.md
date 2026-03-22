---
name: github-review
description: Address GitHub PR review comments - pull feedback, plan approach, and execute fixes.
version: 1.0.0
---

# GitHub Review Skill

You are entering the **github-review phase**. You will address review comments from a GitHub Pull Request.

## Process

### Step 0: Detect Stack Structure

Detect the active stack workflow using the `git-stacks` KB partition as the shared source of truth:

1. `list_kb_documents` for partition `git-stacks`
2. `read_kb_document_by_path` for `/index.md`
3. Run the dedicated-client checks from `git-stacks/index.md`
   - If a dedicated client is detected, record `STACK_CLIENT` accordingly
   - If no dedicated client is detected, inspect the current PR base and local branch relationships to decide whether this repo is using a native git stack
   - If confirmed, record `STACK_CLIENT=native-git`

4. **Load the matching KB client doc before running any stack-specific command:**
   - `charcoal` → `read_kb_document_by_path` for `/charcoal.md`
   - `git-town` → `read_kb_document_by_path` for `/git-town.md`
   - `native-git` → `read_kb_document_by_path` for `/native-git.md`
   - Use the client doc as the source of truth for stack navigation commands

**If in a stack:**
- You may have multiple PRs with review comments
- Present option to address comments from all PRs or just current

**Present to user (if in stack):**
```
## Stack Detected

Your stack has N PRs with open review comments:
| PR | Branch | Open Comments |
|----|--------|---------------|
| #123 | feat/part-1 | 2 |
| #124 | feat/part-2 | 5 |
| #125 | feat/part-3 | 0 |

How would you like to proceed?
1. Address all PRs (recommended) - Fix comments across all PRs
2. Address current PR only (#124) - Fix comments on feat/part-2 only
```

### Step 1: Pull OPEN (Unresolved) PR Review Comments

**For stacked PRs:** Pull comments from each PR in scope.

First, identify the PR(s) and pull only **unresolved** review threads using GraphQL (the REST API does not expose resolved/unresolved status):

```bash
# Get PR number and basic info from current branch
gh pr view --json number,title,url,reviewDecision

# Get ONLY unresolved review threads using GraphQL
gh api graphql -f query='
query($owner: String!, $repo: String!, $pr: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $pr) {
      reviewThreads(first: 100) {
        nodes {
          isResolved
          path
          line
          comments(first: 10) {
            nodes {
              author { login }
              body
              createdAt
            }
          }
        }
      }
    }
  }
}' -f owner='{owner}' -f repo='{repo}' -F pr=<PR_NUMBER>
```

**Important:** Filter the results to only show threads where `isResolved: false`.

Present the feedback summary to the user:

**For stacked PRs:**
```
## Stack Review Summary

### PR #123: feat/part-1 (Add User model)
**Review Decision:** approved

*No open comments*

---

### PR #124: feat/part-2 (Add User API)
**Review Decision:** changes_requested

#### Open (Unresolved) Review Comments

1. **@reviewer** on `UserController.cs:42`
   > Missing null check here

2. **@reviewer** on `UserController.cs:87`
   > Consider using async

---

### PR #125: feat/part-3 (Add tests)
**Review Decision:** pending

*No open comments*

---

**Total open comments across stack:** 2
```

**For single PR:**
```
## PR Review Summary

**PR:** #<number> - <title>
**URL:** <url>
**Review Decision:** <approved/changes_requested/pending>

### Open (Unresolved) Review Comments

1. **@reviewer** on `file.cs:42`
   > Comment text here

2. **@reviewer** on `file.cs:87`
   > Comment text here

**Resolved comments (X):** Not shown - already addressed
```

### Step 1.5: Query Knowledge Base for Context

Before analyzing the review comments, query the KB MCP for relevant best practices and patterns:

1. Call `list_kb_documents` to see available KB documents
2. Identify the topics raised in the review comments (e.g., null handling, async patterns, validation, naming)
3. Call `read_kb_document_by_keywords` with keywords matching those topics
4. Use any relevant guidance found to inform your fix approach — if the KB has an opinion on how something should be done, follow it

This ensures fixes align with established project patterns and best practices, not just the reviewer's comment in isolation.

### Step 2: Plan Approach to Feedback

For each review comment, analyze and categorize (using KB context from Step 1.5 to inform your approach):

**Categories:**
- **Must Fix**: Blocking issues, bugs, security concerns
- **Should Fix**: Best practice improvements, code quality
- **Discuss**: Ambiguous feedback that needs clarification
- **Won't Fix**: Feedback you disagree with (explain why)

**For each comment, determine:**
1. What change is being requested?
2. Do you understand the request clearly?
3. Do you agree with the feedback?
4. What's the implementation approach?

**Use AskUserQuestion for:**
- Ambiguous feedback where multiple interpretations exist
- Feedback you disagree with - confirm before ignoring
- Conflicting comments from different reviewers
- Architectural decisions that affect other parts of the codebase

### Step 3: Present Plan for Approval

Before making any changes, present your plan:

**For stacked PRs (group by PR):**
```
## Addressing Review Comments

### PR #124: feat/part-2

#### Must Fix (2 items)
1. Missing null check - **Approach:** Add null check with early return
2. Async usage - **Approach:** Convert to async/await pattern

#### Should Fix (0 items)
*None*

---

### PR #125: feat/part-3
*No comments to address*

---

**Total fixes planned:** 2

Proceed with fixes? [Use AskUserQuestion to confirm]
```

**For single PR:**
```
## Addressing Review Comments

### Must Fix (X items)
1. [Comment summary] - **Approach:** [how you'll fix it]
2. ...

### Should Fix (X items)
1. [Comment summary] - **Approach:** [how you'll fix it]
2. ...

### Discuss (X items)
1. [Comment summary] - **Question:** [what needs clarification]
2. ...

### Won't Fix (X items)
1. [Comment summary] - **Reason:** [why you disagree]
2. ...

---

Proceed with fixes? [Use AskUserQuestion to confirm]
```

### Step 4: Execute Fixes

After approval, work through each item:

1. **Read the relevant file(s)** before making changes
2. **Make the fix** using Edit tool
3. **Verify the fix** - run tests/build if applicable
4. **Mark as complete** and move to next item

Track progress using TodoWrite:
```
- [x] Fix: Null check on line 42 (reviewer: @alice)
- [x] Fix: Rename variable for clarity (reviewer: @bob)
- [ ] Fix: Add error handling (reviewer: @alice)
```

### Step 4.5: Verify Only Intended Files Changed

**Before committing, verify no unrelated files are staged:**

```bash
git status
git diff --name-only --cached
```

**Watch for:**
- Files in `.github/` that shouldn't change
- Config files that weren't part of the fix
- Files renamed by accident (R status in git)
- Any file not directly related to the review comments

**If unrelated files appear, unstage them:**
```bash
git restore --staged <unrelated-file>
```

**Why this matters:** It's easy to accidentally stage unrelated files during development. Committing them creates noise in the PR and can cause unintended side effects. Always verify the staged file list matches exactly what you intended to change.

### Step 5: Summary and Reply Suggestions

After completing all fixes:

```
## Fixes Complete

### Changes Made
- `file1.cs`: Added null check, renamed variable
- `file2.cs`: Added error handling

### Suggested PR Comment

> Thanks for the review! I've addressed all the feedback:
>
> - Added null check on line 42
> - Renamed `x` to `descriptiveName` for clarity
> - Added error handling for the edge case
>
> Ready for another look!

### Unresolved Items
[List any items marked "Discuss" or "Won't Fix" that need conversation]
```

## Command Reference

### Stack Client Detection

Use the `git-stacks` KB partition as the shared source of truth:

1. `list_kb_documents` for partition `git-stacks`
2. `read_kb_document_by_path` for `/index.md`
3. Run the dedicated-client checks from `/index.md`
4. Load the matching client doc: `/charcoal.md`, `/git-town.md`, or `/native-git.md`

### GitHub CLI

```bash
# Get PR info from current branch
gh pr view --json number,title,url,reviewDecision

# Get ALL review threads (resolved and unresolved) via GraphQL
# NOTE: REST API does NOT expose resolved/unresolved status!
gh api graphql -f query='
query($owner: String!, $repo: String!, $pr: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $pr) {
      reviewThreads(first: 100) {
        nodes {
          isResolved
          path
          line
          startLine
          comments(first: 10) {
            nodes {
              author { login }
              body
              createdAt
              url
            }
          }
        }
      }
    }
  }
}' -f owner='{owner}' -f repo='{repo}' -F pr=123

# Filter for unresolved only using jq
gh api graphql -f query='...' | jq '.data.repository.pullRequest.reviewThreads.nodes | map(select(.isResolved == false))'

# Get general PR comments (not inline review comments)
gh pr view 123 --json comments

# Reply to a review thread (if needed)
gh api repos/{owner}/{repo}/pulls/comments/{comment_id}/replies -f body="Fixed in latest commit"
```

**Why GraphQL?** The REST API (`gh api repos/.../pulls/.../comments`) returns all review comments but does NOT include the `isResolved` status. Only the GraphQL API exposes `reviewThreads.isResolved`.

## When to Use

- After receiving PR review feedback
- When `gh pr status` shows "Changes requested"
- When you have pending review comments to address
- After a code review meeting where feedback was discussed

## Linking to Original Plan

When running github-review, check if there's a related plan file:

1. **Check branch name** for plan hints (e.g., `feat/feature-name` → `.plans/*-feature-name.md`)
2. **Check .plans/ directory** for recent plans matching the feature
3. **Reference the plan** in your fix approach for context

This keeps review fixes connected to the original implementation plan.

## Full Workflow Integration

```
/plan → creates .plans/YYYY-MM-DD-feature.md
       ↓
/work .plans/YYYY-MM-DD-feature.md → implements
       ↓
/review → AI code review
       ↓
/pr-push → creates draft PR
       ↓
[Human reviews PR on GitHub]
       ↓
/github-review → THIS SKILL - addresses feedback
       ↓
/pr-push → pushes fixes (optional, if needed)
       ↓
[Repeat until approved]
```

## Output Format

Always structure your output as:

1. **Summary of feedback** (what reviewers said)
2. **Plan** (how you'll address each item)
3. **Confirmation** (ask before proceeding)
4. **Execution** (make the changes)
5. **Summary** (what was done, suggested reply)
