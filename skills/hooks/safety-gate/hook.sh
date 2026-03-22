#!/usr/bin/env bash
# hook: safety-gate
# trigger: PreToolUse
# status: stub — full implementation coming in a later phase
#
# Purpose: Block tool invocations until safety documentation has been
# loaded into the session context. Ensures the agent has read relevant
# safety guidelines before performing potentially destructive actions.

set -euo pipefail

echo "[safety-gate] Hook triggered (stub)"
echo "[safety-gate] TODO: Check if safety docs have been loaded this session"
echo "[safety-gate] TODO: Block destructive tools if safety context is missing"
echo "[safety-gate] TODO: Return allow once safety docs are confirmed loaded"

exit 0
