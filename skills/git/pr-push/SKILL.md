---
name: pr-push
description: Create or update a draft PR, auto-fixing pre-commit failures until push succeeds.
version: 1.1.0
---

# PR Push Skill

You are entering the **PR push phase**. You will create or update a draft PR, automatically fixing any pre-commit hook failures until the push succeeds.

**CRITICAL SAFETY RULE: This skill MUST NEVER publish a PR. Always use `--draft` flag.**

## Process

### Step 1: Pre-flight Checks

Run checks 1-5 in parallel where possible.

1. **Check current branch:**
   ```bash
   git branch --show-current
   ```
   - If on `main`: Ask user what branch name to use, then create the branch using the detected stack workflow from Step 1.4
   - Otherwise: Continue with current branch

2. **Check if PR already exists (run early — gates later steps):**
   ```bash
   gh pr view --json number,state,isDraft,url,title,body,baseRefName 2>/dev/null
   ```
   - If PR exists: **Record PR number, URL, current body, and current base branch.** Skip Step 2 (metadata generation) and skip stack submission or `git push` if remote is already up-to-date. Proceed to update description if needed.
   - If no PR: Will create new draft PR — continue to Step 2.

3. **Check for uncommitted changes:**
   ```bash
   git status --porcelain
   ```
   - If there are uncommitted changes: Warn user and ask if they should be committed first

4. **Detect the active stack workflow** using the `git-stacks` KB partition as the shared source of truth:
   - `list_kb_documents` for partition `git-stacks`
   - `read_kb_document_by_path` for `/index.md`
   - Run the dedicated-client checks from `git-stacks/index.md`
   - If a dedicated client is detected, record `STACK_CLIENT` accordingly
   - If no dedicated client is detected, inspect GitHub base refs and local branch relationships to decide whether this is a native git stack
   - **Load the matching KB client doc** (`/charcoal.md`, `/git-town.md`, or `/native-git.md`) before pushing or navigating the stack
   - If no stack is confirmed: **Use standard git workflow** (Step 3b)

5. **Resolve the target PR base from local branch relationships:**
   ```bash
   git rev-parse --abbrev-ref --symbolic-full-name @{u} 2>/dev/null
   git log --pretty=format:'%D' | grep -v '^$' | grep -v "^HEAD -> $(git branch --show-current)$" | head -1 | tr ',' '\n' | sed 's/^ *//' | grep -v "HEAD" | grep -v "origin/HEAD" | head -1
   ```
   - Prefer the detected stack client's local parent metadata when it is available
   - Otherwise, use the git upstream/tracking branch and normalize remote refs like `origin/feature/foo` to `feature/foo`
   - Otherwise, fall back to the existing local parent-branch heuristic
   - If multiple sources disagree, or no unambiguous base can be determined, **STOP and ask the user**
   - Record the resolved branch as `TARGET_BASE`
   - **Never silently fall back to the repository default branch**

6. **Check if local is ahead of remote:**
   ```bash
   git rev-list @{u}..HEAD --count 2>/dev/null
   ```
   - If 0 (or remote matches local) AND PR already exists → **Skip push entirely**, jump to Step 4 (update description if needed)
   - If >0 or no upstream → push is needed

7. **CRITICAL: Verify the feature works:**
   - For CLI commands: Run the actual command with test data
   - For API changes: Call the endpoint
   - For library changes: Run a consumer
   - **Build success is NOT sufficient verification**
   - **If you cannot verify the feature works, STOP and ask user for verification steps**

### Step 2: Generate PR Metadata

**Only needed if creating a new PR (no existing PR).**

1. **Get commits since branching from the resolved base:**
   ```bash
   git log <target-base>..HEAD --oneline
   ```

2. **Determine conventional PR title type:**
   - Analyze commit messages from `<target-base>..HEAD` for prefixes (fix:, feat:, chore:, etc.)
   - If multiple "fix:" commits → type is `fix`
   - If multiple "feat:" commits → type is `feat`
   - If mixed or no clear pattern → type is `chore`

3. **Generate title in format:** `<type>([scope]): <Sentence>`
   - Scope: Extract from file paths or commit messages (optional)
   - Sentence requirements:
     - Must be a grammatical English sentence in present tense
     - Must start with a capital letter
   - Append the PR number at the end (for example, `feat(mobile): Update login view to light mode (#3567)`)
   - Keep the Conventional Commits type/scope prefix lowercase

4. **Find and read PR template (REQUIRED — do not skip):**
   ```bash
   # Check for auto-ticket.no-qa.md first (preferred)
   if [ -f ".github/PULL_REQUEST_TEMPLATE/auto-ticket.no-qa.md" ]; then
     TEMPLATE=".github/PULL_REQUEST_TEMPLATE/auto-ticket.no-qa.md"
   elif [ -f ".github/PULL_REQUEST_TEMPLATE/default.md" ]; then
     TEMPLATE=".github/PULL_REQUEST_TEMPLATE/default.md"
   fi
   ```
   - **You MUST check for these templates before creating a PR.**
   - If a template is found, read its contents with the Read tool.

5. **Generate PR body:**
   - **With template (preferred):** Use the template as the PR body structure. Fill in sections you can populate from the `<target-base>..HEAD` commits/diff (e.g., Summary, Description). Leave other sections with their template placeholders intact for the user to fill.
   - **Without template:** Write a body with `## Summary` (bullet points of changes) and `## Test plan` (checklist).
   - **Never generate a freeform body when a template exists.**

### Step 3a: Push with the Detected Stack Workflow

**If a stack workflow is active (detected in Step 1.4), use the matching client guidance from KB.**

**If PR already exists AND no unpushed commits (Step 1.6) → skip stack submission, go to Step 4.**

Use the client doc as the source of truth for how to:

- Submit or propose the stack as draft PRs
- Preserve the local parent branch as the GitHub PR base
- Keep parent-child PR relationships intact
- Re-run the client workflow after fixing pre-push failures
- Inspect the final stack state and PR URLs

**If the client-specific workflow fails, is interactive-only, or cannot create the expected draft PRs:**
- Fall back to **Step 3b** for the current branch
- Reuse the already-resolved `TARGET_BASE` when falling back
- You MUST still follow **Step 2** to generate PR metadata including template lookup

### Step 3b: Push with Git (Single PR / No Stack)

**If NOT in a detected stack workflow, use standard git:**

**Before creating or updating a PR:**
- Ensure `TARGET_BASE` is resolved from Step 1.5
- If `TARGET_BASE` is missing or ambiguous: **STOP and ask the user**

**Initialize tracking:**
- `fixes_made = []` - List of fixes applied
- `error_attempts = {}` - Map of error signature to attempt count

**Push attempt loop:**

```
while true:
  1. Attempt: git push -u origin <branch>

  2. If SUCCESS:
     - Break loop, proceed to Step 4

  3. If FAILURE (pre-commit hook):
     - Parse the error output
     - Generate error_signature (file + line + error type)

     - If error_signature in error_attempts AND error_attempts[error_signature] >= 2:
       - STOP: "Same error failed twice. Manual intervention needed."
       - Report the error and fixes attempted
       - Exit skill

     - Increment error_attempts[error_signature]

     - Analyze and fix the error:
       a. Read the offending file
       b. Identify the issue (build error, lint error)
       c. Apply the fix
       d. Commit with message: "fix: resolve [error type] in [filename]"
       e. Add to fixes_made list

     - Continue loop (retry push)
```

**Error types to handle:**
- **Build errors**: Compilation errors (language-specific format)
- **Lint errors**: formatting issues, linter errors
- **Other pre-commit failures**: Analyze output and fix accordingly

### Step 4: Create or Update PR

**If no existing PR:**
- If a template was found in Step 2.4, fill it in and pass it as the body:
  ```bash
  gh pr create --draft --base "<target-base>" --title "<generated title>" --body "<filled-in template>"
  ```
- If no template was found:
  ```bash
  gh pr create --draft --base "<target-base>" --title "<generated title>" --body "<generated body>"
  ```

**If PR already exists:**
- Compare the existing PR base to `TARGET_BASE`
- If the bases differ: update the PR first with `gh pr edit <number> --base "<target-base>"`
- Check if the PR body is empty or still has unfilled template placeholders (e.g., `<!--` comments with no real content, `ADD_YOUR_DURATION` still present)
- If body needs filling: Generate a proper description from the `<target-base>..HEAD` commits/diff and update with `gh pr edit <number> --body "<filled body>"`
- If body is already populated: No additional action needed

### Step 5: Report Summary

After successful push:

**For stacked PRs:**
```
## Stack Push Complete

**Stack Structure:**
| PR | Branch | Status | URL |
|----|--------|--------|-----|
| 1  | feat/part-1 | Draft | <url> |
| 2  | feat/part-2 | Draft | <url> |
| 3  | feat/part-3 | Draft | <url> |

### Fixes Applied During Push
[Only show if fixes_made is not empty]
- `file1.cs`: Fixed [error type]

### Next Steps
- Review PRs on GitHub (start with PR 1)
- PRs will merge in order: 1 → 2 → 3
- When PR 1 merges, PR 2's base updates automatically
- Request review when ready (do NOT use this skill to publish)
```

**For single PR (standard git):**
```
## PR Push Complete

**PR:** #<number> - <title>
**URL:** <url>
**Status:** Draft

### Fixes Applied During Push
[Only show if fixes_made is not empty]
- `file1.cs`: Fixed [error type]
- `file2.cs`: Fixed [error type]

### Next Steps
- Review the PR on GitHub
- Add any additional details to the PR description
- Request review when ready (do NOT use this skill to publish)
```

## Safety Rules

**NEVER DO THESE THINGS:**
- NEVER use `gh pr ready` - this publishes the PR
- NEVER omit `--draft` flag when creating
- NEVER use `gh pr merge`
- NEVER automatically publish or mark as ready for review

**ALWAYS:**
- Resolve and use the local `TARGET_BASE`
- Use `gh pr create --draft --base "<target-base>"`
- Keep PR in draft state
- Let user manually publish when ready

## Error Handling

**When to STOP and ask for help:**
1. Same error fails 2 times after attempted fixes
2. Error type is unrecognized
3. Fix attempt makes things worse (more errors than before)
4. Authentication or permission errors
5. The local upstream/parent base is missing or conflicting

**Report format when stopping:**
```
## Push Failed - Manual Intervention Needed

**Error:**
[Error message]

**Fixes Attempted:**
- [List of fixes tried]

**Suggestion:**
[What the user might try]
```

## When to Use

- After implementation is complete and review passes
- When you're ready to create or update a draft PR
- After running `/review` and addressing any P1 issues

## Command Reference

### Stack Client Detection

Use the `git-stacks` KB partition as the shared source of truth:

1. `list_kb_documents` for partition `git-stacks`
2. `read_kb_document_by_path` for `/index.md`
3. Run the dedicated-client checks from `/index.md`
4. Load the matching client doc: `/charcoal.md`, `/git-town.md`, or `/native-git.md`

### Standard Git

```bash
# Check current branch
git branch --show-current

# Check for uncommitted changes
git status --porcelain

# Check if PR exists
gh pr view --json number,state,isDraft,url,baseRefName

# Resolve the local upstream/base branch
git rev-parse --abbrev-ref --symbolic-full-name @{u}

# Get commits for title generation from the resolved local base
git log <base>..HEAD --oneline
git log <base>..HEAD --format="%s"

# Push to origin
git push -u origin <branch>

# Create draft PR against the resolved local base
gh pr create --draft --base <base> --title "title" --body "body"

# Create draft PR with template against the resolved local base
gh pr create --draft --base <base> --title "title" --body-file .github/PULL_REQUEST_TEMPLATE/auto-ticket.no-qa.md

# Update an existing PR base to match the resolved local base
gh pr edit <number> --base <base>
```
