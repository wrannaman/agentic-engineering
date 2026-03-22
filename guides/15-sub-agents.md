# Sub-Agents: Parallelism, Depth, and Consensus

Sub-agents are one of the most underutilized capabilities in agentic engineering. A single agent working sequentially is fine for simple tasks. For anything complex — research, review, analysis, exploration — spawning multiple sub-agents in parallel gets you better results faster.

## Three Uses for Sub-Agents

### 1. Speed (Parallel Exploration)

Instead of searching the codebase sequentially, spawn 5 sub-agents that each explore a different aspect simultaneously:

```
Main agent: "I need to plan a new API endpoint."

Sub-agent 1: "Find existing API endpoints and extract patterns."
Sub-agent 2: "Find the auth middleware and how it's applied."
Sub-agent 3: "Find the test patterns for API endpoints."
Sub-agent 4: "Search the KB for API conventions."
Sub-agent 5: "Check for existing types/models related to this feature."

All 5 return in ~10 seconds instead of ~50 seconds sequentially.
```

**Used in:** `/plan` (codebase research), `/seed` (codebase analysis), `/compound` (parallel extraction)

### 2. Depth (Multiple Perspectives)

A single agent reviewing code has one perspective. Eight sub-agents each reviewing from a different angle catch more issues:

```
Main agent: "Review this diff."

Sub-agent 1 (API Design):    "Are the endpoints RESTful? DTOs clean?"
Sub-agent 2 (Performance):   "Any N+1 queries? Unnecessary re-renders?"
Sub-agent 3 (Security):      "Input validation? Auth checks? Injection?"
Sub-agent 4 (Patterns):      "Does this follow the KB conventions?"
Sub-agent 5 (Simplicity):    "Is anything over-engineered?"
Sub-agent 6 (Code Reuse):    "Does this duplicate something that already exists?"
Sub-agent 7 (Idiom):         "Is this idiomatic for the language/framework?"
Sub-agent 8 (AI Slop):       "Unnecessary abstractions? Verbose comments?"

Main agent deduplicates and ranks findings.
```

This isn't just faster — it's more thorough. Each sub-agent focuses deeply on one lens without getting distracted by others.

**Used in:** `/review` (8 parallel review passes), `/adversarial` (multiple attack angles)

### 3. Consensus (Agree Before Acting)

For high-stakes decisions, spawn sub-agents that independently analyze the same question, then compare answers:

```
Main agent: "Should we use Redis or Postgres for this cache?"

Sub-agent 1: "Argue for Redis. Consider performance, ops complexity, team familiarity."
Sub-agent 2: "Argue for Postgres. Consider simplicity, existing infrastructure, maintenance."
Sub-agent 3: "What does the KB say about caching patterns in this codebase?"

Main agent synthesizes: "Two sub-agents agree that Postgres is better for this case
because we already run it and the cache volume is small. Redis would be premature optimization."
```

When sub-agents independently reach the same conclusion, confidence is high. When they disagree, you've found a genuine decision point that needs human input.

**Used in:** `/brainstorm` (evaluate approaches), `/plan` (validate design decisions)

## How to Use Sub-Agents in Skills

### In Claude Code

Use the Agent tool with `subagent_type` parameter:

```
Agent tool call:
  subagent_type: "Explore"
  prompt: "Find all API endpoints in src/api/ and extract the common patterns..."
```

Multiple Agent tool calls in the same message run in parallel.

### In Cursor / Codex / Other Agents

The sub-agent pattern adapts to whatever parallel execution your agent supports. The key principle is: **decompose the task, run parts simultaneously, synthesize results.**

If your agent doesn't support parallel sub-agents, the skills still work — they just run sequentially. The output is the same; the speed is slower.

## When NOT to Use Sub-Agents

- **Simple, sequential tasks.** Reading one file and making one change doesn't benefit from parallelism.
- **Tasks with dependencies.** If sub-agent B needs sub-agent A's output, they can't run in parallel.
- **When context is small.** If the answer is in one file, one agent is fine.

## Sub-Agent Patterns in This Architecture

| Skill | Sub-Agent Pattern | Why |
|-------|-------------------|-----|
| `/plan` | 5 parallel explorers (types, libraries, patterns, tests, conventions) | Research is embarrassingly parallel |
| `/review` | 8 parallel reviewers (API, perf, security, patterns, simplicity, reuse, idiom, slop) | Each perspective is independent |
| `/seed` | 1 sub-agent per major directory (frontend, backend, tests, infra) | Large codebases parallelize by area |
| `/compound` | 2 parallel: prose extraction + code pattern extraction | Independent analysis streams |
| `/brainstorm` | 2-3 sub-agents each researching a different approach | Independent exploration |
| `/adversarial` | Sub-agents attack from different angles (edge cases, failures, scale, abuse) | Each attack vector is independent |
