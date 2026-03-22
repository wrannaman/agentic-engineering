---
keywords: typescript, react, components, hooks, testing, jest, conventions
last_reviewed: 2026-03-18
owner: frontend-team
---

# TypeScript & React Guidelines

> Example KB seed document. Customize for your team.

## File Organization

- One component per file
- Co-locate tests with source (`Component.test.tsx` next to `Component.tsx`)
- Shared utilities in `src/utils/`, shared types in `src/types/`

## Naming Conventions

- Components: `PascalCase` (`UserProfile.tsx`)
- Hooks: `camelCase` with `use` prefix (`useAuth.ts`)
- Utilities: `camelCase` (`formatDate.ts`)
- Types/Interfaces: `PascalCase` (`UserProfile`, `ApiResponse`)
- Constants: `UPPER_SNAKE_CASE` (`MAX_RETRY_COUNT`)

## Component Patterns

- Prefer function components with hooks over class components
- Extract custom hooks when logic is reused across 2+ components
- Use `React.memo` only when profiling shows a performance issue
- Prefer composition over prop drilling

## Error Handling

- Use error boundaries for component-level errors
- Use try/catch for async operations
- Always show user-facing error states (never silent failures)
- Log errors to your monitoring service

## Testing

- Test behavior, not implementation
- Use `@testing-library/react` for component tests
- Mock external dependencies (API calls, third-party services)
- Don't mock internal utilities — test the real thing
