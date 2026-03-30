#!/bin/bash
set -e

# Agentic Engineering Skills Installer
#
# Installs and updates the AX Stack skills for your coding agents.
# Detects all installed agents, manages dependencies, and verifies health.
#
# Usage:
#   ./install.sh                        # Interactive (or re-use saved settings)
#   ./install.sh --agent claude          # Force single agent
#   ./install.sh --prefix myco           # Prefix skills (myco-plan, myco-review, etc.)
#   ./install.sh --no-prefix             # No prefix
#   ./install.sh --reset                 # Reset saved settings and re-prompt
#   ./install.sh --check                 # Verify installation health (no changes)

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
CONFIG_DIR="$HOME/.agentic-eng"
CONFIG_FILE="$CONFIG_DIR/install-config"
AGENT=""
PREFIX=""
PREFIX_SET=false
RESET=false
CHECK_ONLY=false

# ── Colors & symbols ──────────────────────────────────────────────

BOLD="\033[1m"
DIM="\033[2m"
RED="\033[31m"
GREEN="\033[32m"
YELLOW="\033[33m"
BLUE="\033[34m"
CYAN="\033[36m"
RESET_COLOR="\033[0m"

OK="${GREEN}✓${RESET_COLOR}"
FAIL="${RED}✗${RESET_COLOR}"
WARN="${YELLOW}!${RESET_COLOR}"
ARROW="${CYAN}→${RESET_COLOR}"
BULLET="${DIM}•${RESET_COLOR}"

# ── Output helpers ────────────────────────────────────────────────

banner() {
  local text="$1"
  local width=48
  local padding=$(( (width - ${#text}) / 2 ))
  local pad_str=$(printf '%*s' "$padding" '')
  echo ""
  echo -e "${CYAN}╔$(printf '═%.0s' $(seq 1 $width))╗${RESET_COLOR}"
  echo -e "${CYAN}║${RESET_COLOR}${BOLD}${pad_str}${text}${pad_str}$([ $(( (width - ${#text}) % 2 )) -eq 1 ] && echo ' ')${RESET_COLOR}${CYAN}║${RESET_COLOR}"
  echo -e "${CYAN}╚$(printf '═%.0s' $(seq 1 $width))╝${RESET_COLOR}"
  echo ""
}

section() {
  echo ""
  echo -e "${ARROW} ${BOLD}$1${RESET_COLOR}"
}

ok()   { echo -e "    ${OK} $1"; }
warn() { echo -e "    ${WARN} $1"; }
fail() { echo -e "    ${FAIL} $1"; }
info() { echo -e "    ${BULLET} $1"; }

# ── Parse arguments ───────────────────────────────────────────────

while [[ $# -gt 0 ]]; do
  case $1 in
    --agent) AGENT="$2"; shift 2 ;;
    --prefix) PREFIX="$2"; PREFIX_SET=true; shift 2 ;;
    --no-prefix) PREFIX=""; PREFIX_SET=true; shift ;;
    --reset) RESET=true; shift ;;
    --check) CHECK_ONLY=true; shift ;;
    -h|--help)
      echo "Usage: ./install.sh [OPTIONS]"
      echo ""
      echo "Options:"
      echo "  --agent <claude|cursor|codex>  Force single agent (default: detect all)"
      echo "  --prefix <name>                Prefix skill names (e.g., myco → myco-plan)"
      echo "  --no-prefix                    No prefix on skill names"
      echo "  --reset                        Reset saved settings and re-prompt"
      echo "  --check                        Verify installation health (no changes)"
      echo "  -h, --help                     Show this help"
      exit 0
      ;;
    *) echo "Unknown argument: $1"; exit 1 ;;
  esac
done

# ── Load saved settings ──────────────────────────────────────────

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

# ── Skill catalog ────────────────────────────────────────────────

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

HOOK_DIRS=(
  "hooks/session-compound"
  "hooks/pr-workflow"
  "hooks/tool-miss"
  "hooks/safety-gate"
  "hooks/permission-analyzer"
)

apply_prefix() {
  local name="$1"
  if [ -n "$PREFIX" ]; then
    echo "${PREFIX}-${name}"
  else
    echo "$name"
  fi
}

# ── Banner ────────────────────────────────────────────────────────

if [ "$CHECK_ONLY" = true ]; then
  banner "AX Stack — Health Check"
else
  if [ "$SAVED" = true ]; then
    banner "AX Stack — Update"
  else
    banner "AX Stack — Install"
  fi
fi

# ── Pull latest (if in a git repo) ───────────────────────────────

if [ "$CHECK_ONLY" = false ] && git -C "$REPO_DIR" rev-parse --is-inside-work-tree &>/dev/null; then
  section "Pulling latest changes..."
  PULL_OUTPUT=$(git -C "$REPO_DIR" pull 2>&1) || true
  if echo "$PULL_OUTPUT" | grep -q "Already up to date"; then
    ok "Already up to date"
  elif echo "$PULL_OUTPUT" | grep -q "Updating"; then
    ok "Updated to latest version"
  else
    info "$PULL_OUTPUT"
  fi
fi

# ── Detect agents ────────────────────────────────────────────────

section "Detecting coding agents..."

AGENTS_FOUND=()

if command -v claude &>/dev/null; then
  CLAUDE_VERSION=$(claude --version 2>/dev/null | head -1 || echo "installed")
  ok "Claude Code ($CLAUDE_VERSION)"
  AGENTS_FOUND+=("claude")
else
  info "Claude Code — not found"
fi

if [ -d "$HOME/.cursor" ] || command -v cursor &>/dev/null; then
  ok "Cursor"
  AGENTS_FOUND+=("cursor")
else
  info "Cursor — not found"
fi

if command -v codex &>/dev/null; then
  ok "Codex"
  AGENTS_FOUND+=("codex")
else
  info "Codex — not found"
fi

if [ ${#AGENTS_FOUND[@]} -eq 0 ]; then
  fail "No coding agents detected"
  echo ""
  echo -e "    Install one of: Claude Code, Cursor, or Codex"
  echo -e "    Then re-run this script."
  exit 1
fi

# If --agent was specified, filter to just that one
if [ -n "$AGENT" ]; then
  AGENTS_FOUND=("$AGENT")
fi

# ── Ask about prefix (if not set) ────────────────────────────────

if [ "$PREFIX_SET" = false ] && [ "$CHECK_ONLY" = false ]; then
  section "Skill prefix (optional)"
  info "Skills are named: plan, review, compound, etc."
  info "A prefix like 'myco' makes them: myco-plan, myco-review, etc."
  info "Useful to avoid conflicts with other skills."
  echo ""
  read -p "    Prefix (leave empty for none): " PREFIX
  PREFIX_SET=true
fi

# ── Save settings ────────────────────────────────────────────────

if [ "$CHECK_ONLY" = false ]; then
  cat > "$CONFIG_FILE" << EOF
SAVED_AGENT="$AGENT"
SAVED_PREFIX="$PREFIX"
SAVED_PREFIX_SET="$PREFIX_SET"
EOF
fi

# ── Verify config directory ──────────────────────────────────────

section "Verifying config directory..."

if [ -d "$CONFIG_DIR" ]; then
  ok "Config directory exists: $CONFIG_DIR"
else
  mkdir -p "$CONFIG_DIR"
  ok "Created $CONFIG_DIR"
fi

# ── Check dependencies ───────────────────────────────────────────

section "Checking dependencies..."

DEP_ISSUES=0

# Git
if command -v git &>/dev/null; then
  GIT_VERSION=$(git --version 2>/dev/null | sed 's/git version //')
  ok "git $GIT_VERSION"
else
  fail "git not found"
  DEP_ISSUES=$((DEP_ISSUES + 1))
fi

# Python (for KB server)
if command -v python3 &>/dev/null; then
  PY_VERSION=$(python3 --version 2>/dev/null | sed 's/Python //')
  ok "python3 $PY_VERSION"
else
  warn "python3 not found (needed for KB server)"
fi

# Docker (optional, for team deployment)
if command -v docker &>/dev/null; then
  DOCKER_VERSION=$(docker --version 2>/dev/null | sed 's/Docker version //' | cut -d',' -f1)
  ok "docker $DOCKER_VERSION"
else
  info "docker not found (optional — needed for team KB deployment)"
fi

# GitHub CLI
if command -v gh &>/dev/null; then
  GH_VERSION=$(gh --version 2>/dev/null | head -1 | sed 's/gh version //' | cut -d' ' -f1)
  ok "gh $GH_VERSION"
else
  warn "gh CLI not found (needed for PR skills)"
fi

# jq (used by hooks)
if command -v jq &>/dev/null; then
  ok "jq $(jq --version 2>/dev/null | sed 's/jq-//')"
else
  warn "jq not found (needed for hooks)"
fi

if [ $DEP_ISSUES -gt 0 ]; then
  fail "$DEP_ISSUES required dependency missing"
  exit 1
fi

# ── Verify KB server Python environment ──────────────────────────

KB_DIR="$REPO_DIR/apps/kb-server"
if [ -d "$KB_DIR" ]; then
  section "Verifying KB server environment..."

  VENV_DIR="$KB_DIR/.venv"
  if [ -d "$VENV_DIR" ] && [ -f "$VENV_DIR/bin/python" ]; then
    ok "Python venv exists: $VENV_DIR"
    # Quick sanity check — can it import the server?
    if "$VENV_DIR/bin/python" -c "import src.server" 2>/dev/null; then
      ok "KB server module importable"
    else
      warn "KB server dependencies may need install: cd apps/kb-server && pip install -e ."
    fi
  else
    info "No venv found — run: cd apps/kb-server && python -m venv .venv && pip install -e ."
  fi

  # Check if KB server is running
  if curl -sf http://localhost:8080/health &>/dev/null; then
    ok "KB server is running (localhost:8080)"
  else
    info "KB server is not running (start with: cd apps/kb-server && python -m src.server)"
  fi
fi

# ── Install skills ───────────────────────────────────────────────

install_for_agent() {
  local agent="$1"
  local skills_dir=""
  local use_symlinks="true"
  local label=""

  case "$agent" in
    claude)
      skills_dir="$HOME/.claude/skills"
      label="Claude Code"
      ;;
    cursor)
      skills_dir="$HOME/.cursor/skills"
      use_symlinks="false"
      label="Cursor"
      ;;
    codex)
      skills_dir="$HOME/.codex/skills"
      label="Codex"
      ;;
    *)
      fail "Unknown agent: $agent"
      return 1
      ;;
  esac

  section "Installing skills → $label"

  if [ "$use_symlinks" = "false" ]; then
    info "Using copies (${label} doesn't follow symlinks)"
  fi

  mkdir -p "$skills_dir"

  local installed=0
  local updated=0
  local unchanged=0

  for skill_path in "${SKILL_DIRS[@]}"; do
    local base_name=$(basename "$skill_path")
    local skill_name=$(apply_prefix "$base_name")
    local source="$SCRIPT_DIR/$skill_path"
    local target="$skills_dir/$skill_name"

    if [ ! -d "$source" ]; then
      warn "$skill_name — source not found, skipping"
      continue
    fi

    if [ -L "$target" ]; then
      # Symlink exists — check if it points to the right place
      local current_target=$(readlink "$target" 2>/dev/null || true)
      if [ "$current_target" = "$source" ]; then
        unchanged=$((unchanged + 1))
        continue
      else
        rm "$target"
        ln -s "$source" "$target"
        updated=$((updated + 1))
        continue
      fi
    elif [ -d "$target" ]; then
      if [ "$use_symlinks" = "true" ]; then
        # Was a copy, should be a symlink — upgrade
        rm -rf "$target"
        ln -s "$source" "$target"
        updated=$((updated + 1))
      else
        # Copy mode — refresh
        rm -rf "$target"
        cp -r "$source" "$target"
        updated=$((updated + 1))
      fi
      continue
    fi

    # Fresh install
    if [ "$use_symlinks" = "true" ]; then
      ln -s "$source" "$target"
    else
      cp -r "$source" "$target"
    fi
    installed=$((installed + 1))
  done

  if [ $installed -gt 0 ]; then
    ok "Installed $installed new skills"
  fi
  if [ $updated -gt 0 ]; then
    ok "Updated $updated skills"
  fi
  if [ $unchanged -gt 0 ] && [ $installed -eq 0 ] && [ $updated -eq 0 ]; then
    ok "All ${#SKILL_DIRS[@]} skills up to date"
  fi

  # Count hooks
  local hooks_available=0
  for hook_path in "${HOOK_DIRS[@]}"; do
    if [ -d "$SCRIPT_DIR/$hook_path" ]; then
      hooks_available=$((hooks_available + 1))
    fi
  done
  info "$hooks_available hooks available (copy from skills/hooks/ to your agent config)"
}

if [ "$CHECK_ONLY" = false ]; then
  for agent in "${AGENTS_FOUND[@]}"; do
    install_for_agent "$agent"
  done
fi

# ── Health check (always runs) ───────────────────────────────────

if [ "$CHECK_ONLY" = true ]; then
  section "Checking skill installations..."

  for agent in "${AGENTS_FOUND[@]}"; do
    check_dir=""
    case "$agent" in
      claude) check_dir="$HOME/.claude/skills" ;;
      cursor) check_dir="$HOME/.cursor/skills" ;;
      codex) check_dir="$HOME/.codex/skills" ;;
    esac

    if [ ! -d "$check_dir" ]; then
      warn "$agent: skills directory not found"
      continue
    fi

    count=0
    broken=0
    for skill_path in "${SKILL_DIRS[@]}"; do
      base_name=$(basename "$skill_path")
      skill_name=$(apply_prefix "$base_name")
      target="$check_dir/$skill_name"

      if [ -L "$target" ]; then
        if [ -e "$target" ]; then
          count=$((count + 1))
        else
          fail "$agent: broken symlink → $skill_name"
          broken=$((broken + 1))
        fi
      elif [ -d "$target" ]; then
        count=$((count + 1))
      fi
    done

    if [ $broken -eq 0 ]; then
      ok "$agent: $count/${#SKILL_DIRS[@]} skills installed"
    else
      warn "$agent: $count installed, $broken broken"
    fi
  done
fi

# ── Summary ──────────────────────────────────────────────────────

banner "$([ "$CHECK_ONLY" = true ] && echo "Health Check Complete" || echo "Installation Complete")"

echo -e "  ${BOLD}Configuration${RESET_COLOR}"
echo -e "    Settings    ${DIM}$CONFIG_FILE${RESET_COLOR}"
echo -e "    Config      ${DIM}$CONFIG_DIR${RESET_COLOR}"
echo -e "    Toolkit     ${DIM}$REPO_DIR${RESET_COLOR}"
if [ -n "$PREFIX" ]; then
  echo -e "    Prefix      ${DIM}$PREFIX${RESET_COLOR}"
fi
echo ""

echo -e "  ${BOLD}Agents${RESET_COLOR}"
for agent in "${AGENTS_FOUND[@]}"; do
  case "$agent" in
    claude) echo -e "    ${OK} Claude Code   ${DIM}$HOME/.claude/skills${RESET_COLOR}" ;;
    cursor) echo -e "    ${OK} Cursor        ${DIM}$HOME/.cursor/skills${RESET_COLOR}" ;;
    codex)  echo -e "    ${OK} Codex         ${DIM}$HOME/.codex/skills${RESET_COLOR}" ;;
  esac
done
echo ""

if [ "$CHECK_ONLY" = false ]; then
  echo -e "  ${BOLD}What's next${RESET_COLOR}"
  echo -e "    1. Open your project repo"
  if [ -n "$PREFIX" ]; then
    echo -e "    2. Run ${CYAN}/${PREFIX}-setup${RESET_COLOR} for guided configuration"
    echo -e "    3. Try  ${CYAN}/${PREFIX}-brainstorm${RESET_COLOR} on a feature"
  else
    echo -e "    2. Run ${CYAN}/setup${RESET_COLOR} for guided configuration"
    echo -e "    3. Try  ${CYAN}/brainstorm${RESET_COLOR} on a feature"
  fi
  echo ""

  echo -e "  ${DIM}Note for Cursor users:${RESET_COLOR}"
  echo -e "  ${DIM}  Skills are copied (not symlinked). Re-run install.sh after updates.${RESET_COLOR}"
  echo ""
fi
