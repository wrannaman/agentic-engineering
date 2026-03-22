# Proof: Agentic Engineering in the Wild

> Don't take our word for it. Here's what's happening at companies that have implemented this.

## The Numbers (Industry-Wide)

- **57% of organizations** have AI agents running in production ([LangChain State of Agents](https://www.langchain.com/state-of-agent-engineering))
- **64% of companies** generate a majority of their code with AI assistance ([Jellyfish benchmark study](https://jellyfish.co/blog/2025-ai-metrics-in-review/))
- **59% increase** in average engineering throughput with AI-assisted development (CircleCI 2026 State of Software Delivery)
- Companies in the **top quartile of AI adoption** have **2x the PR throughput** of low adopters
- **64% of CIOs** plan to deploy agentic AI within 24 months (Gartner 2026 CIO Agenda)

---

## Company Case Studies

### Stripe — "Minions" (2026)

**Scale:** 1,300+ PRs merged per week with zero human-written code. Human-reviewed, but entirely agent-produced.

**Architecture:** One-shot agents called "Minions" that receive a fully assembled context payload and return a structured result. Workflows ("Blueprints") interleave agent steps with deterministic code steps — linters, test suites, CI, and formatters run without agent involvement. Agents + deterministic code beats either alone.

**Infrastructure:** ~500 MCP tools through an internal "Toolshed." Devboxes achieve "hot and ready" status within 10 seconds through proactive provisioning. Rule files scoped to specific directories (their version of partitioned knowledge).

**Key insight:** Iteration is bounded — one CI loop with autofixes, then one additional iteration if tests fail, then human review. Not infinite retries.

**Sources:** [Stripe Minions Part 2](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2), [Stripe AI Benchmarks](https://stripe.com/blog/can-ai-agents-build-real-stripe-integrations)

### Intercom — Internal Claude Code Platform (March 2026)

**Scale:** 13 plugins, 100+ skills, hooks as enforcement layer.

**Key findings:**
- **Non-engineers are the top users.** The read-only Rails production console's top 5 users were design managers, customer support engineers, and product management leaders.
- **Session-level compound loop:** Every session analyzed for improvement opportunities, auto-classified (`missing_skill`, `missing_tool`, `repeated_failure`, `wrong_info`), posted to Slack with pre-filled GitHub issue URLs.
- **OTEL instrumentation** of 14 agent lifecycle events flowing to Honeycomb. Privacy-first: never capture user prompts or messages.
- **Data team built 30+ analytics skills** (Snowflake, Gong, finance, customer health). Sales reps, PMs, data scientists all use them.
- **Safety gates for production access:** Read-replica only, blocked critical tables, mandatory model verification, Okta auth, DynamoDB audit trail. "No cowboy queries."
- **Evidence-based permissions:** After 5 permission prompts, the system analyzes 14 days of session transcripts and writes safe defaults.
- Quote: *"Friends at other tech companies are nowhere near this level of sophistication"*

**Source:** [Brian Scanlan's thread](http://x.com/brian_scanlan/status/2033978300003987527?s=20)

### TELUS — Full-Pipeline AI Integration (2025-2026)

**Scale:** One of Canada's largest telecom companies.

**Results:**
- **500,000 engineering hours saved**
- **30% faster** delivery speed
- **13,000+ custom AI solutions** created by teams

**Source:** [Jellyfish benchmark study](https://jellyfish.co/blog/2025-ai-metrics-in-review/)

### Doctolib — Claude Code Rollout (2026)

**Scale:** Entire engineering team.

**Results:**
- Replaced legacy testing infrastructure **in hours instead of weeks**
- Shipping features **40% faster**

**Source:** [Anthropic enterprise case studies](https://claude.com/blog/how-enterprises-are-building-ai-agents-in-2026)

### Zapier — Organization-Wide AI Adoption (2026)

**Results:**
- **89% AI adoption** across entire organization
- **800+ agents** deployed internally

**Source:** [Anthropic enterprise case studies](https://claude.com/blog/how-enterprises-are-building-ai-agents-in-2026)

### Dropbox — AI-Assisted Engineering (2026)

**Results:**
- Engineers who regularly use AI ship **20% more pull requests**
- While also **reducing change failure rate** (more code, fewer bugs)

**Source:** [Jellyfish benchmark study](https://jellyfish.co/blog/2025-ai-metrics-in-review/)

### Block (Square/Cash App) — "Goose" (2026)

Built their own internal coding agent called Goose. Part of a trend where large companies (Meta, Google with "Jetski" and "Cider") build custom agents tuned to their codebases and workflows.

**Source:** [Pragmatic Engineer AI Tooling 2026](https://newsletter.pragmaticengineer.com/p/ai-tooling-2026)

---

## Technical Evidence

### Vercel — AGENTS.md Outperforms RAG (2026)

**Finding:** A compressed 8KB docs index embedded in AGENTS.md achieved **100% pass rate** on framework-specific tasks, while skills-based retrieval (RAG) maxed at **79%**.

**Key insight:** "With AGENTS.md, there's no moment where the agent must decide 'should I look this up?' The information is always available." Simple, curated context beats complex retrieval.

**Source:** [Vercel blog](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals)

---

## The Trend

The pattern across all these companies is the same:

1. **Agents work best with curated context** — knowledge bases, rule files, AGENTS.md. Not generic pre-training.
2. **Non-engineers become power users** — designers, PMs, support, data teams. Not just engineers.
3. **The compound loop is the differentiator** — teams that feed learnings back improve continuously. Teams that don't plateau.
4. **Deterministic + agentic beats either alone** — linters, CI, formatters run deterministically. Agents handle the creative work. Stripe calls this "Blueprints." We call it the pipeline.
5. **Review stays human** — every company keeps human review as the final gate. Nobody ships agent code without a human approving it.

If your team is not doing this yet, the gap is growing. These companies aren't experimenting — they're shipping 1,300 PRs a week this way.

---

*Have a case study or data to add? Open a PR.*

## Skepticism & Counterpoints

Being honest about what doesn't work yet:

- **Autonomous agent activity is still a small percentage of total PRs at most companies.** It's growing exponentially, but it's early.
- **More code doesn't always mean better outcomes.** Jellyfish found the median team saw 15.2% throughput increase on feature branches, but throughput on the main branch *declined* 6.8%. More code being written doesn't mean more value being shipped. ([Source](https://waydev.co/engineering-leadership-blind-spot-of-2026/))
- **Novel architecture is hard to one-shot.** Agents are best at incremental work following existing patterns.
- **KB quality is critical.** Garbage in, garbage out. Stale docs produce confidently wrong code.
- **The cold start is real.** The first 2-4 weeks require intentional investment from senior engineers.
- **Review bandwidth is the true bottleneck.** If you automate everything except review, you need enough reviewers.

---

*Have a counterpoint or failure case? Open a PR. Honest failures are more valuable than success stories.*
