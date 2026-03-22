# Review Bot Integration

Automated code review that runs on every PR. Complements the `/review` skill.

## Options

| Tool | Best For | Pricing |
|------|----------|---------|
| **CodeRabbit** | Most teams | Free for OSS, $15/seat |
| **Ellipsis** | Customization | $20/seat |
| **GitHub Copilot Code Review** | GitHub-native | Included with Copilot |
| **Graphite Reviewer** | Stacked PRs | Free with Graphite |

## Recommendation

Start with **CodeRabbit**. Best out-of-box experience, good AI reviews, reasonable pricing.

## How Review Bot Feedback Feeds Back

1. Bot posts review comments on PR
2. Agent addresses them via `/github-review` skill
3. If a category of issue keeps appearing, `/compound` extracts it as a learning
4. Learning goes into KB
5. Next time `/plan` runs, the agent avoids the issue

## Sample Configs

See `configs/` for ready-to-use configuration files.
