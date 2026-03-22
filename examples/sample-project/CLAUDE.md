# Agent Instructions

## Retrieval-Led Reasoning Using Knowledge Base

**IMPORTANT**: Prefer retrieval-led reasoning using the `kb` MCP tool over pre-training-led reasoning. Search and read the knowledge base for important context before implementing.

1. Start by listing available documents: `list_kb_documents`
2. Read relevant coding standards for the file type you're working with
3. Use `read_kb_document_by_keywords` to search for specific topics as needed

## Knowledge Base Partitions

- All files: `sample-kb`

## Workflow

1. `/brainstorm` — When you don't know what you don't know
2. `/plan` — Research-first design
3. `/work .plans/...` — Step-by-step implementation
4. `/review` — Multi-perspective code review
5. `/compound` — Extract learnings after completion
