# Trust CI

If agents write the code and humans only review it, the thing standing between a merged PR and production is your CI pipeline. That pipeline needs to be bulletproof. Not "runs some tests" bulletproof — "I would bet my company on this passing means the code works" bulletproof.

This is probably the most underinvested area in most engineering orgs right now. When a human writes code, they manually test things, eyeball the UI, click through flows, sanity-check the database. When an agent writes code, none of that happens. The agent pushes, CI runs, a human reviews the diff, and it either ships or it doesn't.

If your CI is weak, agentic engineering amplifies that weakness at scale.

## What Bulletproof CI Actually Means

It means you can push to main and deploy to production with confidence, multiple times a day, without manual QA. This is what Stripe does. It's scary the first time. It becomes normal in a week.

**The minimum:**
- Type checking (catches a huge class of agent mistakes)
- Lint + format (deterministic, not agentic — agents don't need to remember style rules)
- Unit tests (fast, focused, run on every push)
- Integration tests (hit real databases, test real API contracts)
- Build (if it doesn't compile, it doesn't ship)

**What most teams are missing:**
- Visual regression testing (LLM-as-judge on screenshots, or pixel-diff tools)
- Browser-based E2E tests (agents can verify behavior, not just rendering)
- Contract tests (if service A changed the response shape, service B's tests should break)
- Database migration validation (does the migration lock critical tables? Does it work on the production data shape, not just the test fixture?)

## You'll Probably Build 3-5 Custom CI Tools

Off-the-shelf CI gets you 70% of the way. The last 30% is bespoke to your codebase and your failure modes. Expect to build:

### 1. Visual Diff Testing

Agents change CSS, move components, adjust layouts. They can't tell if the result looks right. You need automated visual comparison.

**Options:**
- [Playwright visual comparisons](https://playwright.dev/docs/test-snapshots) — screenshot comparison built into your E2E framework
- [Chromatic](https://www.chromatic.com/) — visual testing for Storybook components
- [Percy](https://percy.io/) — visual review platform
- Roll your own: take screenshots before and after, diff them, flag changes above a threshold

The agent creates a PR. CI takes screenshots of affected pages. A visual diff is posted to the PR as a comment. The human reviewer sees exactly what changed visually, not just in code.

### 2. Browser-Based E2E for Agent Code

Agents should be able to verify their own work by driving a browser. This means your E2E test framework needs to:
- Be runnable in CI (headless)
- Cover the critical user flows (login, checkout, CRUD operations)
- Be fast enough to run on every PR (not a 45-minute suite)

**The pattern:** Agent writes code → agent writes or updates E2E test → CI runs the test → if it passes, the feature works. If it fails, the agent gets the failure output and fixes it (bounded: one retry, then human).

### 3. Database Migration Safety

Agents love to write migrations. Agents do not think about table locks, data volume, or production shapes.

**Build a migration checker that:**
- Estimates lock duration on tables over N rows
- Flags `ALTER TABLE` on high-traffic tables
- Runs the migration against a production-shaped test database (not just an empty one)
- Validates up AND down migrations

### 4. API Contract Testing

If you have multiple services, agents changing one service's response shape can silently break consumers.

**Options:**
- [Pact](https://pact.io/) — consumer-driven contract testing
- OpenAPI schema validation — generate schemas from code, fail CI if they change unexpectedly
- Roll your own: snapshot the API response shape, diff on every PR

### 5. Security Scanning

At agent scale, security can't be "the human reviewer remembers to check for injection."

- SAST (static analysis) on every PR — [Semgrep](https://semgrep.dev/), [CodeQL](https://codeql.github.com/)
- Dependency vulnerability scanning — `npm audit`, Dependabot, Snyk
- Secrets detection — [gitleaks](https://github.com/gitleaks/gitleaks), [trufflehog](https://github.com/trufflesecurity/trufflehog)

## The Mental Model

```
Agent writes code
    ↓
Type check (does it compile?)
    ↓
Lint + format (does it follow conventions?)
    ↓
Unit tests (does the logic work?)
    ↓
Integration tests (do the pieces fit together?)
    ↓
Visual regression (does it look right?)
    ↓
E2E tests (does the user flow work?)
    ↓
Migration check (is the migration safe?)
    ↓
Contract check (did the API shape change?)
    ↓
Security scan (is it safe?)
    ↓
Human reviews the diff + visual diff + test results
    ↓
Merge → Deploy
```

Every step except the human review is automated. The human doesn't need to run anything locally, click through anything manually, or eyeball the UI. CI did all of that. The human's job is judgment: "Is this the right approach? Does this make sense for the business? Is there context the CI can't know?"

## The Investment

Building bulletproof CI is a 2-4 week investment for most teams. It pays for itself immediately in agentic workflows because:

1. **Agents produce more PRs.** Manual QA doesn't scale. Automated CI does.
2. **Agents make different mistakes than humans.** They don't typo variable names — they misunderstand business logic. Your CI needs to catch business logic failures, not just syntax.
3. **Trust enables speed.** If you trust CI, you can merge and deploy multiple times a day. If you don't trust CI, every PR requires manual testing, which is the bottleneck you're trying to eliminate.

If you're going to do agentic engineering, invest in CI first. Everything else — the KB, the skills, the compound loop — assumes CI catches what the agent gets wrong. If CI doesn't catch it, the human reviewer is the last line of defense, and humans miss things in code review. Especially at volume.

## Stripe's Model

Stripe merges 1,300+ agent PRs per week. They don't manually test each one. Their CI is the safety net:

- Deterministic steps (linting, type checking, formatting) run without agent involvement
- One CI loop with autofixes
- One additional iteration if tests fail
- Then human review

The agent + CI + human review = the quality bar. No single layer is sufficient. All three together are.
