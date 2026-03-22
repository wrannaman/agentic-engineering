# Philosophy

## Thinking Is Not Dead

Agents write code. You make decisions. That division of labor is the entire point.

Someone said recently that "by the end of the year, software engineering will be solved." It's not. The writing-code part is getting automated. The thinking part — what to build, why, whether it's right, what breaks if you're wrong — that's more important than ever, and it's entirely human.

This system amplifies your judgment. If your judgment is good, the agent multiplies your output 5-10x. If your judgment is absent — copy-pasting without reading, approving without reviewing, merging without thinking — the agent multiplies your mistakes at the same rate.

The agent doesn't know your largest customer depends on that exact response shape. It doesn't know the migration will lock the orders table for 45 minutes during peak. It doesn't know "simplify auth" means something different to security than to product. You know those things. That's why you're here.

Everything in this repo — the KB, the skills, the compound loop, the mandatory human review — exists to keep humans in the loop where they add the most value: judgment, context, taste, and the ability to say "that's wrong, and here's why."

On the low end, someone with no engineering background can build an app with AI tools and that's wonderful. On the high end — five nines, database sharding, regulatory compliance, thousands of customers — someone has to think. That's you.

> These positions are shaped by what the best engineering organizations are doing right now — Stripe, Intercom, TELUS, Zapier, Dropbox, and others. They're not predictions. They're observations about what works.

## The Role Shift

Most feature development should be driven by **product and design, not engineering**.

The translation step — designer creates mockup, engineer interprets, engineer implements — is the bottleneck this architecture eliminates. With a well-seeded knowledge base and the compound loop running, product people and designers should be able to describe what they want, have an agent implement it, and get 80-90% of the way there for incremental features.

Copy changes, styling, config, simple features, new pages that follow existing patterns — these don't need an engineer to write the code. They need an engineer to **review** the code.

**Figma becomes a thinking tool, not a handoff artifact.** You use Figma to align on what you're building. You don't need a separate process to "translate" that into engineering tickets. The person who knows what they want describes it to the agent, and the agent builds it.

Net-new features, novel architecture, performance-critical systems, complex integrations — these still need senior engineers driving. Anthropic's own research shows developers can fully delegate only [0-20% of tasks](https://claude.com/blog/eight-trends-defining-how-software-gets-built-in-2026). But the incremental 80% — the work that follows established patterns — that's where agents excel, and that's what this system targets.

## The Skill Shift

The skills that make a great engineer are changing. This isn't speculation — it's what companies running agents at scale are seeing.

| From | To |
|------|-----|
| Writing code | Specifying intent precisely |
| Debugging code | Debugging agent behavior |
| Code review (style + logic) | Code review (judgment + architecture) |
| Architecture design | Constraint system design |
| Knowing syntax | Knowing your codebase's patterns |

The skills that remain critical: **domain expertise** (understanding the business problem), **systems thinking** (how components interact), **security awareness** (agent-scale development requires agent-scale security), and **code reading ability** (you review more than you write).

## Engineering's New Job

Engineering shifts from "write features" to **"build and maintain the infrastructure that enables everyone in the org to ship."**

This is a full-time job:

- Maintaining the knowledge base (keeping it accurate, well-partitioned, pruned)
- Improving the skills (tuning the brainstorm/plan/work/review cycle)
- Running the compound loop (extracting learnings, feeding them back)
- Setting up guardrails (CI, review bots, test coverage, type safety)
- Reviewing PRs (the one human gate that stays)
- Building the hard stuff (the 10-20% that agents can't one-shot)

The best engineering orgs won't be the ones with the most engineers writing code. They'll be the ones where engineers have built the best systems for everyone else to ship safely.

## Seven Principles

### 1. Product & Design Ship Features, Engineering Builds the System

The person closest to the problem should be able to ship the solution. Product knows what the customer needs. Design knows how it should look and feel. They shouldn't need to translate that into an engineering ticket and wait.

### 2. Anyone Can Ship (Mechanically)

No local dev environment required. Slack command triggers a Codespace. Agent runs the full cycle. Draft PR goes up. Engineer reviews. If your PM can describe a bug fix clearly, the agent can implement it.

### 3. Prove It Works

The planner defines how verification will happen — not just "tests pass," but "we can observe that the thing actually does the thing." Redis keys exist with correct values. The API fails correctly when the write fails. The page renders the cached data.

Sometimes verification requires human input. That's fine. The agent should know what it needs and ask for it explicitly.

### 4. Be Review-Constrained

All code gets reviewed by a human. No exceptions. Senior engineers, juniors, agents, designers — all code goes through review.

This is the correct organizational bottleneck. Everything else should be automated. Review is where humans add judgment, context, and taste. The compound loop reduces even the review burden over time.

### 5. Deterministic + Agentic (Not Either/Or)

This is [how Stripe builds their agents](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2), and it's the right model: **agents handle the creative work. Deterministic code handles everything else.**

Linters, formatters, test runners, CI pipelines, commit message formatting — these should NEVER run through the agent. They run as deterministic steps in the pipeline. The agent writes code; deterministic tooling validates it. This is more reliable, faster, and cheaper than asking the agent to self-validate.

```
Agent writes code (agentic)
    → Linter formats it (deterministic)
    → Type checker validates it (deterministic)
    → Tests run (deterministic)
    → CI builds (deterministic)
    → Agent reads failures and fixes (agentic)
    → Repeat ONCE, then human (bounded)
```

### 6. Bounded Iteration (Not Infinite Loops)

When the agent's code fails CI, it gets one automatic retry with fixes. If the same error fails twice, it stops and asks a human. Stripe does one CI loop + one retry, then human review. Not infinite retries.

This matters because:
- Infinite retry loops waste tokens and time
- If the agent can't fix it in two tries, it's likely a design problem, not a typo
- The human needs to see the failure to understand the gap
- The failure feeds the compound loop (next time, the KB has the answer)

### 7. Security at Agent Scale

An agent producing 1,000 PRs per week with a 1% vulnerability rate creates 10 new vulnerabilities weekly. Manual review cannot catch all of them at that volume.

Security must be automated and structural:
- Input validation is enforced by framework, not by the agent remembering
- Auth checks are middleware, not per-endpoint decisions
- The `/review` skill includes security as a **default** perspective (not optional)
- CI includes SAST/DAST scanning on every PR
- The KB contains security patterns specific to your stack

This is one area where the agent should be paranoid. Better to over-validate than to ship an injection vulnerability.
