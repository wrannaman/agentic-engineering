---
keywords: api, endpoint, validation, zod, express, pattern
source_pr: "#52"
extracted_by: compound
date: 2026-03-16
---

# API Endpoint with Validation

## When to Use
Any new API endpoint that accepts a request body.

## Template
See `api-endpoint-with-validation.template` in this directory.

## Conventions
- Always validate request body with Zod before processing
- Always use `AppError` for error responses (never raw `res.status().json()`)
- Always include the auth middleware
- Response shape: `{ data: T }` for success, `{ error: { code, message } }` for errors
