# KB Server: Required Capabilities

Any knowledge base server deployed as part of this architecture must support these capabilities.

## Required (C1-C8)

### C1: MCP Transport

The server must expose tools via the Model Context Protocol. Coding agents (Claude Code, Cursor, Codex, Copilot) connect via MCP. This is the standard protocol for agent-tool communication.

### C2: Document Listing

Agents need to discover what's in the KB. The server must provide an index of available documents with titles, paths, and keywords. Supports browsing by partition.

### C3: Retrieval by Path

Agents need to read specific documents by their file path (e.g., `coding-standards/typescript-guidelines.md`). Must support partial path matching (search from right-to-left if exact match fails).

### C4: Keyword / Semantic Search

Agents need to search for relevant documents by topic when they don't know the exact path. Must support either full-text keyword search or vector-based semantic search (or both).

### C5: Partitioning

Knowledge must be segmented so agents working on frontend don't get backend docs polluting their context.

**Implementation: Partitions are top-level folders in the docs repo. Tools accept an optional `partition` parameter.**

On disk:
```
kb-docs/
├── frontend/       → partition "frontend"
├── backend/        → partition "backend"
└── infra/          → partition "infra"
```

- Adding a partition = creating a folder in the docs repo
- Agents pass `partition="frontend"` to scope tool results
- Leave partition empty to search everything
- CLAUDE.md tells the agent which partition to use for the repo

### C6: Git-Backed Content Sync

The content authoring interface is git. The server must sync content from configured git repositories. When a PR merges to main, the server should detect and index new/changed documents.

Sync can be:
- Polling-based (check repo on interval)
- Webhook-based (triggered by GitHub webhook on push)
- Manual (triggered via API call)

### C7: Authentication

The server is deployed remotely. It must support token-based authentication at minimum (bearer tokens). OAuth 2.0 is preferred for multi-user teams.

### C8: Remote Deployment

Must be deployable as a remote HTTP server, not just local stdio. Docker container preferred for portability.

## Nice-to-Have (N1-N5)

### N1: REST API Alongside MCP

Some teams want to integrate via REST API (dashboards, CI scripts, custom tooling) without MCP. OpenAPI documentation is a bonus.

### N2: Admin UI

Web interface for managing repositories, partitions, and documents. Reduces operational burden.

### N3: Vector Embeddings

Semantic search via embeddings (pgvector, FAISS, Chroma, Qdrant) provides better results than keyword-only search.

### N4: Multiple Storage Backends

PostgreSQL for production, SQLite for local development. Reduces onboarding friction.

### N5: Content Filtering

Inclusion/exclusion filters so you can sync a repo but only index files matching specific patterns (e.g., `kb/*.md`), excluding drafts or work-in-progress.

## MCP Tool Interface Specification

Any server implementing this interface is compatible with the architecture's skills and templates.

### `list_kb_documents`

**Parameters:**
- `partition` (optional, string): Filter by partition name

**Returns:** List of documents with `id`, `title`, `path`, `keywords`

### `read_kb_document_by_path`

**Parameters:**
- `path` (required, string): Document file path
- `partition` (optional, string): Partition to search in

**Returns:** Document content as markdown string

### `read_kb_document_by_keywords`

**Parameters:**
- `keywords` (required, string): Space-separated search terms
- `partition` (optional, string): Partition to search in

**Returns:** Top matching document content, plus a summary of related documents

### `list_kb_partitions`

**Parameters:** None

**Returns:** List of partitions with `name`, `description`, `documentCount`
