# FAQ

## General

**Q: Does this only work with Claude Code?**
No. The skills are markdown files that work with any coding agent that supports skills/instructions: Claude Code, Cursor, Codex, GitHub Copilot, OpenCode, etc. The MCP server works with any MCP-compatible client.

**Q: Do I need all the components?**
No. Start with skills + KB server. Add hooks, review bot, and observability as you mature.

**Q: What if my team doesn't use stacked PRs?**
The skills work with single PRs too. Stacked PRs are recommended but not required.

## Git Platform Support

**Q: Does this only work with GitHub?**
The architecture is GitHub-first but not GitHub-only. Here's what depends on GitHub and what to change for other platforms:

| Component | GitHub Dependency | GitLab/Bitbucket/ADO Adaptation |
|-----------|------------------|--------------------------------|
| KB Server git sync | Uses `GH_TOKEN` for auth | Change to platform-specific token (e.g. `GITLAB_TOKEN`). The server runs plain `git clone`/`git pull` — any git host works. |
| GitHub Actions (compound-on-merge, kb-sync) | GitHub Actions YAML | Rewrite as GitLab CI, Bitbucket Pipelines, or Azure Pipelines. Same logic, different YAML. |
| `/pr-push` skill | Uses `gh` CLI | Replace with `glab` (GitLab), platform API calls, or generic `git push` + API. |
| `/github-review` skill | Reads GitHub PR comments | Adapt to platform's PR/MR comment API. |
| Review bot (CodeRabbit etc.) | GitHub integration | Most bots support GitLab too. Check your bot's docs. |
| Codespaces | GitHub-specific | Use GitPod (GitLab), or any cloud IDE with devcontainers. |

**The core workflow (brainstorm → plan → work → review → compound) is platform-agnostic.** Only the git hosting integrations need adaptation.

**Q: We use GitLab. How much work to adapt?**
Roughly 1-2 days. The KB server works as-is (just change the token env var). The GitHub Actions need rewriting as `.gitlab-ci.yml`. The PR-related skills need `gh` calls replaced with `glab` calls. Everything else is unchanged.

## Knowledge Base

**Q: What if the KB has wrong information?**
Bad KB docs produce confidently wrong code. That's why all KB additions go through PR review. If you find a bad doc, fix it — the compound loop should surface these.

**Q: How often should we update the KB?**
The compound loop handles this automatically. Manual updates are needed when you introduce new patterns, deprecate old ones, or onboard new technologies.

**Q: Can I use Notion/Confluence instead of a git-backed KB?**
The MCP tool interface is documented — you could build an adapter. But git-backed is recommended because it gives you version history, PR review on changes, and branch-based editing.

## Skills

**Q: How do I customize a skill?**
Skills are markdown files. Edit the SKILL.md to change behavior. Fork a skill to create a variant.

**Q: Can I create my own skills?**
Yes. See the skill format in `skills/README.md`. A skill is a markdown file with a frontmatter header and structured instructions.

## Compound Loop

**Q: What if the compound loop extracts bad learnings?**
The auto-compound GitHub Action creates a PR to the KB repo — it doesn't merge directly. A human reviews before learnings enter the KB.

**Q: How long before the flywheel shows results?**
Usually 2-4 weeks. The first improvements come from seed KB docs. Compound learnings add incremental value over months.

## Security

**Q: Is it safe to give agents production access?**
With the right guardrails: read-replica only, blocked tables, audit trails, mandatory safety doc loading. See the Intercom case study in [guides/12-proof.md](12-proof.md).

**Q: How do I handle secrets?**
Never put secrets in KB docs. Use environment variables for tokens. The `.gitignore` excludes `.env` files.
