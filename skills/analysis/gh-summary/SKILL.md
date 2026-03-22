---
name: gh-summary
description: Summarize your merged PRs across repos and interpret the value delivered. Use when user wants to see what they've accomplished, prepare for standups, or reflect on their contributions.
version: 1.0.0
allowed-tools: Bash
---

# GitHub Contribution Summary

Summarize merged PRs and interpret the business/engineering value delivered.

## Usage

- `/gh-summary` - Current repo, last 30 days
- `/gh-summary last 7 days` - Current repo, last 7 days
- `/gh-summary since January 1st` - Current repo, since date
- `/gh-summary owner/repo1 owner/repo2 last 30 days` - Multiple repos

## Arguments

Arguments can be provided in any order. The skill will parse:

1. **Repos** (optional): Comma or space-separated list of repos in `owner/repo` format
   - If omitted, uses the current working directory's repo
   - Examples: `owner/repo-name`, `owner/repo1,owner/repo2`

2. **Time range** (optional): Natural language time specification
   - Relative: "last 7 days", "last 2 weeks", "last 30 days"
   - Absolute: "since January 1st", "since 2026-01-01"
   - If omitted, defaults to "last 30 days"

## Process

### Step 1: Parse Arguments

Parse the ARGUMENTS string to extract:
- **repos**: List of repos, or empty (meaning current repo)
- **time_range**: Natural language time, or "last 30 days" default

Convert time range to ISO date format (YYYY-MM-DD) for the `gh` search query.

### Step 2: Get GitHub Username

```bash
gh api user --jq '.login'
```

### Step 3: Fetch PRs for Each Repo

For each repo (or current repo if none specified):

```bash
gh pr list --repo {repo} --author {username} --state merged \
  --search "merged:>={iso_date}" --limit 200 \
  --json number,title,body,mergedAt,additions,deletions,changedFiles,commits,url
```

If no `--repo` flag needed (current repo), omit it:

```bash
gh pr list --author {username} --state merged \
  --search "merged:>={iso_date}" --limit 200 \
  --json number,title,body,mergedAt,additions,deletions,changedFiles,commits,url
```

### Step 4: Calculate Stats

From the PR data, calculate:
- **PR count**: Total number of PRs merged
- **Lines added**: Sum of `additions` across all PRs
- **Lines removed**: Sum of `deletions` across all PRs
- **Net lines**: additions - deletions
- **Files changed**: Sum of `changedFiles` across all PRs
- **Commits**: Sum of commit counts (length of `commits` array) across all PRs
- **Repos touched**: Count of unique repos (if multi-repo)

### Step 5: Analyze Themes

Read through PR titles and bodies to identify:
- **Categories of work**: Features, bug fixes, refactoring, documentation, tooling, infrastructure
- **Domains/areas touched**: What parts of the system were modified
- **Patterns**: Recurring themes or ongoing initiatives

### Step 6: Summarize and Interpret Value

Create a summary that includes:

1. **Stats block**: The numbers from Step 4
2. **Work summary**: A paragraph describing the themes and direction of work (NOT a list of every PR)
3. **Value delivered**: Interpretation of business or engineering leverage:
   - Did this unblock other work?
   - Did this reduce toil or improve efficiency?
   - Did this add user-facing value?
   - Did this improve system reliability or performance?
   - Did this pay down tech debt?

### Step 7: Offer to Expand

After presenting the summary, offer:
- "Would you like me to expand on any specific area?"
- "Want more detail on [specific theme]?"
- "Should I list the individual PRs in [category]?"

## Output Format

```
## Your Contributions: {time_range}

### Stats
- **{N} PRs** merged
- **+{additions}/-{deletions}** lines (net: {net})
- **{files}** files changed
- **{commits}** commits
- **{repos}** repos (if multi-repo)

### Summary
{Thematic summary of work direction - 2-3 paragraphs describing what was accomplished,
organized by theme rather than listing each PR}

### Value Delivered
{Interpretation of business/engineering leverage - what impact did this work have?
Be specific about the type of value: user-facing features, developer productivity,
system reliability, reduced toil, unblocked initiatives, etc.}

---

Would you like me to expand on any area or see the individual PRs?
```

## Tips for Value Interpretation

When assessing value, consider:

- **Leverage**: Did a small change enable large outcomes? (e.g., fixing a bug that affected many users)
- **Multiplier effects**: Did this make other developers more productive?
- **Risk reduction**: Did this prevent future problems or reduce operational burden?
- **Capability unlocking**: Did this enable new features or use cases?
- **Compounding benefits**: Will this work continue to pay dividends over time?

Be honest - not every PR delivers massive value. It's fine to note that some work was routine maintenance or incremental progress. The goal is accurate reflection, not inflation.
