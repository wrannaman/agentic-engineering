# Code Compound Skill

You are entering the **code-compound phase**. You will analyze existing code to extract patterns and document them as learnings.

## Configuration

**Learnings Directory:** Always use project-local `<git-root>/.llm/learnings/`

Code patterns extracted from a codebase are specific to that codebase and should stay with it. Unlike session-based compound (which may fall back to a shared learnings directory), code-compound always writes to project-local.

**Setup:** If the directory doesn't exist, create it:
```bash
LEARNINGS_DIR="$(git rev-parse --show-toplevel 2>/dev/null)/.llm/learnings"
mkdir -p "$LEARNINGS_DIR/code-patterns"
```

## Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `<paths>` | - | Specific files or directories to analyze |
| `--explore` | false | Self-explore codebase to find interesting patterns |
| `--focus <area>` | - | Focus area: `error-handling`, `validation`, `api`, `data-access`, `testing`, etc. |

**Examples:**
```bash
# Analyze specific files
/code-compound src/services/AuthService.cs src/services/UserService.cs

# Analyze a directory
/code-compound src/domain/

# Self-explore the codebase
/code-compound --explore

# Focus on error handling patterns
/code-compound --explore --focus error-handling

# Combine: explore but focus on specific area
/code-compound src/api/ --focus validation
```

## Process

### Step 1: Determine Scope

**If specific paths provided:**
- Read and analyze the specified files/directories
- Identify the domain/layer these files belong to

**If `--explore` flag:**
1. Get codebase structure overview
2. Identify key architectural layers (API, domain, data access, etc.)
3. Sample representative files from each layer
4. Focus on high-traffic areas (files with many imports/references)

**If `--focus` specified:**
- Filter analysis to patterns related to that focus area

### Step 2: Pattern Extraction

For each file/area analyzed, extract:

**Code Conventions:**
- Naming patterns (classes, methods, variables)
- File/folder organization
- Import/using organization

**Architectural Patterns:**
- Layer separation approach
- Dependency injection patterns
- Interface usage patterns

**Implementation Patterns:**
- Error handling approach
- Validation patterns
- Logging patterns
- Data access patterns
- API design patterns

**Testing Patterns:**
- Test organization
- Mocking approach
- Assertion style

### Step 3: Pattern Analysis

For each extracted pattern, determine:

1. **Consistency** - Is this pattern used consistently or are there variations?
2. **Intentionality** - Does this appear deliberate or accidental?
3. **Quality** - Is this a good pattern to follow or an anti-pattern to avoid?

**Pattern format:**
```
## [Pattern Name]

**Type:** Convention | Architecture | Implementation | Testing
**Consistency:** High | Medium | Low
**Quality:** Follow | Avoid | Context-dependent

**Description:**
[What the pattern is and how it works]

**Examples:**
- `path/to/file.cs:123` - [brief description]
- `path/to/other.cs:45` - [brief description]

**Guidance:**
[When and how to apply this pattern]
```

### Step 4: Present Findings

Present patterns grouped by type:

```
## Code Patterns Found

### Conventions
1. [Pattern 1]
2. [Pattern 2]

### Architecture
1. [Pattern 1]

### Implementation
1. [Pattern 1]
2. [Pattern 2]

### Testing
1. [Pattern 1]

---

**Summary:**
- [X] conventions identified
- [Y] architectural patterns
- [Z] implementation patterns

**Notably Consistent:** [patterns that are very consistently applied]
**Inconsistencies Found:** [patterns with variations - may need standardization]
```

### Step 5: User Approval

Ask the user which patterns to document:

```
## Documentation Options

I found [N] patterns worth documenting.

**Which should I save to the learnings library?**
1. All of them
2. Let me select specific ones
3. None - this was just for understanding
```

Use AskUserQuestion to get approval.

### Step 6: Document Approved Patterns

For each approved pattern, create a file in the project-local learnings directory:

```bash
# Ensure directory exists
LEARNINGS_DIR="$(git rev-parse --show-toplevel 2>/dev/null)/.llm/learnings"
mkdir -p "$LEARNINGS_DIR/code-patterns"
```

**Location:** `$LEARNINGS_DIR/code-patterns/`

**File format:**
```markdown
# [Pattern Name]

**Date:** YYYY-MM-DD
**Source:** [codebase/directory analyzed]
**Type:** Convention | Architecture | Implementation | Testing

## The Pattern

[Clear description of the pattern]

## When to Use

[Guidance on when this pattern applies]

## Examples

    // From path/to/file.cs
    [code example]

## Anti-patterns to Avoid

[What NOT to do, if applicable]
```

**Filename:** `YYYY-MM-DD-pattern-slug.md`

### Step 7: Summary

```
## Code Compound Complete

**Scope Analyzed:**
- [Files/directories analyzed]
- [Focus area if specified]

**Patterns Found:** [N]
**Patterns Documented:** [M]

**New Learning Files:**
- `code-patterns/2025-01-12-error-handling-result-type.md`
- `code-patterns/2025-01-12-validation-fluent-pattern.md`

**Key Takeaways:**
- [Most important pattern to follow]
- [Common pitfall to avoid]

**Inconsistencies to Address:**
- [Any patterns that need standardization]

---

**Knowledge Compounded!** These code patterns are now documented for onboarding and reference.
```

## Exploration Strategy

When using `--explore`, prioritize:

1. **Entry points** - API controllers, command handlers, main files
2. **Core domain** - Business logic, domain models
3. **Data access** - Repositories, database contexts
4. **Cross-cutting** - Middleware, filters, base classes
5. **Tests** - Test organization and patterns

**File selection heuristics:**
- Files with many lines (likely core functionality)
- Files imported by many others (high-impact patterns)
- Files in standard locations (Controllers/, Services/, Domain/)
- Recently modified files (current patterns vs legacy)

## Focus Areas

| Focus | What to Look For |
|-------|------------------|
| `error-handling` | Result types, exceptions, error responses, logging |
| `validation` | Input validation, FluentValidation, data annotations |
| `api` | Route conventions, response formats, versioning |
| `data-access` | EF Core patterns, repositories, query patterns |
| `testing` | Test structure, mocking, fixtures, assertions |
| `logging` | Log levels, structured logging, correlation |
| `security` | Auth patterns, authorization, input sanitization |
| `dependency-injection` | Registration patterns, lifetimes, factories |

## When to Use

- **Onboarding** - New to a codebase, need to understand conventions
- **Documentation** - Codebase has implicit patterns that should be explicit
- **Standardization** - Want to identify and document the "right way" to do things
- **Code review prep** - Understand patterns before reviewing PRs
- **Before refactoring** - Document current patterns before changing them
