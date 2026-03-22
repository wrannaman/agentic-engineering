# Hooks: The Enforcement Layer

Skills are suggestions. Hooks are gates.

Skills guide the agent through workflows. But nothing stops the agent from skipping a skill. Hooks intercept agent lifecycle events and enforce the workflow.

## Available Hooks

| Hook | Event | What It Does |
|------|-------|-------------|
| **session-compound** | SessionEnd | Analyzes transcript with lightweight LLM. Classifies gaps. Posts to Slack with pre-filled issue URL. |
| **pr-workflow** | PreToolUse | Intercepts `gh pr create`. Blocks unless the PR skill was activated first. |
| **tool-miss** | PostToolUse | Detects "command not found" errors. Suggests fix. Updates agent config. |
| **permission-analyzer** | PermissionRequest | After N prompts, analyzes session history. Writes evidence-based safe defaults. |
| **safety-gate** | PreToolUse | Blocks production/admin tools until agent has loaded safety docs from KB. |

## Installation

Hooks are configured in your agent's settings. For Claude Code:

```json
// ~/.claude/settings.json
{
  "hooks": {
    "SessionEnd": ["path/to/session-compound/hook.sh"],
    "PreToolUse": ["path/to/pr-workflow/hook.sh", "path/to/safety-gate/hook.sh"],
    "PostToolUse": ["path/to/tool-miss/hook.sh"]
  }
}
```

## Why Hooks Matter

- They close the gap between "the agent should do X" and "the agent MUST do X"
- They make non-engineer usage safe
- They generate telemetry that feeds the compound loop
- They're composable — add hooks for your team's specific guardrails

## Inspired By

[Intercom's Claude Code plugin system](http://x.com/brian_scanlan/status/2033978300003987527?s=20) — 13 plugins, 100+ skills, hooks as the enforcement layer.
