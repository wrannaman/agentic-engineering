---
name: worktree
description: List and create git worktrees with gtr
version: 1.0.0
---

# Worktree Management

List and create git worktrees using [gtr (git-worktree-runner)](https://github.com/coderabbitai/git-worktree-runner). Complements `/git-cleanup` to provide full worktree lifecycle: **create → list/manage → cleanup**.

## When to Use

- Starting a new workstream and want branch isolation, then continuing work in the same session
- Creating a worktree and immediately executing a plan there (most common)
- Working on multiple features in parallel
- Checking what worktrees exist and their PR status
- Creating a worktree mid-session after realizing you need isolation

## Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `list` | (default) | List all worktrees with PR status and last commit |
| `create <branch>` | — | Create a new worktree for the given branch |
| `create <branch> --from-current` | — | Create a worktree branching from the current branch |

## Process

### Command: `list` (default, no arguments)

1. **Get worktree list:**
   ```bash
   git gtr list
   ```

2. **Enrich each worktree** with PR status and last commit:
   ```bash
   # For each branch in the worktree list:
   gh pr list --head <branch> --state open --json number,title,url --limit 1
   git log -1 --format='%h %s (%cr)' <branch>
   ```

3. **Display as a table:**
   ```
   ## Worktrees

   | Path | Branch | PR | Last Commit |
   |------|--------|----|-------------|
   | ~/projects/myapp | main | — | abc1234 fix typo (2 hours ago) |
   | ~/projects/myapp-feat-auth | feat/auth | #42 Add OAuth | def5678 add token refresh (1 day ago) |
   | ~/projects/myapp-fix-bug | fix/login-bug | — | ghi9012 debug login (3 days ago) |
   ```

### Command: `create <branch-name>`

1. **If no branch name provided**, ask for one using AskUserQuestion.

2. **Preflight: ensure worktrees are stored inside the repo.**
   Worktrees MUST be inside the repo so they stay within Claude Code's sandbox. Check and fix before creating:
   ```bash
   git gtr config get gtr.worktrees.dir
   ```
   - **If it returns `.worktrees`** → proceed to step 3.
   - **If it returns anything else or is empty** → configure it:
     ```bash
     # Add [worktrees] dir = .worktrees to .gtrconfig (create if missing)
     # If .gtrconfig doesn't exist:
     printf '[worktrees]\n  dir = .worktrees\n' > .gtrconfig
     # If .gtrconfig exists but has no [worktrees] section:
     # prepend the section before existing content

     # Ensure .worktrees/ is in .gitignore
     grep -qxF '/.worktrees/' .gitignore 2>/dev/null || echo '/.worktrees/' >> .gitignore
     ```
     Tell the user: "Configured this repo to store worktrees in `.worktrees/` (inside the repo) so Claude Code can access them without permission prompts."

3. **Create the worktree:**
   ```bash
   git gtr new <branch-name>
   ```

4. **Get the worktree path and switch to it:**
   ```bash
   cd "$(git gtr go <branch-name>)"
   ```

5. **Copy plan files into the worktree.** Plans live in `.claude/plans/` which is gitignored, so gtr won't copy them automatically. Copy the directory from the source repo:
   ```bash
   cp -r <source-repo>/.claude/plans/ <worktree-path>/.claude/plans/
   ```
   - Create `.claude/` in the worktree first if it doesn't exist
   - If the source repo has no `.claude/plans/` directory, skip this step
   - This ensures `/work` can find referenced plan files

6. **Report the result and continue:**
   ```
   Worktree created at `/path/to/worktree`. Now working there.

   ```

7. **If the user provided a plan or task**, immediately begin executing it in the worktree directory. Do not wait for further prompting.

### Command: `create <branch-name> --from-current`

1. **Run step 2 (preflight) from the `create` command above** to ensure `gtr.worktrees.dir` is set.

2. **Create the worktree branching from current branch:**
   ```bash
   git gtr new <branch-name> --from-current
   ```

3. **Then follow steps 4-7 above** (switch, copy plans, report, continue).

This is useful when you've started work on a branch and want to create a parallel worktree from that point.

## .gtrconfig Setup

Each repo should have a `.gtrconfig` file checked in. It configures worktree storage and file copying.

**Example `.gtrconfig`:**
```ini
[worktrees]
  dir = .worktrees

[copy]
  include = .secrets/**
  include = .env
  include = .env.local
  include = .infisical.json
```

**Personal preferences** (editor, AI tool) should be set per-machine, not checked in:
```bash
git config --local gtr.editor.default cursor
git config --local gtr.ai.default claude
```

See `templates/gtrconfig.example` in the toolkit for a starting template.

## Quick Reference: Common gtr Commands

These commands work directly — no need to go through this skill:

| Command | Description |
|---------|-------------|
| `git gtr new <branch>` | Create worktree |
| `git gtr new <branch> --from-current` | Create worktree from current branch |
| `git gtr list` | List all worktrees |
| `git gtr go <branch>` | Print worktree path (use with `cd`) |
| `git gtr ai <branch>` | Launch Claude in a worktree |
| `git gtr ai <branch> -- --continue` | Resume Claude session in a worktree |
| `git gtr rm <branch>` | Remove a worktree |
| `git gtr clean --merged` | Remove worktrees for merged PRs |
| `git gtr doctor` | Health check |

## Relationship to Other Skills

- **`/plan`** — Has a worktree pre-flight check (Step -1) that suggests creating a worktree when you're on main
- **`/git-cleanup`** — Cleans up old worktrees and branches (the "cleanup" half of the lifecycle)
- **`/work`** — Executes plans; worktrees should be set up before this phase

## Tips

- **Default: stay in the same session.** After creating a worktree, use its absolute path for all subsequent commands. This lets the user monitor progress directly without switching contexts.
- **Use `git gtr ai <branch>` only if user asks for true parallel isolation** — a separate Claude session running independently (e.g. two features in flight at the same time).
- Use `git gtr ai <branch> -- --continue` to resume an existing session in a worktree.
- The `--from-current` flag is handy when you realize mid-work that you should be on a separate branch.
- gtr automatically copies files matching your `.gtrconfig` patterns — no manual copying needed.
- Run `git gtr doctor` if something isn't working to check your setup.

## Error Handling

### gtr not installed

```
gtr is not installed. Run the toolkit installer:
  cd <toolkit-dir> && ./install.sh
```

### No .gtrconfig in repo

```
No .gtrconfig found. New worktrees won't copy gitignored files.
Create one from the toolkit template:
  cp <toolkit-dir>/templates/gtrconfig.example .gtrconfig
```

### Branch already exists

gtr will report an error if the branch already exists. Either:
- Use a different branch name
- Use `git gtr new <branch> --force --name <suffix>` to create a parallel worktree

## Example Session

```
User: /worktree

Agent: ## Worktrees

| Path | Branch | PR | Last Commit |
|------|--------|----|-------------|
| ~/projects/backend-net | main | — | ed04d1f Merge PR #54 (2 hours ago) |
| ~/projects/backend-net/.worktrees/feat-oauth | feat/oauth | #55 Add OAuth support | a1b2c3d add token validation (1 day ago) |

2 worktrees found.

---

User: /worktree create feat/new-api

Agent: Worktree created at `/home/nm/projects/backend-net/.worktrees/feat-new-api`. Now working there.

---

User: /worktree create feat/new-api, then execute the plan at .claude/plans/2026-02-19-new-api.md

Agent: Worktree created at `/home/nm/projects/backend-net/.worktrees/feat-new-api`. Now working there.

Executing plan...
[continues working in worktree without switching sessions]
```
