# Integrations

Off-the-shelf tools and observability configs.

## What Goes Here vs. in Skills

- **Skills** = PROCESS (how you develop code with agents)
- **Integrations** = PRODUCT tools + external services

| Directory | Purpose | Audience |
|-----------|---------|----------|
| `review-bot/` | Automated PR review (CodeRabbit, Ellipsis, etc.) | All teams |
| `process-otel/` | Agent lifecycle telemetry | Platform/engineering leads |
| `langfuse/` | AI feature tracing and judges | Teams building AI features |
| `otel/` | OTEL collector for AI features | Teams building AI features |
| `datadog/` | Production monitoring for AI features | Teams building AI features |

## Process vs. Product

**Process observability** (`process-otel/`): How agents are being used. Skill usage, gap trends, adoption curves. Every team needs this.

**Product observability** (`langfuse/`, `otel/`, `datadog/`): For teams building AI-powered product features. Skip entirely if you don't build AI features.
