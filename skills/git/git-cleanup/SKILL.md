---
name: git-cleanup
description: Clean up git worktrees and branches for closed PRs and stale branches
version: 1.0.0
---

# Git Cleanup

Clean up local git worktrees and branches that are no longer needed. Identifies branches with closed PRs and stale branches, then removes them after user confirmation.

## When to Use

- When your repo has accumulated many old branches
- After merging/closing multiple PRs
- Periodic maintenance to keep your local repo clean

## Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--stale-weeks N` | 4 | Branches with no commits in more than N weeks (N*7 days) are considered stale. Default 4 = 28 days. Set to 0 to disable stale detection. |

## Process

### Step 1: Gather Information

Run these commands to understand the current state:

```bash
# List all worktrees
git worktree list

# List all local branches with last commit date
git for-each-ref --sort=-committerdate refs/heads/ --format='%(refname:short)|%(committerdate:iso8601)|%(committerdate:relative)'

# Get the default branch
git symbolic-ref refs/remotes/origin/HEAD 2>/dev/null | sed 's@^refs/remotes/origin/@@'

# Get current branch
git branch --show-current
```

For each local branch (except protected ones), check its PR status:

```bash
# Check if branch has any PRs (open, closed, or merged)
gh pr list --head <branch-name> --state all --json number,state,headRefName --limit 1
```

### Step 2: Categorize Branches

Create four categories:

1. **Protected branches** (NEVER delete):
   - `main`
   - `master`
   - `develop`
   - `production`
   - The default branch (from Step 1)
   - The current branch

2. **Closed PR branches** (mark for deletion):
   - Branches where the most recent PR is `CLOSED` or `MERGED`

3. **Stale branches** (mark for deletion):
   - Branches with NO PR (empty result from `gh pr list`) AND last commit older than threshold
   - **Threshold calculation:** `stale_weeks * 7` days. Default is 4 weeks = 28 days.
   - **A branch is stale ONLY if:** `(today - last_commit_date) > (stale_weeks * 7 days)`
   - Example: With default 4 weeks, a branch with last commit 7 days ago is NOT stale (7 < 28)
   - Example: With default 4 weeks, a branch with last commit 30 days ago IS stale (30 > 28)

4. **Active branches** (keep):
   - Branches with open PRs
   - Branches with recent commits (last commit within threshold - e.g., 7 days old is recent when threshold is 28 days)

### Step 3: Identify Worktrees to Remove

Parse `git gtr list` output to find worktrees on branches marked for deletion.

If `git gtr list` is not available (gtr not installed), fall back to `git worktree list`.

Worktree format: `/path/to/worktree  abc1234 [branch-name]`

### Step 4: Present Confirmation

Display the analysis and ask for confirmation using `AskUserQuestion`:

```
## Cleanup Analysis

### Worktrees to Remove
| Path | Branch | Reason |
|------|--------|--------|
| /path/to/worktree | feature/old-thing | PR #123 merged |

### Branches to Delete
| Branch | Reason |
|--------|--------|
| feature/old-thing | PR #123 merged |
| experiment/test | Stale (6 weeks) |

### Keeping
- main (protected)
- develop (protected)
- feature/active (open PR #456)
- bugfix/recent (last commit 2 days ago - within 28-day threshold)

**Total:** 1 worktree, 2 branches to remove
```

Use `AskUserQuestion` with options:
- "Yes, proceed with cleanup"
- "No, cancel"

### Step 5: Execute Cleanup

**Only after user confirms**, execute in this order:

1. **Remove worktrees first** (must happen before branch deletion):
   ```bash
   git gtr rm <branch-name> --yes
   ```
   If gtr is not installed, fall back to `git worktree remove <path>`.
   If a worktree has uncommitted changes, it will fail. Report the error and skip that worktree's branch.

2. **Delete local branches**:
   ```bash
   git branch -D <branch-name>
   ```

3. **Report results**:
   ```
   ## Cleanup Complete

   ### Removed
   - Worktree: /path/to/worktree (feature/old-thing)
   - Branch: feature/old-thing
   - Branch: experiment/test

   ### Skipped (errors)
   - Worktree: /other/path - has uncommitted changes

   Cleanup complete. Removed 1 worktree and 2 branches.
   ```

## Safety Rules

1. **NEVER delete protected branches** - main, master, develop, production, default branch, current branch
2. **ALWAYS show confirmation** before any deletion
3. **Worktrees before branches** - Remove worktree first, then delete branch
4. **Handle failures gracefully** - If worktree removal fails, skip that branch and continue
5. **Current branch safety** - Git won't allow deleting the current branch anyway

## Error Handling

### gh CLI not authenticated

If `gh pr list` fails with authentication error:
```
GitHub CLI is not authenticated. Run `gh auth login` first.
```

### Worktree has uncommitted changes

If `git gtr rm` (or `git worktree remove`) fails:
```
Skipping worktree at /path - has uncommitted changes.
To force removal, manually run: git gtr rm <branch> --force --yes
```

### Branch is checked out in another worktree

This shouldn't happen if we remove worktrees first, but if it does:
```
Cannot delete branch 'X' - it is checked out at '/path'.
Remove the worktree first, or run cleanup from the main worktree.
```

## Example Session

```
User: /git-cleanup

Agent: Let me analyze your branches and worktrees...

## Cleanup Analysis

### Worktrees to Remove
| Path | Branch | Reason |
|------|--------|--------|
| ~/projects/myapp-feature-123 | feature/user-auth | PR #123 merged |

### Branches to Delete
| Branch | Reason |
|--------|--------|
| feature/user-auth | PR #123 merged |
| feature/old-experiment | Stale (8 weeks) |
| bugfix/typo-fix | PR #89 closed |

### Keeping
- main (protected)
- develop (protected)
- feature/new-api (open PR #145)
- feature/current-work (current branch)
- feature/recent-work (last commit 5 days ago - within 28-day threshold)

**Total:** 1 worktree, 3 branches to remove

[AskUserQuestion: Proceed with cleanup?]

User: Yes, proceed

Agent: ## Cleanup Complete

### Removed
- Worktree: ~/projects/myapp-feature-123 (feature/user-auth)
- Branch: feature/user-auth
- Branch: feature/old-experiment
- Branch: bugfix/typo-fix

Cleanup complete. Removed 1 worktree and 3 branches.
```

## Quick Cleanup (Alternative)

For a fast cleanup of merged-PR worktrees without the full analysis, use gtr directly:

```bash
# Preview what would be removed
git gtr clean --merged --dry-run

# Remove worktrees for merged PRs
git gtr clean --merged --yes
```

This only removes worktrees whose branches have merged PRs. It does NOT handle stale branches or provide the detailed categorization that this skill provides. Use it when you want a quick tidy-up.

## Tips

- Run periodically (e.g., weekly) to keep your repo clean
- Use `--stale-weeks 0` if you only want to clean up closed PR branches
- Check `git worktree list` before running if you're unsure what worktrees exist
- The skill only affects local branches and worktrees - remote branches are not touched
