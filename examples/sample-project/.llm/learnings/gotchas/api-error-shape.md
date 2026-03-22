---
keywords: api, error handling, response shape, validation
source_pr: "#52"
extracted_by: compound
date: 2026-03-16
---

# API errors must use the standard error shape

## What Happened
Agent created a new endpoint that returned `{ message: "Not found" }` on 404. The frontend error handler expects `{ error: { code: "NOT_FOUND", message: "..." } }` and crashed.

## The Fix
Use `AppError.notFound()` from `src/utils/errors.ts` — it produces the correct shape automatically.

## The Pattern
```typescript
// WRONG — raw error response
return res.status(404).json({ message: "User not found" });

// RIGHT — standard error shape via AppError
throw AppError.notFound("User not found");
// Middleware catches this and returns:
// { error: { code: "NOT_FOUND", message: "User not found" } }
```

## Prevention
Added to KB: `backend/error-handling.md` — documents the standard error shape and the `AppError` utility.
