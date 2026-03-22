# Review Bots

Automated code review that runs on every PR. Complements the `/review` skill (agent-side, pre-push) with a CI-side, post-push check.

## Recommended Options

| Tool | Best For | Pricing | Notes |
|------|----------|---------|-------|
| **CodeRabbit** | Most teams | Free for OSS, $15/seat | Best out-of-box experience |
| **Ellipsis** | Teams wanting customization | $20/seat | More configurable rules |
| **GitHub Copilot Code Review** | GitHub-native teams | Included with Copilot | Native integration |
| **Graphite Reviewer** | Stacked PR teams | Free with Graphite | Built for stacks |

## How It Fits

```
/review (skill) → catches design issues pre-push
Review bot      → catches style/convention post-push
Human reviewer  → catches judgment calls
```

Defense in depth. The skill should catch everything, but sometimes it doesn't.

## Setup

See `integrations/review-bot/configs/` for sample configuration files for each tool.
