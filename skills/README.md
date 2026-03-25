# Skills

Agent skills that guide coding agents through structured workflows.

## Installation

```bash
./install.sh
```

The installer detects your coding agent (Claude Code, Cursor, Codex) and installs skills into the appropriate directory.

## Skill Catalog

### Core Workflow

The essential cycle. Every feature goes through this.

| Skill | Purpose | When to Use |
|-------|---------|------------|
| [setup](core/setup/) | Interactive guided setup | First-time deployment of the whole stack |
| [seed](core/seed/) | Auto-generate KB docs from codebase | First-time KB seeding (cold start killer) |
| [brainstorm](core/brainstorm/) | Explore unknowns | You don't know what you don't know |
| [plan](core/plan/) | Research-first design | You know what to build, not how |
| [work](core/work/) | Step-by-step implementation | You have an approved plan |
| [review](core/review/) | Multi-perspective code review | After implementation |
| [compound](core/compound/) | Extract learnings + code patterns → KB | After a feature merges |
| [debug](core/debug/) | Parallel bug investigation → diagnosis doc | You have a bug and don't know where to look |
| [ship](core/ship/) | Plan → implement → review → fix → push (one shot) | Well-scoped task, you trust the system |

### Git Workflow

| Skill | Purpose |
|-------|---------|
| [stack-pr](git/stack-pr/) | Create stacked PRs |
| [pr-push](git/pr-push/) | Create/update draft PRs with auto-fix |
| [worktree](git/worktree/) | Isolated worktree management |
| [rebase-fix](git/rebase-fix/) | Resolve merge/rebase conflicts |
| [git-cleanup](git/git-cleanup/) | Clean up stale branches and worktrees |

### Code Quality

| Skill | Purpose |
|-------|---------|
| [deslop](quality/deslop/) | Strip AI-generated slop |
| [simplify](quality/simplify/) | Reduce complexity |
| [github-review](quality/github-review/) | Address PR review comments |

### Analysis

| Skill | Purpose |
|-------|---------|
| [gh-summary](analysis/gh-summary/) | Summarize merged PRs |
| [spec](analysis/spec/) | Write design specs and ADRs |
| [adversarial](analysis/adversarial/) | Adversarial design critique |

### Hooks

| Hook | Event | Purpose |
|------|-------|---------|
| [session-compound](hooks/session-compound/) | SessionEnd | Analyze session for improvement gaps |
| [pr-workflow](hooks/pr-workflow/) | PreToolUse | Enforce PR skill before `gh pr create` |
| [tool-miss](hooks/tool-miss/) | PostToolUse | Detect command-not-found errors |
| [permission-analyzer](hooks/permission-analyzer/) | PermissionRequest | Evidence-based permission defaults |
| [safety-gate](hooks/safety-gate/) | PreToolUse | Block production tools until safety docs loaded |

## Skill Format

Each skill is a directory containing a `SKILL.md` file:

```
skill-name/
└── SKILL.md
```

The SKILL.md contains structured instructions that the coding agent follows. Skills can reference other skills (e.g., `/plan` transitions to `/work`).

## Customization

Skills are markdown. Edit any SKILL.md to customize behavior for your team. Fork a skill to create a variant.
