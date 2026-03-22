---
keywords: testing, unit, integration, e2e, strategy, pyramid
last_reviewed: 2026-03-18
owner: engineering
---

# Testing Strategy

> Example KB seed document. Customize for your team.

## Testing Pyramid

```
         /  E2E  \        Few, slow, high confidence
        / Integration \    Some, medium speed
       /   Unit Tests   \  Many, fast, focused
```

## Unit Tests

- Test pure business logic
- Fast, isolated, no external dependencies
- Mock external boundaries (database, APIs, file system)
- One assertion per test when possible

## Integration Tests

- Test component interactions
- Hit real databases (use test containers or test databases)
- Test API endpoints end-to-end through the HTTP layer
- Don't mock internal services — test the real integration

## When to Write Which

| Scenario | Test Type |
|----------|----------|
| Pure function / calculation | Unit test |
| Database query | Integration test |
| API endpoint | Integration test |
| UI component render | Unit test (with testing-library) |
| Full user flow | E2E test (sparingly) |

## What NOT to Test

- Third-party library internals
- Framework boilerplate (DI registration, etc.)
- Simple getters/setters
- Configuration files
