# Seed

> Auto-generate KB docs from your existing codebase. The cold start killer.

## Purpose

The #1 reason agentic engineering fails is an empty knowledge base. Engineers are told "write docs for the KB" and either procrastinate or write docs so generic they're useless.

This skill analyzes your codebase and generates draft KB documents that capture how your team actually builds software — extracted from real code, not imagination. Senior engineers review and refine the drafts, starting from 80% instead of zero.

## Usage

```
/seed ~/code/my-app
```

Or run from within a repo:

```
/seed .
```

## Process

### Step 1: Analyze Codebase Structure

Scan the repo to understand what's here:

```
- Language(s) and framework(s) (detect from package.json, *.csproj, pyproject.toml, go.mod, etc.)
- Directory structure and organization conventions
- Number and types of source files
- Test location and naming patterns
- Config files and their purposes
```

**Output:** Brief summary to the user:
```
Found: TypeScript/React frontend (src/app/), Python/FastAPI backend (src/api/),
       847 source files, 234 tests, PostgreSQL migrations in db/migrations/
```

### Step 2: Detect Patterns

For each major area, analyze 5-10 representative files to extract patterns:

**API/Routes:**
- Read 5 route handlers → extract common patterns (validation, error handling, response shape)
- Read API tests → extract testing patterns
- Note: endpoint naming, middleware usage, auth patterns

**Components/Pages (frontend):**
- Read 5 page components → extract layout patterns, data fetching, state management
- Read 5 shared components → extract prop patterns, composition style
- Note: styling approach (CSS modules, Tailwind, styled-components)

**Data Layer:**
- Read models/schemas → extract naming conventions, relationship patterns
- Read migrations → extract migration patterns
- Read database access code → extract query patterns (ORM style, raw SQL, etc.)

**Testing:**
- Read 5 test files → extract testing patterns (setup, assertions, mocking)
- Note: test runner, assertion library, fixture patterns

**Config & Infrastructure:**
- Read CI/CD configs → extract pipeline patterns
- Read Docker/deployment configs → extract deployment patterns
- Read linter/formatter configs → extract code style rules

### Step 3: Generate Draft KB Documents

**Search-aware writing:** The KB uses full-text keyword search, not vector embeddings. How you write these docs determines whether agents find them. Follow these rules:

- **Titles match how someone would search.** Not "Considerations for Client-Side Data Management" — use "React Query Data Fetching Patterns."
- **Keywords include synonyms and the specific names from the codebase.** If the utility is called `AppError`, include `AppError`. If the wrapper is `defineApi`, include `defineApi`. Agents search for the concrete things they see in code.
- **Section headings contain the actual terms.** Not "The Approach" — use "Using React Query for Server State."
- **Don't keyword-stuff.** Write naturally. But always prefer specific over vague.

For each detected area, generate a markdown KB document:

```markdown
---
keywords: [relevant keywords including codebase-specific names, synonyms, and related terms]
last_reviewed: [today's date]
owner: [suggest based on directory]
status: draft
---

# [Specific, Searchable Pattern Name]

> Auto-generated from codebase analysis. Review and refine before committing to KB.

## Convention

[Describe the pattern observed in the codebase]

## Example (from codebase)

[Include a real code example extracted from the repo — anonymized if needed]

## Anti-patterns

[Note any inconsistencies found — places where the codebase doesn't follow its own patterns]

## Notes for Review

[Flag anything the skill wasn't sure about — "Is this intentional or tech debt?"]
```

### Step 4: Generate Partition Structure

Propose a partition structure based on what was found:

```
kb-docs/
├── frontend/
│   ├── component-patterns.md
│   ├── data-fetching.md
│   ├── state-management.md
│   └── styling-conventions.md
├── backend/
│   ├── api-conventions.md
│   ├── database-patterns.md
│   ├── error-handling.md
│   └── auth-patterns.md
├── testing/
│   ├── unit-test-patterns.md
│   ├── integration-test-patterns.md
│   └── test-utilities.md
└── architecture/
    ├── directory-structure.md
    ├── service-boundaries.md
    └── deployment.md
```

### Step 5: Write Files

Write all draft docs to a specified output directory:

```bash
# Default: ./kb-docs-draft/
# User can specify: /seed . --output ~/kb-docs/
```

### Step 6: Present Summary

```
Generated 14 KB draft documents in ./kb-docs-draft/

Partitions:
  frontend/     4 docs  (React, TypeScript, Next.js patterns)
  backend/      4 docs  (FastAPI, PostgreSQL, auth patterns)
  testing/      3 docs  (pytest, React Testing Library patterns)
  architecture/ 3 docs  (directory structure, deployment, services)

Next steps:
  1. Review each doc — look for "Notes for Review" sections
  2. Edit: fix anything wrong, add context only humans know
  3. Remove the `status: draft` from frontmatter when reviewed
  4. Commit to your KB docs repo
  5. The KB server will auto-index on next sync

Files with the most "Notes for Review" (prioritize these):
  - backend/error-handling.md (3 notes — inconsistent patterns found)
  - frontend/state-management.md (2 notes — mixed approaches detected)
```

## What This Does NOT Do

- **Does not commit to the KB.** Drafts only. Human review is mandatory.
- **Does not read secrets.** Skips .env files, credentials, etc.
- **Does not invent patterns.** Only documents what it observes in the code. If the codebase is inconsistent, it flags the inconsistency.
- **Does not replace expert judgment.** The "Notes for Review" sections are where senior engineers add context: "This pattern exists because of X constraint" or "This is tech debt, don't follow this."

## When to Use

- **Initial setup** — First time deploying agentic engineering
- **New repo onboarded** — Adding a new repo to the KB
- **Major refactor completed** — Patterns have changed significantly
- **Periodic refresh** — Run quarterly to catch drift between docs and code

## Hard Rules

- Never write directly to the KB docs repo. Always output drafts.
- Always include `status: draft` in frontmatter until human review.
- Always include "Notes for Review" for anything uncertain.
- Never include secrets, credentials, or PII in generated docs.
- Include real code examples (with file paths) so reviewers can verify accuracy.
