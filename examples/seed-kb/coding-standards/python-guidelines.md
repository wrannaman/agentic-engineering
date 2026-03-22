---
keywords: python, fastapi, pytest, conventions, typing
last_reviewed: 2026-03-18
owner: backend-team
---

# Python Guidelines

> Example KB seed document. Customize for your team.

## Style

- Follow PEP 8
- Use type hints on all function signatures
- Use `ruff` for linting and formatting

## Project Structure

```
src/
├── api/          # FastAPI routers
├── models/       # Pydantic models
├── services/     # Business logic
├── storage/      # Database access
└── utils/        # Shared utilities
```

## Error Handling

- Use custom exception classes that inherit from a base app exception
- FastAPI exception handlers for consistent error responses
- Never catch bare `except:` — always specify the exception type

## Testing

- Use `pytest` with fixtures
- Use `httpx.AsyncClient` for API tests
- Use factories (not fixtures) for test data
- Test the API contract, not internal implementation
