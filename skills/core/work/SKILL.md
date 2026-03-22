---
name: work
description: Execute implementation from a plan with verification at each step.
---

# Work Skill

Execute an implementation plan step by step with verification.

**Announce at start:** "I'm using the work skill to implement this plan."

> **Better with subagents:** If the platform supports subagents, the subagent route produces higher quality output. See Step 4.

## Input

```
/work <harness-dir(.claude|.codex)>/plans/2025-01-07-feature-name.md
```

## Step 1: Load & Review Plan

1. Read the plan file
2. Review critically — identify questions or concerns before starting
3. **If concerns:** raise with user before proceeding
4. **If no concerns:** create TodoWrite task list from steps
5. Extract and note:
   - All implementation steps (full text — needed for subagent route)
   - Validation Methodology section (primary validation command)
   - PR Stack section (branch names and step boundaries)

## Step 2: Worktree Setup

1. Check existing worktrees: `git gtr list`
2. Derive branch name from plan filename (`2026-03-06-add-auth.md` → `feat/add-auth`)
3. **If matching worktree exists** → AskUserQuestion: Use existing? Create new? Work in current dir?
4. **If no matching worktree** → AskUserQuestion: Create worktree? Work in current dir?
   - Create → invoke `/worktree create <branch>`
   - Use existing → `cd` into it, copy `<harness-dir(.claude|.codex)>/plans/` if missing

**CRITICAL:** Always use cwd for file operations — never paths from `config.toml`. This breaks in worktrees where cwd differs from `toolkit_directory`.

## Step 3: Initialize Stack

Parse the PR Stack table from the plan, then detect the active stack workflow:

1. `list_kb_documents` for partition `git-stacks`
2. `read_kb_document_by_path` for `/index.md`
3. Run dedicated-client checks from `/index.md`; classify `native-git` if no dedicated client found
4. Load matching client doc before running any stack command:
   - `charcoal` → `/charcoal.md`, `git-town` → `/git-town.md`, `native-git` → `/native-git.md`
5. Check current branch: `git branch --show-current`
6. If on main/trunk, create or switch to the first PR branch using the detected workflow

**Never hardcode `gt` or `git town`** — detect the client first.

## Step 4: Choose Route

After worktree and stack are ready, choose which execution route to follow:

**Subagent route** — recommended when tasks are mostly independent:
- Fresh subagent per task + two-stage review (spec compliance → code quality)
- Coordinator preserves context; subagents get isolated, focused context
- Load and follow: `references/subagent-route.md`

**Main route** — when tasks are tightly coupled or sequential:
- Single-agent sequential execution with per-step verification
- Better when step N+1 depends directly on step N's output
- Load and follow: `references/main-route.md`

**Deciding:**
- Tasks touch different files/modules with minimal overlap → **subagent route**
- Tasks build on each other (output of N = input of N+1) → **main route**
- Subagents unavailable on this platform → **main route**
- Unsure → recommend subagent route and confirm with user

**Never start implementation on main/master without explicit user consent.**
