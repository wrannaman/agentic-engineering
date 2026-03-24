# Knowledge Base Server

A minimal MCP + REST knowledge base server. ~500 lines of Python. Full-text search on curated markdown docs. No embeddings, no vector DB, no API keys.

**Stack:** FastAPI + official MCP Python SDK, SQLAlchemy (SQLite or Postgres — one env var), git clone + pull for sync.

## Quick Start

```bash
cp .env.example .env
# Edit .env: set REPO_URL to your docs repo, set KB_AUTH_TOKEN
docker-compose up -d

# Verify
curl http://localhost:8080/health
# → {"status": "healthy"}
```

## Partitioning

Partitions = **top-level folders** in your docs repo. Adding a partition = creating a folder.

```
kb-docs/
├── frontend/       → partition "frontend"
│   ├── components.md
│   └── testing.md
└── backend/        → partition "backend"
    ├── api-design.md
    └── database.md
```

Every MCP tool accepts an optional `partition` parameter to scope results. In your agent instructions file (`AGENTS.md`, `CLAUDE.md`, `.cursorrules`, etc.), tell the agent which partition to use:

```markdown
## Knowledge Base

Use the `kb` MCP tools. Always pass partition="frontend" when searching.
```

Or leave partition empty to search everything.

**Partition names:** lowercase, alphanumeric, hyphens only. Folders with weird names get normalized (`My Documents` → `my-documents`).

**Connect your repos:**

```json
// .mcp.json
{
  "mcpServers": {
    "kb": {
      "type": "http",
      "url": "https://kb.company.com/mcp",
      "headers": { "Authorization": "Bearer ${KB_AUTH_TOKEN}" }
    }
  }
}
```

**How Claude Code connects:**
```bash
claude mcp add --transport http kb https://kb.company.com/mcp \
  --header "Authorization: Bearer YOUR_TOKEN"
```

## MCP Tools

All tools accept an optional `partition` parameter (comma-separated for multiple).

| Tool | Args | Description |
|------|------|------------|
| `list_documents` | `partition?` | List all documents (titles, paths, keywords) |
| `read_document` | `path`, `partition?` | Read a document by path (supports partial matching) |
| `search_documents` | `query`, `partition?` | Full-text search by keywords |

## REST API

| Method | Endpoint | Description |
|--------|----------|------------|
| GET | `/health` | Health check |
| GET | `/api/partitions` | List partitions with doc counts |
| GET | `/api/documents?partition=X` | List documents |
| GET | `/api/documents/{path}` | Get document by path |
| GET | `/api/search?q=keywords&partition=X` | Search |
| POST | `/api/sync` | Trigger manual sync |

## Configuration

```bash
# Storage — swap with one line
DATABASE_URL=sqlite:///kb.db                    # local dev (default)
DATABASE_URL=postgresql://kb:kb@host/kb         # production

# Auth
KB_AUTH_TOKEN=your-secret-token                 # leave empty for open access

# Repos — multiple repos, each with its own partitions
# Option 1: name:path pairs (local or remote, comma-separated)
REPOS=frontend:/path/to/frontend-kb,backend:/path/to/backend-kb

# Option 2: JSON for full control
REPOS_JSON=[{"name":"frontend","path":"/path/to/frontend-kb"},{"name":"backend","path":"https://github.com/org/backend-kb.git","branch":"main"}]

# Option 3: single repo (backwards compatible)
REPO_URL=https://github.com/org/kb-docs.git

# GH_TOKEN=ghp_xxx                              # only needed for private GitHub repos (not needed for local paths or public repos)
SYNC_INTERVAL_SECONDS=300                       # pull frequency (5 min default)
```

**Local paths work too.** You don't need a remote git repo. Point at a local directory and the server indexes it directly. Remote URLs are cloned automatically.

## How Sync Works

1. On startup: index all configured repos (clone remote, read local)
2. Every N seconds: re-sync (pull remote repos, re-scan local paths)
3. Frontmatter keywords (`---\nkeywords: react, testing\n---`) extracted for search
4. First `# Heading` becomes the document title
5. Documents deleted from repos are removed from the index
6. Each repo's folder structure creates partitions (e.g., `frontend-kb/coding-standards/` → partition `frontend-kb`)

## Capabilities

| # | Capability | Status |
|---|-----------|--------|
| C1 | MCP transport (Streamable HTTP via official SDK) | Done |
| C2 | Document listing | Done |
| C3 | Retrieval by path (exact + partial match) | Done |
| C4 | Full-text search (FTS5 / tsvector) | Done |
| C5 | Partitions (folder-based, tool parameter) | Done |
| C6 | Git-backed sync (clone + pull on timer) | Done |
| C7 | Bearer token auth | Done |
| C8 | Remote deployment (Docker) | Done |
