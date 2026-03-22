# Simplify

> Review changed code for reuse, quality, and efficiency. Fix what you find.

## Purpose

After implementation, take a second pass looking for opportunities to simplify. Not the same as deslop (which removes AI bloat) — this is about finding cleaner approaches to what you just built.

## Usage

```
/simplify                  # Simplify changed files on current branch
/simplify src/api/         # Simplify specific directory
```

## Process

### Step 1: Get Changed Files

```bash
git diff --name-only main...HEAD
```

### Step 2: For Each File, Check

**Duplication:** Is there logic that duplicates something already in the codebase? Could it use an existing utility?

**Naming:** Do names clearly communicate intent? Would a reader understand this without context?

**Complexity:** Is there a simpler way to express this? Could a nested conditional be a guard clause? Could a loop be a map/filter?

**Consistency:** Does this follow the patterns established in surrounding code? Is it using the project's conventions?

**Efficiency:** Any obvious N+1 queries, unnecessary re-renders, or redundant computations?

### Step 3: Apply Fixes

For each issue found:
1. Apply the simplification
2. Verify tests pass
3. Move to next file

### Step 4: Report

```
Simplified 3 files:

  src/api/users.ts
    - Extracted duplicate validation into shared validateRequest()
    - Replaced nested if/else with early return

  src/app/users/page.tsx
    - Replaced manual fetch + useState with existing useQuery hook
    - Removed unused import

  src/utils/format.ts
    - No changes needed
```

## When to Use

- After `/work` completes, before `/review`
- When code feels "correct but messy"
- As a lighter alternative to a full refactor

## Difference from Deslop

| Simplify | Deslop |
|----------|--------|
| Finds cleaner approaches | Removes AI bloat |
| May restructure code | Mostly deletes/inlines |
| Focuses on design quality | Focuses on removing noise |
| Use after implementation | Use when code feels verbose |
