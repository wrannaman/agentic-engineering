# Compound Skill

You are entering the **compound phase**. You will capture learnings from this session and search past sessions for similar issues.

## Configuration

**Learnings Directory Lookup:**
1. First, check for project-local learnings at `<git-root>/.llm/learnings/`
2. If not found, fall back to `[paths.learnings_directory]` from `~/.agentic-eng/config.toml`

This allows each project to have its own learnings while maintaining backwards compatibility. New learnings should be stored in the project-local directory when available.

## Purpose

"Compound engineering" means every fix makes future work easier. This skill helps you:
1. Learn from past sessions using CASS
2. Document patterns to prevent recurring mistakes
3. Decide whether to update patterns or create hooks
4. **Optimize the workflow itself** - skills, hooks, and processes

**Core Philosophy:** Mistakes should only be made once. Every compound run must make future work:
1. **Better** - Higher quality output, fewer errors
2. **Faster** - Less manual work, more automation

## Process

**CRITICAL: Be exhaustive. The user should NOT have to prompt you for thoroughness.**

### Step 1: Identify the Feature Scope

Before searching, establish what we're analyzing:

1. **Check for a plan file** - Was this a planned feature?
   ```bash
   ls .plans/
   ```

2. **Check the git branch** - What feature is this?
   ```bash
   git branch --show-current
   ```

3. **Check git log** - What commits are part of this feature?
   ```bash
   git log main..HEAD --oneline
   ```

4. **Check git diff for structural changes** - Did files move/reorganize?
   ```bash
   git diff main --stat
   git diff main --name-status | grep -E "^R|^D"  # Renames and deletes
   ```

**Output:** Feature name, plan file (if any), branch name, key files involved.

### Step 2: Find ALL Related Sessions (EXHAUSTIVE)

Re-index and search MULTIPLE ways:

```bash
cass index
```

**Search by ALL of these** (not just one):

1. **Plan name** (if exists):
   ```bash
   cass search "[plan-file-name]" --limit 10
   ```

2. **Branch name**:
   ```bash
   cass search "[branch-name]" --limit 10
   ```

3. **Key type/class names** from git diff:
   ```bash
   cass search "[MainClassName]" --limit 10
   ```

4. **Feature keywords**:
   ```bash
   cass search "[feature-description-keywords]" --limit 10
   ```

**Collect ALL unique session IDs** from these searches. You should typically find 3-8 related sessions for any non-trivial feature.

### Step 3: Analyze User Corrections (CRITICAL)

**For EACH related session**, search for user corrections:

```bash
# Extract user messages and look for correction patterns
cat [session-file].jsonl | jq -r 'select(.type == "user") | .message.content' | \
  grep -i -E "no,|actually|don't|stop|wrong|wait|instead|should be|not what|fix|redo|revert|mistake"
```

**Correction patterns to look for:**
- "no," / "actually" / "wait" - User correcting direction
- "don't" / "stop" / "DO NOT" - User preventing action
- "should be" / "instead" - User specifying correct approach
- "why" / "confused" - User asking for explanation (not implementation)
- Expletives ("fuck", "damn") - User frustrated with mistake

**Document EVERY correction found** - these are the most valuable learnings.

### Step 3.5: Analyze GitHub Review Feedback

**If `/github-review` was run during this session, extract learnings from the PR review comments.**

GitHub review comments are a rich source of patterns that often get missed because they come from external reviewers (humans or bots), not user chat corrections.

**1. Find review sessions in transcript:**

Look for GraphQL queries that fetched `reviewThreads` and the fixes applied:
```bash
# Search for github-review skill invocations
cass search "reviewThreads" --limit 5
cass search "github-review" --limit 5
```

**2. For each review comment that required a fix, document:**
- What was the issue?
- What pattern/gotcha does this reveal?
- Should this be documented?

**3. Categorize review feedback:**

| Category | Example | Action |
|----------|---------|--------|
| Threading/concurrency | "DbContext concurrent access" | Add to gotchas |
| Logging patterns | "Use Log.Here() for call-site" | Add to lang-patterns |
| API design | "Remove unused parameter" | Add to code-patterns |
| Performance | "Duration tracking lost" | Add to gotchas |
| Code style | "Prefer early return" | Add to lang-patterns |
| Security | "Validate input before use" | Add to gotchas |

**4. Create learnings for recurring review feedback:**

If the same type of comment appears across multiple PRs/sessions, it's a pattern worth documenting. These are often more valuable than one-off mistakes because they represent systemic gaps.

**Why this matters:** Review comments from `@propel-code-bot`, senior engineers, and code reviewers often surface patterns that aren't captured elsewhere. The compound skill previously only looked at user chat corrections, missing this valuable feedback source.

### Step 4: Analyze Structural Changes

Check what changed in the codebase structure:

```bash
# File organization changes
git diff main --name-status

# New directories created
git diff main --stat | grep -E "^\s+\w+/"

# Files that moved between directories
git diff main --name-status | grep "^R"
```

**Questions to answer:**
- Did files get reorganized into subdirectories?
- Did namespaces change due to moves?
- Were types consolidated/merged?
- Did the final structure differ from the plan?

### Step 5: Synthesize ALL Findings

Create a comprehensive table of ALL issues found:

```
## Issues Found Across Sessions

| Session | Issue | User Feedback | Root Cause |
|---------|-------|---------------|------------|
| Plan | [issue] | [exact user quote] | [why it happened] |
| Work | [issue] | [exact user quote] | [why it happened] |
| Review | [issue] | [exact user quote] | [why it happened] |
| Debug | [issue] | [exact user quote] | [why it happened] |
```

**For EACH issue, ask:**
1. Could this have been caught earlier? (In plan? In work? In review?)
2. What skill should have prevented this?
3. What check/question was missing?

**Categorize issues:**
- **Research gaps** - Didn't find existing code/types
- **Organization gaps** - Didn't plan structure
- **Verification gaps** - Wrong build command, missed test
- **Intent gaps** - Misunderstood what user wanted
- **Pattern violations** - Didn't follow documented patterns

### Step 6: Document the Learnings

**For pattern updates** -> Update existing pattern file:
```bash
# Determine learnings directory (project-local first)
LEARNINGS_DIR="$(git rev-parse --show-toplevel 2>/dev/null)/.llm/learnings"
if [ ! -d "$LEARNINGS_DIR" ]; then
  LEARNINGS_DIR="<learnings_directory from config.toml>"
fi
# Edit existing pattern file
edit $LEARNINGS_DIR/lang-patterns/[relevant-topic].md
```

**For new learnings** -> Create file in appropriate subdirectory:
```bash
# Create new learning file
$LEARNINGS_DIR/gotchas/YYYY-MM-DD-description.md
```

**For hooks** (only if patterns don't prevent recurrence):
```bash
# Create hookify rule
~/.claude/hooks/[hook-name].md
```

### Step 7: File Skill Improvement Issues

In addition to the steps below, apply `common.md` routing for reusable code/domain learnings so KB issues are created with retrieval-led targeting when appropriate.

**For EACH issue found**, determine which skill needs improvement:

| Issue Type | Skill to Improve |
|------------|------------------|
| Research gap (missed existing type) | plan Step 2 |
| Organization gap (flat files) | plan Step 2.5 |
| Wrong build command | plan + work |
| Integration test visibility | work "What NOT To Do" |
| Intent misunderstanding | Add to learnings (project-local, not an issue) |

**File a GitHub issue** for each skill that needs improvement. Learnings (patterns, gotchas, tool patterns) stay project-local:

```bash
gh issue create \
  --title "compound: Update [skill-name] - [brief description]" \
  --body "$(cat <<'EOF'
## Skill to Update
[skill-name] - [section/step]

## Proposed Change
[What should be added/changed in the skill instructions]

## Why
[Root cause from compound analysis - what went wrong and how this change prevents it]

## Source
Feature: [feature name]
Branch: [branch name]
Session: [session ID or date]
EOF
)"
```

**When to file an issue vs. create a learning:**
- **File issue:** The improvement is about the skill's instructions (applies to all projects)
- **Create learning:** The knowledge is project-specific (patterns, gotchas, tool usage, domain conventions)

### Step 8: Quality Gate (BLOCKING)

**Before presenting summary, verify you have:**

- [ ] Found ALL related sessions (searched by plan name, branch, class names, keywords)
- [ ] Extracted ALL user corrections from each session
- [ ] Checked git diff for structural changes
- [ ] Created issues table with ALL findings
- [ ] Filed issues for skill improvements (or confirmed none needed)
- [ ] Created/updated learnings documentation

**If any checkbox is unchecked, go back and complete it.**

### Step 9: Summarize Learnings

```
## Compound Summary

**Feature:** [name] | **Sessions:** [count] | **Branch:** [name]

### Issues Found

| Session | Issue | User Quote | Issue Filed |
|---------|-------|------------|-------------|
| ... | ... | ... | ... |

### Actions Taken

**Skill Issues Filed:**
- `#[number]`: [skill-name] - [brief description]
- (or "No skill changes needed")

**Learnings Created:**
- `gotchas/YYYY-MM-DD-name.md`: [what it covers]

**Hooks Created:**
- [List any hooks, or "None needed"]
```

Then proceed to Step 10 (Workflow Optimization) - this is required.

## Decision Tree: Patterns vs Hooks

```
Problem occurred ->
|
+- Is this documented in patterns?
|  +- YES -> Pattern not being followed
|  |        -> Improve pattern visibility/clarity
|  |
|  +- NO -> New undocumented issue
|          -> Add to patterns
|
+- After documenting, will this prevent recurrence?
|  +- YES -> Done (patterns are preferred)
|  |
|  +- NO -> Create hook to catch at runtime
```

## Learning Storage Locations

Use project-local `<git-root>/.llm/learnings/` when available, otherwise fall back to config path.

| Type | Location |
|------|----------|
| Language patterns | `$LEARNINGS_DIR/<language>-patterns/` (e.g., `lang-patterns/`, `lang-patterns/`) |
| Gotchas | `$LEARNINGS_DIR/gotchas/` |
| Workflow patterns | `$LEARNINGS_DIR/patterns/` |
| Tool patterns | `$LEARNINGS_DIR/tools/` |
| Hooks (last resort) | `~/.claude/hooks/` |

### Step 10: Workflow Optimization (REQUIRED)

**This step is not optional.** Every compound run must identify at least one way to improve the workflow.

Analyze the ENTIRE session for friction - not just errors, but any manual work that slowed things down.

**Questions to Answer (must address ALL):**

1. **What mistake was made?** How do we prevent it next time?
   - Update a pattern? Update a skill checklist? Create a hook?

2. **What was slow?** What manual work could be automated?
   - New skill? Improve existing skill? Better tooling?

3. **What existing skill could be improved?** Based on this session:
   - Missing checklist items? Unclear instructions? Missing automation?

4. **Is there a new skill opportunity?**
   - Repetitive pattern that should be a skill?
   - Context-switching that could be eliminated?

**Output Format (REQUIRED):**

```
## Workflow Optimization

**Mistake Prevention:**
- [What was added/updated to prevent recurrence, or "No mistakes made"]

**Speed Improvements:**
- [What was automated/improved, or "No optimization opportunities identified - explain why"]

**Skill Issues Filed:**
- [List issues filed: `#N` - description, or "No skill changes needed"]

**New Skill Opportunities:**
- [Describe opportunity, or "None identified - workflow is optimal for this task type"]
```

**Common Improvements:**

| Session Pattern | Improvement Type |
|----------------|------------------|
| Caught issue in review | Add to review checklist |
| Manual repetitive task | Create/update skill |
| Pattern violation | Update pattern docs |
| Same mistake twice | Create hook |
| Switched to external tool | Create integration skill |

## When to Use

- After completing a feature
- After fixing a bug
- When you encountered an unexpected issue
- When you had to deviate from documented patterns
- After any "aha" moment during development
- **When you notice workflow friction that could be automated**
