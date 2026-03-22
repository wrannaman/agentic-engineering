# KB Server Setup Guide

## Deployment Options

### Option 1: Docker Compose (Recommended for Getting Started)

```bash
cd apps/kb-server
cp .env.example .env
# Edit .env
docker-compose up -d
```

### Option 2: Railway / Fly.io / Render

TODO: Add one-click deploy templates for popular platforms.

### Option 3: Self-Hosted

TODO: Add bare-metal deployment instructions.

## Partitioning Strategy

Create partitions that match your team's knowledge boundaries:

```
frontend-kb   → React, TypeScript, CSS, component patterns
backend-kb    → API design, database, business logic
infra-kb      → CI/CD, deployment, monitoring
learnings-kb  → Compound loop output (auto-populated)
```

## Auth Configuration

### Bearer Token (Simplest)

Set `KB_AUTH_TOKEN` to a strong random string. All MCP clients include this in the `Authorization: Bearer` header.

### OAuth (Multi-User)

TODO: Document OAuth setup for teams that need per-user authentication.

## Git Sync Configuration

### Adding a Repository

```bash
curl -X POST https://your-server/api/partitions \
  -H "Authorization: Bearer $KB_AUTH_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "frontend-kb",
    "repoUrl": "https://github.com/your-org/kb-docs.git",
    "branch": "main",
    "pathFilter": "frontend/**/*.md"
  }'
```

### Webhook Sync

Configure a GitHub webhook on your docs repo:
- URL: `https://your-server/api/sync`
- Events: Push
- Secret: Your `KB_AUTH_TOKEN`

The server will re-index on every push to main.
