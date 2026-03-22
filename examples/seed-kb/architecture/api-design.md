---
keywords: api, rest, endpoints, http, design, conventions
last_reviewed: 2026-03-18
owner: backend-team
---

# API Design Conventions

> Example KB seed document. Customize for your team.

## URL Structure

- Use plural nouns: `/users`, `/orders`
- Nest for relationships: `/users/{id}/orders`
- Use query params for filtering: `/orders?status=pending`

## HTTP Methods

| Method | Usage | Response |
|--------|-------|----------|
| GET | Read | 200 + body |
| POST | Create | 201 + created resource |
| PUT | Full update | 200 + updated resource |
| PATCH | Partial update | 200 + updated resource |
| DELETE | Remove | 204 no content |

## Error Responses

Always return consistent error shapes:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Human-readable description",
    "details": [
      {"field": "email", "message": "Invalid email format"}
    ]
  }
}
```

## Pagination

Use cursor-based pagination for lists:

```
GET /users?cursor=abc123&limit=20
```

Response includes `nextCursor` for the next page.
