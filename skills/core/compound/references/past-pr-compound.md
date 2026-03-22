# Past PR Compound Skill

You are entering the **past-pr-compound phase**. You will analyze merged PRs to identify recurring patterns and document them.

## Configuration

**Learnings Directory Lookup:**
1. First, check for project-local learnings at `<git-root>/.llm/learnings/`
2. If not found, fall back to `[paths.learnings_directory]` from `~/.agentic-eng/config.toml`

This allows each project to have its own learnings while maintaining backwards compatibility. New learnings should be stored in the project-local directory when available.

## Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--limit N` | 20 | Number of PRs to analyze |
| `--after YYYY-MM-DD` | - | Only PRs merged after this date |
| `--before YYYY-MM-DD` | - | Only PRs merged before this date |
| `--threshold N` | 2 | Minimum occurrences to count as "recurring" |

**Date filtering examples:**
```bash
# Last 4 weeks of PRs
/past-pr-compound --after 2025-12-15

# December PRs only
/past-pr-compound --after 2025-12-01 --before 2025-12-31

# Backfill October
/past-pr-compound --after 2025-10-01 --before 2025-10-31
```

## Process

### Step 1: Fetch Merged PRs

Fetch merged PRs from the current repository:

```bash
# Without date filter
gh pr list --state merged --limit <LIMIT> --json number,title,mergedAt,url

# With date filter (use search syntax)
gh pr list --state merged --limit <LIMIT> --search "merged:>YYYY-MM-DD" --json number,title,mergedAt,url

# Date range
gh pr list --state merged --limit <LIMIT> --search "merged:YYYY-MM-DD..YYYY-MM-DD" --json number,title,mergedAt,url
```

### Step 2: Fetch Review Comments for Each PR

For each PR, use GraphQL to get review threads and comments:

```bash
gh api graphql -f query='
query($owner: String!, $repo: String!, $pr: Int!) {
  repository(owner: $owner, name: $repo) {
    pullRequest(number: $pr) {
      title
      body
      reviews(first: 50) {
        nodes {
          author { login }
          body
          state
        }
      }
      reviewThreads(first: 100) {
        nodes {
          isResolved
          path
          line
          comments(first: 20) {
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

**Bot filtering:** Automatically skip comments from:
- `github-actions[bot]`
- `dependabot[bot]`
- `renovate[bot]`
- Any author ending in `[bot]`

### Step 3: Extract Lessons Per PR

For each PR, analyze review comments and extract **distinct lessons**. A lesson is a normalized concept, not the raw comment text.

**Focus on:**
- Actionable feedback (not nitpicks like typos)
- Code quality patterns
- Security concerns
- Performance considerations
- Architecture decisions
- Testing gaps

**Lesson format:**
```
{ lesson: string, pr: number, source: "review_comment" | "review_summary" }
```

**Present lessons grouped by PR:**

```
## PR #123: Add user authentication
**Lessons:**
1. Always validate JWT expiration before trusting claims
2. Use bcrypt with cost factor 12+ for password hashing
3. Log authentication failures for security auditing

## PR #124: Fix database queries
**Lessons:**
1. Always use parameterized queries to prevent SQL injection
2. Add indexes for frequently queried columns
```

### Step 4: Cluster Across PRs

Review ALL extracted lessons and identify those that appear semantically in `<threshold>` or more PRs.

**Important:** Use semantic similarity, not keyword matching. These are the same lesson:
- "Add null check"
- "Handle null case"
- "Validate input is not null"

**Present recurring lessons:**

```
## Recurring Lessons (appeared in 2+ PRs)

### 1. Input Validation
- PR #123: "Always validate JWT expiration"
- PR #127: "Validate user input before processing"
- PR #131: "Check request parameters for null"
**Summary:** Validate all external inputs before trusting them.

### 2. Security Logging
- PR #123: "Log authentication failures"
- PR #128: "Add audit trail for admin actions"
**Summary:** Log security-relevant events for auditing.
```

**Only include lessons meeting the threshold (default: 2+ PRs).**

### Step 5: User Approval

Present the recurring lessons and ask for approval:

```
## Recurring Lessons Found

I found [N] recurring lessons across [M] PRs.

[Show recurring lessons as above]

---

**Which lessons should I document?**
1. All of them
2. Let me select specific ones
3. None - skip documentation
```

Use AskUserQuestion to get approval.

### Step 6: Document Approved Lessons

For each approved recurring lesson, create a file in the learnings directory:

```bash
# Determine learnings directory (project-local first, config fallback)
LEARNINGS_DIR="$(git rev-parse --show-toplevel 2>/dev/null)/.llm/learnings"
if [ ! -d "$LEARNINGS_DIR" ]; then
  LEARNINGS_DIR="<learnings_directory from config.toml>"
fi
mkdir -p "$LEARNINGS_DIR/pr-learnings"
```

**Location:** `$LEARNINGS_DIR/pr-learnings/`

**File format:**
```markdown
# [Lesson Title]

**Date:** YYYY-MM-DD
**Source PRs:** #123, #127, #131

## The Pattern
[What this lesson teaches - written as actionable guidance]

## Examples from PRs
- PR #123: [specific feedback from review]
- PR #127: [specific feedback from review]

## Prevention
[How to avoid this issue in future code]
```

**Filename:** `YYYY-MM-DD-lesson-slug.md` (e.g., `2025-01-11-validate-external-inputs.md`)

### Step 7: Summary

Present a final summary:

```
## Past PR Compound Complete

**PRs Analyzed:** [N]
**Total Lessons Extracted:** [X]
**Recurring Lessons Found:** [Y] (threshold: [Z]+)
**Lessons Documented:** [W]

**New Learning Files:**
- `pr-learnings/2025-01-11-validate-external-inputs.md`
- `pr-learnings/2025-01-11-security-logging.md`

**Next Steps:**
- Review the documented lessons in `$LEARNINGS_DIR/pr-learnings/`
- Consider adding to CLAUDE.md if broadly applicable
- Run `/compound` after future PRs to continue compounding

---

**Knowledge Compounded!** These patterns from past reviews are now documented for future reference.
```

## Skill Flow Summary

```
/past-pr-compound [--limit N] [--after DATE] [--before DATE] [--threshold N]
    |
    v
1. Fetch merged PRs (filtered by date range if specified)
    |
    v
2. For each PR, fetch review threads via GraphQL
    |
    v
3. Extract lessons from review comments
   (filter bot comments, focus on actionable feedback)
    |
    v
4. Present all lessons, grouped by PR
    |
    v
5. Analyze for recurring patterns (threshold+ PRs)
    |
    v
6. Present recurring lessons for user approval
    |
    v
7. Document approved lessons to learnings library
```

## When to Use

- Monthly review of PR feedback patterns
- Onboarding to understand common code review themes
- Backfilling learnings from historical PRs
- After a sprint to extract team-wide patterns
