---
keywords: react-query, staleTime, data fetching, performance
source_pr: "#47"
extracted_by: compound
date: 2026-03-15
---

# React Query staleTime defaults to 0

## What Happened
Agent created a new page with `useQuery`. Every navigation back to the page triggered a full refetch, causing a loading spinner flash.

## The Fix
Set `staleTime: 60_000` (60 seconds) for non-critical data. The project default should be set in the QueryClient config, not per-query.

## The Pattern
```typescript
// In src/lib/query-client.ts
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60_000, // 60 seconds — prevents refetch on every navigation
    },
  },
});
```

## Why This Matters
React Query's default `staleTime` is 0, meaning data is considered stale immediately. This is correct for real-time data but wrong for most CRUD pages. The agent didn't know our project-wide default because it wasn't documented.

## Prevention
Added to KB: `frontend/data-fetching.md` — documents the project's QueryClient defaults.
