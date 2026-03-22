# Compound References Index

This is the canonical source for the compound skill family:
- `compound`
- `code-compound`
- `past-pr-compound`

Use progressive disclosure.

## Required Load Order

1. Read [`common.md`](common.md).
2. Read exactly one workflow doc:
   - `/compound` -> [`session-compound.md`](session-compound.md)
   - `/code-compound` -> [`code-compound.md`](code-compound.md)
   - `/past-pr-compound` -> [`past-pr-compound.md`](past-pr-compound.md)
3. Load extra docs only when the workflow requires it.

## Ownership Rule

- Shared policy changes belong in `common.md`.
- Workflow-only changes belong in that workflow doc.
- Skill wrappers (`skills/*/SKILL.md`) should stay thin and only route to these references.
