#!/usr/bin/env bash
# hook: pr-workflow
# trigger: PreToolUse (gh pr create)
# status: stub — full implementation coming in a later phase
#
# Purpose: Block `gh pr create` unless the pr-push skill was used.
# Ensures PRs are always created through the controlled workflow.

set -euo pipefail

echo "[pr-workflow] Hook triggered (stub)"
echo "[pr-workflow] TODO: Check if pr-push skill is the active caller"
echo "[pr-workflow] TODO: Block direct gh pr create if not"

exit 0
