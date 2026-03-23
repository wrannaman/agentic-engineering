# Common Compound Policies

Apply these rules across all compound workflows.

## Learnings Directory Policy

Use project-local learnings when possible.

```bash
LEARNINGS_DIR="$(git rev-parse --show-toplevel 2>/dev/null)/.llm/learnings"
if [ ! -d "$LEARNINGS_DIR" ]; then
  LEARNINGS_DIR="<learnings_directory from config.toml>"
fi
```

Code-compound is stricter: it always writes project-local.

```bash
LEARNINGS_DIR="$(git rev-parse --show-toplevel 2>/dev/null)/.llm/learnings"
mkdir -p "$LEARNINGS_DIR"
```

## Evidence and Exhaustiveness

- Be exhaustive; do not stop at first signal.
- Tie each finding to concrete evidence.
- Prefer exact user quotes, review comments, file paths, and command outputs.
- Distinguish recurring patterns from one-off incidents.

## CRITICAL: Edit, Don't Add

The KB's biggest failure mode is bloat. The compound loop naturally wants to ADD new docs. Fight this.

**Before creating any new KB doc or learning file:**
1. Search the KB for existing docs on this topic (`search_documents` with relevant keywords)
2. Search `.llm/learnings/` locally for existing files on this topic
3. If a related doc exists → propose an EDIT to that doc (add a section, update a paragraph, refine the wording)
4. Only create a new doc if nothing related exists after searching

**Think wiki, not blog.** A wiki has one page about error handling that gets refined. A blog has 12 posts about error handling that nobody can navigate.

**Precision over coverage.** A 10-line addition to an existing doc is better than a new 50-line doc that overlaps with three others.

## Routing Outcomes

For each finding, route to one or more destinations:

| Finding Type | Destination | Action |
|--------------|-------------|--------|
| Skill instruction/workflow gap | Skills repo | File skill improvement issue |
| Reusable code/domain knowledge | Relevant KB repo | File KB update/create issue |
| Project-specific one-off detail | Local learnings | Create/update local learning file |
| Reusable knowledge that also helps now | Both local learnings + KB repo | Do both |

## Retrieval-Led KB Targeting

Use retrieval-led modeling to determine the right KB repo/doc before filing a KB issue.

1. `list_kb_partitions`
2. `list_kb_documents` for likely partitions
3. `read_kb_document_by_keywords`
4. `read_kb_document_by_path` for likely canonical docs

Then:
- Prefer updating an existing canonical doc when there is a strong match.
- If no match exists, propose a new doc in the closest partition/repo.
- Include partition + path decision in the issue body.

## Issue Templates

### Skill issue

```bash
gh issue create \
  --title "compound: Update [skill-name] - [brief description]" \
  --body "$(cat <<'__ISSUE_BODY__'
## Skill to Update
[skill-name] - [section/step]

## Proposed Change
[What should be added/changed]

## Why
[Root cause and recurrence prevention]

## Source
Feature: [feature]
Branch: [branch]
Session/PR: [id or date]
__ISSUE_BODY__
)"
```

### KB issue (KB docs repo)

**Search-aware writing:** The KB uses full-text keyword search, not embeddings. When proposing new docs or updates:
- Title should match how an agent would search (specific, not vague)
- Keywords should include synonyms AND the concrete names from the codebase (`AppError`, `defineApi`, etc.)
- Section headings should contain the actual terms, not abstractions

```bash
gh issue create --repo [kb-docs-repo] \
  --title "compound: [topic] - [create|update] KB doc" \
  --body "$(cat <<'__KB_BODY__'
## Knowledge Gap
[What reusable code/domain learning was discovered]

## Proposed KB Change
- Target doc: `kb/[area]/[doc].md` (or "new document needed")
- Change type: [create/update]
- Summary: [what to add]
- Suggested keywords: [include codebase-specific names, synonyms, related terms]

## Retrieval Evidence
- Partition(s) checked: [...]
- Existing docs considered: [...]
- Why this target: [...]

## Source
Feature/PR: [...]
Branch: [...]
Session/Date: [...]

## Local Learnings Link
[$LEARNINGS_DIR/... if created]
__KB_BODY__
)"
```

## Patterns vs Hooks

Prefer documentation first; use hooks only when docs alone do not reliably prevent recurrence.

Decision tree:

```text
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

Use project-local `<git-root>/.llm/learnings/` when available, otherwise fallback to config path.

| Type | Location |
|------|----------|
| Language patterns | `$LEARNINGS_DIR/<language>-patterns/` |
| Codebase patterns | `$LEARNINGS_DIR/code-patterns/` |
| PR-derived recurring patterns | `$LEARNINGS_DIR/pr-learnings/` |
| Gotchas | `$LEARNINGS_DIR/gotchas/` |
| Workflow patterns | `$LEARNINGS_DIR/patterns/` |
| Tool patterns | `$LEARNINGS_DIR/tools/` |
| Hooks (last resort) | `~/.claude/hooks/` |

## Standard Completion Summary Block

Use this structure in final workflow summaries:

```markdown
## Compound Summary

**Scope:** [...]
**Findings:** [...]

### Actions Taken
**Skill Issues Filed:** [... or none]
**KB Issues Filed:** [... or none]
**Learnings Updated:** [... or none]
**Hooks Added:** [... or none]
```
