---
name: rebase-fix
description: Resolve merge/rebase conflicts and continue restacking until the entire stack is clean. Use when the user says "fix rebase", "fix conflicts", "resolve conflicts", "restack", "gt sr", "stack rebase", or when a rebase or restack operation has stopped due to merge conflicts.
---

# Rebase Fix

Resolve merge and rebase conflicts iteratively across an entire stack, continuing the restack until every branch is clean. Works with any stacking client (Charcoal/Graphite, Git Town, native git) or a plain git rebase.

## When to Use

- A rebase or restack stopped due to merge conflicts
- The user says "fix rebase", "fix conflicts", "resolve conflicts"
- `git status` shows `UU` (unmerged) files
- A stacking client reports a conflict during `gt sr`, `git town sync`, or similar

## Process

### Step 1: Detect Stack Client, Rebase State, and Stack Shape

Use the `git-stacks` KB partition as the shared source of truth for git-client detection:

1. `list_kb_documents` for partition `git-stacks`
2. `read_kb_document_by_path` for `/index.md`
3. Run the detection order from `/index.md` in parallel with:

```bash
git status
```

Use `git-stacks/index.md` to classify `charcoal` or `git-town`. If neither dedicated client is detected, classify `native-git` only when `git status` shows a rebase, cherry-pick, or unresolved conflicts. Otherwise classify `none`.

If `client != none`, read the matching KB client doc before continuing:

- `charcoal` → `/charcoal.md`
- `git-town` → `/git-town.md`
- `native-git` → `/native-git.md`

After classification, use this skill-specific command map:

| Condition | Client | Sync Command | Continue Command | Restack Command | Stack Enumerate |
|-----------|--------|-------------|-----------------|-----------------|-----------------|
| Dedicated client is `charcoal` | `charcoal` | `gt repo sync --no-interactive` | `gt continue` | `gt stack restack --no-interactive` | `gt log short` |
| Dedicated client is `git-town` | `git-town` | N/A | `git town continue` | `git town sync` | `git town branch` |
| No dedicated client, but `git status` shows active rebase/conflicts | `native-git` | N/A | `git rebase --continue` | N/A | N/A |
| No dedicated client and no active rebase/conflicts | `none` | N/A | N/A | N/A | N/A |

#### Sync client state before restacking

**Critical for Charcoal:** Before recording the stack or running any restack, sync the client's internal metadata with the remote. Without this, Charcoal compares against stale state and may incorrectly report branches "do not need to be restacked" even when the trunk has moved forward.

```bash
# For charcoal — always run before gt stack restack
gt repo sync --no-interactive
```

If `git status` shows an active rebase (conflicts already in progress), skip the sync — the rebase must be resolved first via the continue loop before syncing.

#### Record the full stack

For Charcoal, parse `gt log short` to extract the ordered list of branches from bottom (closest to trunk) to top. Example output:

```
◯ feat/step-3
│ 1 commit
◯ feat/step-2          ← conflicts may start here
│ 2 commits
◯ feat/step-1          ← you are here, mid-rebase
│ 1 commit
◯ main (trunk)
```

Record this as the **stack manifest** — you'll use it to track progress across the entire restack.

If no rebase is in progress and no conflicts exist, inform the user and exit.

### Step 2: Resolve-Stage-Continue Loop (Per Branch)

This is the inner loop. It resolves conflicts for the **current rebase step** (one branch being rebased onto its parent):

```
while conflicts exist on current branch:
    1. Identify conflicted files
    2. Read and resolve each file
    3. Verify resolution
    4. Stage and continue
```

#### 2a: Identify Conflicted Files

```bash
git diff --name-only --diff-filter=U
```

#### 2b: Read and Resolve Each Conflicted File

Read every conflicted file in parallel. For each file:

1. **Understand both sides.** Read the full file content. Identify the `<<<<<<<` HEAD (current) and `>>>>>>>` incoming blocks.

2. **Determine intent.** The goal is to combine both sides correctly:
   - If both sides add **independent features** (different imports, different functions, different fields), keep both.
   - If the incoming side **replaces** the HEAD version (same function rewritten with a new signature, new implementation), take the incoming version.
   - If both sides modify the **same lines** differently, analyze surrounding code to determine which version is consistent with the rest of the file.

3. **Watch for collateral damage.** After resolving conflict markers, check for:
   - **Duplicate declarations** (e.g., two `db?` fields, two identical imports)
   - **Stale references** (e.g., an import that was removed by one side but the other side still references it)
   - **Indentation mismatches** from the merge (one side used 2-space indent inside a block, the other used top-level)

4. **Apply the fix** using the Edit tool. Remove all `<<<<<<<`, `=======`, and `>>>>>>>` markers.

#### 2c: Verify Resolution

```bash
# Ensure no conflict markers remain in any package/source directory
rg '^[<>=]{7}' <relevant-paths>
```

If markers remain, fix them before proceeding.

#### 2d: Stage and Continue

Stage resolved files, then invoke the client-specific continue command:

| Client | Stage | Continue |
|--------|-------|----------|
| `charcoal` | `gt add .` or `gt add <files>` | `gt continue` |
| `git-town` | `git add <files>` | `git town continue` |
| `native-git` | `git add <files>` | `git rebase --continue` |

**If the continue command succeeds cleanly** → proceed to Step 3 (check next branch).

**If the continue command reports new conflicts on the same branch** → loop back to 2a.

**If the continue command fails for a non-conflict reason** → stop and report the error to the user.

### Step 3: Stack Progression Loop (Outer Loop)

After the inner loop completes for one branch, the restack client may automatically advance to the next branch in the stack and encounter new conflicts. This is the **outer loop** that drives the full stack:

```
stack_branches = [branch1, branch2, branch3, ...]  # from Step 1
resolved_branches = []

while restack is not complete:
    # Check current state
    status = git status

    if status shows conflicts:
        current_branch = git branch --show-current
        run Step 2 (inner loop) to resolve
        resolved_branches.append(current_branch)

    elif status shows rebase in progress but no conflicts:
        # Mid-rebase but clean — continue to let it advance
        run continue command

    elif status is clean:
        # Current branch done. Check if the full stack is restacked.
        if client == charcoal:
            # Sync metadata then check if more restacking is needed
            run `gt repo sync --no-interactive`
            run `gt log short` to check stack state
            if all branches are restacked → break
            else → run `gt stack restack --no-interactive` to continue restacking upward
        elif client == git-town:
            run `git town sync` to check/continue
        elif client == native-git:
            break  # single rebase, no stack concept
```

#### Key behaviors per client:

**Charcoal (`gt`):**
- **Always run `gt repo sync --no-interactive` before `gt stack restack --no-interactive`** to ensure Charcoal's internal metadata reflects the current remote state. Without this, Charcoal may falsely report branches "do not need to be restacked."
- `gt stack restack --no-interactive` restacks the entire stack bottom-up. When it hits a conflict, it stops.
- After resolving and running `gt continue`, it may either continue restacking or return you to a clean state on the conflicted branch.
- If `gt continue` returns cleanly but there are still un-restacked branches above, **re-run `gt repo sync --no-interactive` then `gt stack restack --no-interactive`** to continue upward.
- Use `gt log short` to verify: all branches should show as up-to-date with their parents.

**Git Town:**
- `git town sync` operates similarly — resolves one branch at a time.
- After `git town continue`, check if more branches need syncing.

**Native git:**
- Only one rebase at a time. The outer loop is effectively a single iteration.

### Step 4: Verify Completion

After the outer loop exits:

```bash
# Confirm clean state
git status --short

# For charcoal, confirm the full stack is restacked
gt log short 2>/dev/null

# Check that we're on the expected branch
git branch --show-current
```

Report a summary:

```
## Rebase Complete

**Branches restacked:** <ordered list from stack manifest>
**Conflicts resolved:** <count> files across <count> branches
**Client:** <charcoal|git-town|native-git>
**Current branch:** <branch name>
```

## Resolution Heuristics

These patterns cover the most common conflict shapes:

### Import Conflicts

Both sides add different imports to the same block.
**Resolution:** Merge both import sets. Remove duplicates. Verify each import is actually used in the file.

### Additive Conflicts (Both Sides Add)

HEAD adds feature A, incoming adds feature B to the same location.
**Resolution:** Keep both. Order them logically (e.g., alphabetical for imports, HEAD-then-incoming for code blocks).

### Replacement Conflicts (Incoming Rewrites)

HEAD has an old implementation, incoming has a completely new one (different function signature, different types, different approach).
**Resolution:** Take the incoming version. Verify that callers in the file match the new signature.

### Type/Interface Conflicts

HEAD adds field `foo`, incoming adds field `bar` to the same type.
**Resolution:** Keep both fields. Check for duplicate field names.

### Mixed Conflicts (Additive + Replacement)

Some hunks are additive, others are replacements — within the same file.
**Resolution:** Handle each hunk independently. Don't assume the whole file is one or the other.

### Cascading Conflicts Across Branches

When Branch B depends on Branch A, and you resolved conflicts in A by changing a function signature or removing code, Branch B may conflict in the same area.
**Resolution:** Apply the same resolution direction consistently. If you took the incoming version in Branch A, the "HEAD" in Branch B's conflict already reflects that resolution — take the incoming version again to carry the change upward.

## Safety Rules

1. **Never blindly take one side.** Always read both sides and the surrounding code.
2. **Never leave conflict markers.** Verify with `rg '^[<>=]{7}'` after every resolution.
3. **Never skip verification.** Even if you're confident, run the check.
4. **If a resolution is ambiguous, ask the user.** Use `AskUserQuestion` with the two options and your recommendation.
5. **Don't run builds or typechecks** unless the user asks. The goal is conflict resolution, not full validation.
6. **Preserve the user's branch position.** After restacking, return to the branch the user was on when they invoked the skill.

## Error Handling

### Continue command reports "not in a rebase"

The rebase may have completed between your stage and continue. Check `git status` — if clean, the rebase is done. Proceed to the outer loop to check remaining branches.

### Continue command fails with "commit is empty"

The resolution produced no changes vs. the target. Use `git rebase --skip` (or the client equivalent) to skip that commit.

### Restack command says "already up to date" or "does not need to be restacked"

First verify that `gt repo sync --no-interactive` was run before the restack. If sync was skipped, Charcoal's stale metadata may produce false "does not need" results. Run sync and retry the restack.

If sync was already done and the message persists, all branches in the stack are correctly based on their parents. The stack is clean — report success.

### A branch was deleted or moved during restack

If `gt log short` shows a different stack shape than the original manifest, re-enumerate the stack and continue with the updated list.

### Unrecognized conflict shape

If you cannot determine the correct resolution for a conflict, stop and present both sides to the user with `AskUserQuestion`:

```
I can't automatically resolve this conflict in <file>:<lines>.

**HEAD (current):**
<code block>

**Incoming:**
<code block>

Which version should I keep, or should I combine them differently?
```
