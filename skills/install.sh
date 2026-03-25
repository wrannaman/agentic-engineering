#!/bin/bash
set -e

# Agentic Engineering Skills Installer
#
# Interactive installer with prefix support and memory.
# Remembers your settings between runs.
#
# Usage:
#   ./install.sh                        # Interactive (or re-use saved settings)
#   ./install.sh --agent claude          # Force agent
#   ./install.sh --prefix myco           # Force prefix (skills become myco-plan, myco-review, etc.)
#   ./install.sh --no-prefix             # Force no prefix
#   ./install.sh --reset                 # Reset saved settings and re-prompt

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CONFIG_DIR="$HOME/.agentic-eng"
CONFIG_FILE="$CONFIG_DIR/install-config"
AGENT=""
PREFIX=""
PREFIX_SET=false
RESET=false

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --agent) AGENT="$2"; shift 2 ;;
    --prefix) PREFIX="$2"; PREFIX_SET=true; shift 2 ;;
    --no-prefix) PREFIX=""; PREFIX_SET=true; shift ;;
    --reset) RESET=true; shift ;;
    -h|--help)
      echo "Usage: ./install.sh [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --agent <claude|cursor|codex>  Force agent type"
      echo "  --prefix <name>                Prefix skill names (e.g., myco → myco-plan)"
      echo "  --no-prefix                    No prefix on skill names"
      echo "  --reset                        Reset saved settings"
      echo "  -h, --help                     Show this help"
      exit 0
      ;;
    *) echo "Unknown argument: $1"; exit 1 ;;
  esac
done

# Load saved settings (if they exist and we're not resetting)
mkdir -p "$CONFIG_DIR"
if [ "$RESET" = true ] && [ -f "$CONFIG_FILE" ]; then
  rm "$CONFIG_FILE"
  echo "Settings reset."
fi

if [ -f "$CONFIG_FILE" ]; then
  source "$CONFIG_FILE"
  SAVED=true
else
  SAVED=false
fi

# Use saved values as defaults (CLI args override)
[ -z "$AGENT" ] && AGENT="${SAVED_AGENT:-}"
[ "$PREFIX_SET" = false ] && PREFIX="${SAVED_PREFIX:-}" && PREFIX_SET="${SAVED_PREFIX_SET:-false}"

# --- Auto-detect agent if not set ---
if [ -z "$AGENT" ]; then
  if command -v claude &> /dev/null; then
    DETECTED="claude"
  elif [ -d "$HOME/.cursor" ]; then
    DETECTED="cursor"
  elif command -v codex &> /dev/null; then
    DETECTED="codex"
  else
    DETECTED=""
  fi

  if [ -n "$DETECTED" ]; then
    echo "Detected agent: $DETECTED"
    read -p "Use $DETECTED? [Y/n] " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Nn]$ ]]; then
      read -p "Agent (claude/cursor/codex): " AGENT
    else
      AGENT="$DETECTED"
    fi
  else
    read -p "Agent (claude/cursor/codex): " AGENT
  fi
fi

# --- Ask about prefix if not set ---
if [ "$PREFIX_SET" = false ]; then
  echo ""
  echo "Skill prefix (optional):"
  echo "  Skills are named: plan, review, compound, etc."
  echo "  With a prefix like 'myco', they become: myco-plan, myco-review, myco-compound"
  echo "  This avoids conflicts if you have other skills with the same names."
  echo ""
  read -p "Prefix (leave empty for no prefix): " PREFIX
  PREFIX_SET=true
fi

# --- Save settings for next run ---
cat > "$CONFIG_FILE" << EOF
SAVED_AGENT="$AGENT"
SAVED_PREFIX="$PREFIX"
SAVED_PREFIX_SET="$PREFIX_SET"
EOF

echo ""
echo "=== Agentic Engineering Skills Installer ==="
echo "Agent: $AGENT"
if [ -n "$PREFIX" ]; then
  echo "Prefix: $PREFIX (skills will be ${PREFIX}-plan, ${PREFIX}-review, etc.)"
else
  echo "Prefix: none"
fi
echo ""

# Skill directories
SKILL_DIRS=(
  "core/setup"
  "core/seed"
  "core/brainstorm"
  "core/plan"
  "core/work"
  "core/review"
  "core/compound"
  "core/debug"
  "core/ship"
  "git/stack-pr"
  "git/pr-push"
  "git/worktree"
  "git/rebase-fix"
  "git/git-cleanup"
  "quality/deslop"
  "quality/simplify"
  "quality/github-review"
  "analysis/gh-summary"
  "analysis/spec"
  "analysis/adversarial"
)

apply_prefix() {
  local name="$1"
  if [ -n "$PREFIX" ]; then
    echo "${PREFIX}-${name}"
  else
    echo "$name"
  fi
}

install_skills() {
  local skills_dir="$1"
  local use_symlinks="$2"  # "true" for symlinks, "false" for copy

  mkdir -p "$skills_dir"

  local installed=0
  local skipped=0

  for skill_path in "${SKILL_DIRS[@]}"; do
    local base_name=$(basename "$skill_path")
    local skill_name=$(apply_prefix "$base_name")
    local source="$SCRIPT_DIR/$skill_path"
    local target="$skills_dir/$skill_name"

    if [ -L "$target" ] || [ -d "$target" ]; then
      echo "  [skip] $skill_name (already installed)"
      skipped=$((skipped + 1))
    else
      if [ "$use_symlinks" = "true" ]; then
        ln -s "$source" "$target"
      else
        cp -r "$source" "$target"
      fi
      echo "  [installed] $skill_name"
      installed=$((installed + 1))
    fi
  done

  echo ""
  echo "Installed: $installed, Skipped: $skipped"
  echo "Skills directory: $skills_dir"
}

case "$AGENT" in
  claude)
    echo "Installing for Claude Code (symlinks)..."
    install_skills "$HOME/.claude/skills" "true"
    echo "Restart Claude Code to load new skills."
    ;;
  cursor)
    echo "Installing for Cursor (copies — Cursor doesn't follow symlinks)..."
    install_skills "$HOME/.cursor/skills" "false"
    echo "Restart Cursor to load new skills."
    ;;
  codex)
    echo "Installing for Codex (symlinks)..."
    install_skills "$HOME/.codex/skills" "true"
    ;;
  *)
    echo "Unknown agent: $AGENT"
    exit 1
    ;;
esac

echo ""
echo "=== Installation complete ==="
echo ""
echo "Settings saved to $CONFIG_FILE"
echo "Run with --reset to change settings."
echo ""
echo "Next steps:"
echo "  1. Configure your project's CLAUDE.md or AGENTS.md (see templates/)"
echo "  2. Configure MCP connection to your KB server (see templates/.mcp.json.template)"
if [ -n "$PREFIX" ]; then
  echo "  3. Try: /${PREFIX}-brainstorm <your first feature>"
else
  echo "  3. Try: /brainstorm <your first feature>"
fi
