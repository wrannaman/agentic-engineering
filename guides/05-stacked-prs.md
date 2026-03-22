# Stacked PRs

This architecture is opinionated: use stacked PRs as your default workflow.

## Why Stacked PRs

- **Smaller, reviewable units.** A 1500-line PR is hard to review. Three 500-line stacked PRs are not.
- **Faster review cycles.** Reviewers can approve earlier PRs while later ones are still in progress.
- **Clearer dependency chains.** Each PR has a defined scope and builds on the previous one.
- **Better compound signal.** Each PR generates its own review feedback, which the compound loop can extract separately.

## How It Works

```
main ← feat/add-model ← feat/add-api ← feat/add-tests
  PR 1: data model        PR 2: endpoints    PR 3: tests
```

Each branch is based on the previous one. The full stack merges together once all review is complete.

## Stacks Are for Reviewers, Not for CI

**Individual PRs in a stack do NOT need to compile or pass CI independently.** This is a deliberate choice.

The purpose of splitting into a stack is to make it easy for a human to review — "PR 1 is the data model, PR 2 is the API, PR 3 is the tests." Each PR is a logical unit that a reviewer can understand in isolation. That's the value.

What stacked PRs are NOT:
- They are not independently deployable units
- They are not meant to be merged one at a time to production
- They are not required to have passing builds in isolation

**The stack merges as one.** Once all PRs in the stack are reviewed and approved, you merge the full stack (either by merging them in order quickly, or by squash-merging the final branch into main). The complete stack should compile and pass CI. Individual slices don't have to.

If you enforce "every PR in the stack must pass CI independently," you end up with two problems:
1. Engineers waste time adding stubs, mocks, and temporary code to make intermediate slices compile
2. The intermediate slices become harder to review because they're full of scaffolding that gets removed in the next PR

The stack is a review tool, not a deployment tool.

**This also implies a few things about how your org works:**

**No long-running feature branches.** If you're maintaining a branch for weeks, something is wrong. Stacks should be small enough to review and merge within a day or two. If a feature takes a week, it's 2-3 stacks merged across the week, not one branch that lives for 7 days.

**You merge the whole stack, not part of it.** In practice, you almost never merge PR 1 and leave PR 2 hanging. The stack is one logical unit split for reviewability. It goes in together or not at all.

**You're working toward continuous deployment.** Merge to main, push to prod, multiple times a day. Short-lived branches. Small batches. Fast feedback. The stacked PR workflow is designed for this — not for teams that do weekly releases from a release branch.

If your org isn't there yet, stacked PRs are a good forcing function to get there. They make long-lived branches feel obviously wrong.

## Tooling

You have three options. All work. Pick based on your team's preference.

### Option 1: Plain `git` + `gh` CLI (no extra tools)

The agent can create and manage stacked PRs using commands your team already has installed. No dependencies, no learning curve. The `/stack-pr` skill handles the branch creation, PR linking, and rebase-after-merge workflow using plain git.

```bash
git checkout -b feat/add-model
# ... work ...
git push -u origin feat/add-model
gh pr create --base main --head feat/add-model --draft

git checkout -b feat/add-api  # branches from feat/add-model
# ... work ...
gh pr create --base feat/add-model --head feat/add-api --draft
```

**Best for:** Teams that want zero additional tooling. The agent handles all the complexity.

### Option 2: [Charcoal](https://github.com/danerwilliams/charcoal)

An open-source CLI for managing stacked PRs. Handles branch creation, restacking, and submission.

```bash
brew install danerwilliams/tap/charcoal
# or cargo install charcoal

charcoal branch create feat/add-model
# ... work ...
charcoal submit  # creates/updates the stack of PRs
```

**Best for:** Teams that want a dedicated tool with a clean UX. Open source, actively maintained.

### Option 3: [git-town](https://www.git-town.com/)

A git extension for stacked changes with strong multi-branch workflow support.

```bash
brew install git-town

git town hack feat/add-model
# ... work ...
git town propose  # creates PR
```

**Best for:** Teams that want deep git integration and don't mind a slightly steeper learning curve.

### What About Graphite?

Graphite popularized stacked PRs but is a closed-source SaaS product. [Charcoal](https://github.com/danerwilliams/charcoal) and other open-source forks of the Graphite CLI exist if you want that workflow without the vendor dependency. Or just use plain `git` + `gh` — the agent handles it fine.

## In the Skills

The `/plan` skill defines a PR Stack table:

```markdown
## PR Stack

| PR | Branch | Steps | Description |
|----|--------|-------|-------------|
| 1  | feat/add-model | 1-2 | Add User entity and repository |
| 2  | feat/add-api | 3-4 | Add User API endpoints |
| 3  | feat/add-tests | 5-6 | Add integration tests |
```

The `/work` skill handles branch transitions between PRs automatically. The `/stack-pr` skill creates the full stack. The `/rebase-fix` skill handles conflicts when earlier PRs merge.

## Our Recommendation

**Start with plain `git` + `gh`.** It works, the agent handles the complexity, and there's nothing to install. If your team finds they're managing stacks frequently and want a better UX, try Charcoal. The skills adapt to whatever you use.
