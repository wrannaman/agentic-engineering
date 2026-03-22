# GitHub Codespaces Configuration

Pre-configured development environment for the "anyone can ship" workflow.

## What This Does

Gives designers, PMs, and non-engineers a one-click development environment with:
- Skills pre-installed
- MCP connected to the knowledge base
- Agent runtime ready

## Usage

1. Copy `.devcontainer/` into your project repo
2. Customize `devcontainer.json` for your project's dependencies
3. Set repository secrets for `KB_AUTH_TOKEN` and `KB_SERVER_URL`
4. Non-engineers open a Codespace and start working

## Files

- `.devcontainer/devcontainer.json` — Container configuration
- `.devcontainer/post-create.sh` — Installs skills, configures MCP connection
