# Slack Trigger

A Slack bot/workflow that lets non-engineers create PRs from Slack.

## Flow

```
User in Slack: "/ship fix the header color on /pricing"
    → Bot creates a GitHub Codespace
    → Runs coding agent with the user's prompt
    → Agent executes: brainstorm → plan → work → review
    → Bot posts back: "Draft PR created: <link>"
    → Engineer reviews and merges
```

## Implementation Options

### Option 1: Slack Workflow + GitHub Actions

Use Slack's built-in Workflow Builder to trigger a GitHub Actions workflow:
1. Slack workflow captures the request text
2. Sends webhook to GitHub Actions
3. Action creates a Codespace and runs the agent
4. Posts result back to Slack

### Option 2: Custom Slack Bot

Build a lightweight bot (Node.js or Python) that:
1. Listens for slash commands
2. Calls GitHub API to create Codespaces
3. Monitors the agent's progress
4. Posts PR link when done

### Option 3: GitHub Copilot Chat in Slack

If your org uses GitHub Copilot, it can be integrated directly into Slack.

## Sample Configs

See `configs/` for sample Slack app manifests and workflow configurations.

## Guardrails

- All PRs created this way are **draft** by default
- All PRs require engineer review before merge
- CI runs on all PRs regardless of author
