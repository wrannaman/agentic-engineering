---
name: debug
description: "Find bugs by launching parallel investigation agents. Use when you have a bug report, error log, or broken behavior and need to find the root cause. Outputs a diagnosis document, not a fix."
---

# Debug

> Find the bug. Don't fix it yet. Output a diagnosis.

## Purpose

When you have a bug — an error in logs, a broken feature, unexpected behavior — this skill launches parallel investigation agents to find the root cause. It outputs a diagnosis document that feeds into `/plan` for the fix.

This is for the "I don't know where the bug is" case. If you already know what to fix, use `/plan` directly.

## Usage

```
/debug "Users are getting 500 errors on the /orders endpoint when filtering by date"
/debug <paste error log or stack trace>
/debug "The checkout flow hangs after clicking 'Place Order'"
```

## Process

### Step 1: Understand the Symptom

Parse the bug report to extract:
- **What's broken** — the observable symptom
- **When it happens** — trigger conditions, if known
- **Error output** — stack traces, logs, HTTP status codes
- **Affected area** — which part of the codebase (if known)

If the report is vague, ask ONE clarifying question. Don't ask five.

### Step 2: Launch Investigation Agents (Parallel)

Spawn 4-6 sub-agents simultaneously, each investigating a different hypothesis:

```
Sub-agent 1 (Stack Trace):     "Trace the error through the call stack. Read each file
                                 in the stack trace. What's the state at each step?"

Sub-agent 2 (Recent Changes):  "Check git log for the affected files. What changed recently?
                                 git log --oneline -20 -- <affected paths>"

Sub-agent 3 (Data Flow):       "Trace the data from input to error. What transformations
                                 happen? Where could the data be wrong?"

Sub-agent 4 (Similar Patterns): "Search the codebase for similar code paths that DO work.
                                  What's different about the broken path?"

Sub-agent 5 (KB/Learnings):    "Search the KB and .llm/learnings/ for known gotchas
                                 related to this area. Has this type of bug happened before?"

Sub-agent 6 (Environment):     "Check config, environment variables, database state,
                                 external service status — anything outside the code."
```

Not all 6 are needed for every bug. Choose based on the symptom:

| Symptom | Agents to Launch |
|---------|-----------------|
| Stack trace / error log | 1 (Stack Trace), 2 (Recent Changes), 5 (KB) |
| "It used to work" | 2 (Recent Changes), 4 (Similar Patterns), 6 (Environment) |
| Wrong data / unexpected behavior | 3 (Data Flow), 4 (Similar Patterns), 5 (KB) |
| Intermittent / flaky | 3 (Data Flow), 6 (Environment), 2 (Recent Changes) |
| No error, just broken | All 6 |

### Step 3: Synthesize Findings

Collect results from all sub-agents. Build a diagnosis:

```markdown
## Bug Diagnosis

**Symptom:** [What's broken]

**Root Cause:** [What's actually wrong — be specific: file, function, line if possible]

**Evidence:**
- [Finding from sub-agent 1]
- [Finding from sub-agent 2]
- [Corroborating evidence]

**Confidence:** [High / Medium / Low]
- High: root cause identified with evidence from 2+ agents
- Medium: likely root cause but needs verification
- Low: multiple hypotheses, needs more investigation

**Hypotheses Eliminated:**
- [What we checked that WASN'T the problem — saves time if someone revisits]

**Verification Steps:**
- [How to confirm this diagnosis before fixing]
  e.g., "Add a log at line X and reproduce — if Y is null, this diagnosis is correct"
```

### Step 4: Output the Diagnosis

If confidence is High or Medium:

```
## Diagnosis Complete

**Root Cause:** [specific explanation]
**File:** [path:line]
**Confidence:** High

**Verification:** [how to confirm before fixing]

Ready to fix? Use `/plan` to create an implementation plan for the fix.
```

If confidence is Low:

```
## Diagnosis Incomplete — Multiple Hypotheses

1. **[Hypothesis A]** — Evidence: [X]. Disproved by: [nothing yet].
2. **[Hypothesis B]** — Evidence: [Y]. Disproved by: [nothing yet].

**Recommended next step:** [specific investigation to narrow down]
   e.g., "Reproduce with logging enabled at [location] to differentiate hypotheses"
```

### Step 5: Save Diagnosis

Write to `.plans/YYYY-MM-DD-debug-<topic>.md` so the plan skill can reference it.

## What This Is NOT

- **Not a fixer.** This skill finds the bug. `/plan` + `/work` fix it.
- **Not a test runner.** If you know what test is failing, just read the test and the code.
- **Not for performance issues.** Performance investigation needs profiling data, not code reading.

## When to Use

- You have a bug report but don't know where to start looking
- The stack trace spans multiple files and you need to understand the flow
- "It used to work and now it doesn't" — something changed but you don't know what
- The error message is unhelpful and you need to trace through the code

## Hard Rules

- Don't fix anything. Output a diagnosis.
- Don't guess without evidence. If you're not sure, say so.
- Always check git history for recent changes — the most common bug cause is "someone changed something."
- Always check the KB for known gotchas in this area.
- If the diagnosis feeds into a fix, save it so `/plan` can reference it.
