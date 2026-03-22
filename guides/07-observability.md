# Observability

Observability serves two distinct purposes in this architecture.

## Process Observability (How Agents Are Used)

**Audience:** Engineering team maintaining the agentic platform.

Instrument the agent lifecycle with OTEL:

| Event | What It Tells You |
|-------|------------------|
| SessionStart / SessionEnd | Who's using agents, how often, how long |
| SkillActivation | Which skills are popular, which are dead |
| PreToolUse / PostToolUse | Which tools succeed, which fail |
| PermissionRequest | What permissions are being asked for |
| CompoundGapDetected | What gaps the session-level compound finds |

**Key dashboards:**
- Skill usage heatmap
- Gap classification trends (are `missing_skill` gaps decreasing?)
- Non-engineer adoption curve
- One-shot success rate over time (the north star)

**Privacy-first:** Never capture raw prompts or messages. Hash usernames. Log events and metadata only.

See `integrations/process-otel/` for collector configs and dashboard templates.

## Product Observability (AI Features You Build)

**Audience:** Teams building AI-powered product features. Skip this section entirely if your team doesn't build AI features.

When building AI features, instrument LLM calls with OTEL and stream to LangFuse:

1. Configure OTEL collector to route AI traces
2. Set up LangFuse (self-hosted or cloud)
3. Add judge evaluators (correctness, hallucination, tone)
4. Build dashboards showing quality metrics over time

See `integrations/langfuse/` and `integrations/otel/` for configs.
