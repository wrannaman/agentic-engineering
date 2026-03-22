# Sources & Prior Art

This architecture draws from publicly documented best practices, research, and case studies. Every core pattern has prior art in the public domain.

## Core Workflow: Brainstorm → Plan → Implement → Review → Compound

The structured phase-based workflow is documented across multiple independent sources:

- **Tyler Burleigh (Feb 2026)** — ["Research, Plan, Implement, Review: My Agentic Engineering Workflow"](https://tylerburleigh.com/blog/2026/02/22/) describes a four-stage cycle with fresh sessions at each phase transition, markdown artifacts as persistent truth, and AI self-review before human evaluation. The key insight: "the bottleneck in AI-assisted development isn't code generation, it's ensuring the model understands what to build before it starts building."

- **Addy Osmani (O'Reilly, 2025)** — ["How to Write a Good Spec for AI Agents"](https://addyosmani.com/blog/good-spec/) recommends a four-phase gated workflow: Specify → Plan → Tasks → Implement, with validation checkpoints at each stage. Based on analysis of 2,500+ agent configuration files.

- **Dr. Randal Olson (Nov 2025)** — ["The Three Phases of AI-Assisted Coding"](https://www.randalolson.com/2025/11/24/three-phases-ai-assisted-coding/) documents Research → Planning → Execution as the gold standard for AI coding workflows.

- **Every.to (2026)** — ["Compound Engineering"](https://every.to/guides/compound-engineering) describes the pattern of extracting learnings from completed work and feeding them back into future sessions.

## Research Before Asking (Plan Skill)

The principle that agents should research the codebase before asking the user questions:

- **Anthropic (Sep 2025)** — ["Effective Context Engineering for AI Agents"](https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents) — "Find the smallest set of high-signal tokens that maximize the likelihood of your desired outcome" through just-in-time exploration.

- **Anthropic (Nov 2025)** — ["Effective Harnesses for Long-Running Agents"](https://www.anthropic.com/engineering/effective-harnesses-for-long-running-agents) — Agents should explore their environment and retrieve information just-in-time rather than loading everything upfront.

- **Ken Muse (2026)** — ["Why Focused AI Agents Get Better Coding Results"](https://www.kenmuse.com/blog/why-focused-ai-agents-get-better-coding-results/) — Smaller, focused contexts produce better outcomes than monolithic prompts.

## Multi-Perspective Parallel Review (Review Skill)

The pattern of launching multiple sub-agents in parallel, each reviewing from a different perspective:

- **HAMY Labs (Feb 2026)** — ["9 Parallel AI Agents That Review My Code"](https://hamy.xyz/blog/2026-02_code-reviews-claude-subagents) — Documents a 9-agent parallel review system with perspectives including security, performance, code quality, test quality, dependency safety, and simplification. Results aggregated by severity.

- **Anthropic (Mar 2026)** — Launched a [multi-agent code review tool](https://techcrunch.com/2026/03/09/anthropic-launches-code-review-tool-to-check-flood-of-ai-generated-code/) for Claude Code.

- **HubSpot (Mar 2026)** — ["Sidekick: Multi-Model AI Code Review"](https://www.infoq.com/news/2026/03/hubspot-ai-code-review-agent/) — Reduced time-to-first-feedback by 90% with multi-agent review.

- **RKoots (Mar 2026)** — ["Scaling Code Review: Multi-Agent Systems"](https://rkoots.github.io/blog/2026/03/09/bringing-code-review-to-claude-code/) — Enterprise-scale multi-agent review with specialized perspectives.

## Simple Search Beats RAG (KB Architecture)

The decision to use full-text keyword search instead of vector embeddings:

- **Vercel (2026)** — ["AGENTS.md Outperforms Skills in Our Agent Evals"](https://vercel.com/blog/agents-md-outperforms-skills-in-our-agent-evals) — Compressed 8KB index achieved 100% pass rate. Skills-based RAG retrieval achieved 53-79%. "With AGENTS.md, there's no moment where the agent must decide 'should I look this up?'"

- **HumanLayer (2026)** — ["Writing a Good CLAUDE.md"](https://www.humanlayer.dev/blog/writing-a-good-claude-md) — Less than 300 lines, pointers not copies, progressive disclosure. "Never send an LLM to do a linter's job."

## Deterministic + Agentic (Pipeline Architecture)

The principle that agents handle creative work while deterministic tooling handles validation:

- **Stripe (2026)** — ["Minions: One-Shot End-to-End Coding Agents"](https://stripe.dev/blog/minions-stripes-one-shot-end-to-end-coding-agents-part-2) — "Blueprints" interleave agentic nodes with deterministic code nodes. Linters, test suites, CI, and formatters run without agent involvement. "Agents plus code beats either alone."

## Compound Learning Loop

The pattern of extracting learnings from completed work and feeding them into future sessions:

- **Intercom (Mar 2026)** — [Brian Scanlan's thread](http://x.com/brian_scanlan/status/2033978300003987527?s=20) — Session-level compound loop: auto-classifies gaps (`missing_skill`, `missing_tool`, `repeated_failure`, `wrong_info`), posts to Slack with pre-filled GitHub issue URLs.

- **Every.to (2026)** — ["Compound Engineering"](https://every.to/guides/compound-engineering) — Documents the broader pattern of knowledge accumulation across coding sessions.

## Non-Engineers as Power Users

The observation that non-engineers adopt and benefit from agent tooling:

- **Intercom (Mar 2026)** — Top 5 users of their production console were design managers, customer support engineers, and product management leaders — not engineers.

- **Zapier (2026)** — 89% AI adoption across entire org, not just engineering.

## Bounded Iteration

The principle that agents get limited retries before asking humans:

- **Stripe (2026)** — One CI loop with autofixes, then one additional iteration if tests fail, then human review. Not infinite retries.

## Security at Agent Scale

The observation that high-volume agent output requires structural security:

- **NxCode (2026)** — ["Agentic Engineering: The Complete Guide"](https://www.nxcode.io/resources/news/agentic-engineering-complete-guide-vibe-coding-ai-agents-2026) — "Agent-scale development requires agent-scale security." 1,000 PRs/week with 1% vulnerability rate = 10 new vulnerabilities weekly.

## Industry Data

- **LangChain (2026)** — [State of AI Agents](https://www.langchain.com/state-of-agent-engineering) — 57% of organizations have agents in production
- **Jellyfish (2026)** — [Benchmark Study](https://jellyfish.co/blog/2025-ai-metrics-in-review/) — 64% of companies generate a majority of their code with AI assistance
- **Gartner (2026)** — CIO Agenda: 64% of CIOs plan to deploy agentic AI within 24 months
- **Anthropic (2026)** — [Eight Trends](https://claude.com/blog/eight-trends-defining-how-software-gets-built-in-2026) — Developers can fully delegate only 0-20% of tasks
