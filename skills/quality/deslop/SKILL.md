---
name: deslop-code
description: Aggressively reduce and clean up code in any language — strip AI slop, remove bloat, collapse indirection, and shrink files to their essence. ALWAYS use this skill when the user wants code made shorter, leaner, or less verbose — whether they say "deslop", "reduce", "simplify", "trim", "slim down", "too much code", "make shorter", "clean up", "bloated", "overengineered", or complain about excessive comments, unnecessary abstractions, single-use helpers, defensive checks, or verbose boilerplate. Also triggers when reviewing AI-generated code before committing. Default scope is changed files on the current branch vs main.
---

Aggressively reduce code. Every line must earn its place — strip AI artifacts, remove bloat, and shrink files to their essence while preserving clarity and correctness.

## Scope

Default: files changed on the current branch vs main (`git diff --name-only main...HEAD`).
If the user specifies files, directories, or patterns, use those instead.

## Process

1. Get the file list for the scope above
2. Read each file completely — understand what it does before touching it
3. Apply reductions file by file, using all applicable techniques below
4. After all edits, run any available tests/typecheck to confirm nothing broke
5. Report: files modified, approximate lines removed, notable structural changes

## Reduction Techniques

Apply in rough priority order. Each change should pass a simple test: "does the code still read clearly to someone seeing it for the first time?"

### Delete dead code
- Unreachable branches, unused imports, unused variables, unused functions, unused types
- Feature flags that are always on/off
- Commented-out code — it's in git history if anyone needs it

### Strip AI-generated noise
- Comments explaining obvious code (`// increment counter` above `count++`)
- Comments more detailed than surrounding file style
- Section headers/banners (`// TYPES ---`, `// CONSTANTS`, `// PUBLIC API`)
- Keep only comments explaining WHY, not WHAT
- Noisy logs: `console.log`/`logger` calls with no actionable information (keep errors, warnings, state transitions, external API calls)

### Remove defensive bloat
- `try/catch` around code that cannot throw
- Null checks on values already guaranteed non-null by the type system or prior logic
- Redundant parameter validation inside internal (non-boundary) functions
- Assertions that duplicate what the type system already enforces
- Exception: keep defensive code at system boundaries (network calls, file I/O, user input, external APIs)

### Collapse indirection
- Inline functions/methods called exactly once (unless the name provides significant documentation value)
- Inline single-use variables: `const x = foo(); return x;` → `return foo();`
- Flatten unnecessary wrappers: `const handleClick = () => doThing()` → pass `doThing` directly
- Collapse single-implementation interfaces/abstractions — if there's only one implementation and no test mock, the abstraction isn't paying for itself yet

### Simplify control flow
- `if (x) return true; return false;` → `return x;`
- `if (x) { return a; } else { return b; }` → `return x ? a : b;` (simple expressions only)
- Early returns to reduce nesting
- Merge sequential ifs with the same body
- Replace verbose iteration with built-in methods (`map`, `filter`, `reduce`, `find`, `some`, `every`, `Object.entries`, `Object.fromEntries`)

### Leverage language features
- Destructuring instead of repeated property access
- Optional chaining (`?.`) and nullish coalescing (`??`) instead of manual checks
- Template literals instead of string concatenation
- Spread/rest instead of manual copying
- In Python: list/dict comprehensions, `dict.get()`, `{**d1, **d2}`, `itertools`, unpacking
- In TypeScript/JavaScript: `satisfies`, `as const`, mapped types, utility types to eliminate boilerplate

### Fix type safety
- `as any`, `as Type` casts — replace with type guards
- `@ts-ignore` — fix the underlying type issue
- Use `unknown` + narrowing instead

### Tighten declarations
- `let` → `const` where not reassigned (then inline if single-use)
- Remove explicit types the language can infer
- Remove language-specific redundancies (e.g., redundant `public` in TypeScript)
- Remove empty constructors, empty `super()` calls, default parameter values matching the type's default

### Consolidate repetition
- Extract repeated multi-line patterns into a helper **only if it appears 3+ times**
- Replace repetitive construction with data-driven generation
- Use loop/map over repetitive sequential statements
- Collapse identical test setups into shared fixtures

### Match surrounding style
- Naming, spacing, or patterns that don't match the surrounding file — reformat to match existing conventions

## What NOT to do

- **Don't minify** — `calculateTax` → `ct` destroys readability
- **Don't merge unrelated logic** — cramming two concerns onto one line makes code worse
- **Don't remove error handling at system boundaries** — network calls, file I/O, user input need their guards
- **Don't sacrifice readability for cleverness** — a 3-line `reduce` nobody can parse is worse than a 5-line loop
