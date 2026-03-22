#!/usr/bin/env bash
# hook: tool-miss
# trigger: PostToolUse (Bash — non-zero exit)
# status: stub — full implementation coming in a later phase
#
# Purpose: Detect command-not-found errors from Bash tool invocations
# and suggest installing the missing tool or using an alternative.

set -euo pipefail

echo "[tool-miss] Hook triggered (stub)"
echo "[tool-miss] TODO: Parse stderr for 'command not found' patterns"
echo "[tool-miss] TODO: Suggest install command or alternative tool"

exit 0
