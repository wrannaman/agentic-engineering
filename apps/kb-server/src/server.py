"""
KB Server — minimal MCP + REST knowledge base.

Architecture: Starlette app with REST routes + MCP SDK app mounted at /mcp.
"""

import logging
import threading
from contextlib import asynccontextmanager
from typing import Optional

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Route, Mount
from mcp.server.fastmcp import FastMCP

from .config import config
from .db import SessionLocal, init_db
from .models import Document
from .sync import sync

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# MCP Server (official SDK)
# ---------------------------------------------------------------------------

mcp = FastMCP(
    "kb-server",
    stateless_http=True,
    json_response=True,
    instructions=(
        "Knowledge base server. Use list_documents to see what's available, "
        "read_document to read a specific doc, search_documents to find docs by keyword. "
        "Pass a partition name to scope results (e.g. 'frontend', 'backend')."
    ),
)


@mcp.tool()
def list_documents(partition: str = "") -> str:
    """List all documents in the knowledge base. Returns titles, paths, and keywords.

    Args:
        partition: Optional partition name to filter by (e.g. 'frontend', 'backend').
                   Leave empty for all partitions. Comma-separated for multiple.
    """
    partitions = _parse_partitions(partition) if partition else None
    docs = _get_docs(partitions)
    if not docs:
        return "No documents found."
    lines = []
    for d in docs:
        kw = f" [{d.keywords}]" if d.keywords else ""
        lines.append(f"- **{d.title}** (`{d.path}`){kw}")
    return "\n".join(lines)


@mcp.tool()
def read_document(path: str, partition: str = "") -> str:
    """Read a document by its file path. Supports partial path matching.

    Args:
        path: Document file path (e.g. 'coding-standards/typescript-guidelines.md').
        partition: Optional partition to scope the search.
    """
    partitions = _parse_partitions(partition) if partition else None
    doc = _read(path, partitions)
    if not doc:
        return "Document not found."
    return doc.content


@mcp.tool()
def search_documents(query: str, partition: str = "") -> str:
    """Search documents by keywords. Returns the most relevant matches.

    Args:
        query: Search query (space-separated keywords).
        partition: Optional partition to scope the search.
    """
    partitions = _parse_partitions(partition) if partition else None
    docs = _search(query, partitions, limit=5)
    if not docs:
        return "No matching documents found."
    lines = []
    for i, d in enumerate(docs):
        if i == 0:
            lines.append(f"## Top match: {d.title}\n\n{d.content}")
        else:
            lines.append(f"- **{d.title}** (`{d.path}`)")
    result = lines[0]
    if len(lines) > 1:
        result += "\n\n---\n\n### Related documents\n\n" + "\n".join(lines[1:])
    return result


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _parse_partitions(partition_str: Optional[str]) -> Optional[list[str]]:
    if not partition_str:
        return None
    partitions = []
    for p in partition_str.split(","):
        p = p.strip().lower()
        if p and all(c.isalnum() or c == "-" for c in p):
            partitions.append(p)
    return partitions if partitions else None


def _get_docs(partitions: Optional[list[str]]):
    db = SessionLocal()
    try:
        from .storage import list_documents as _list
        if not partitions:
            return _list(db)
        docs = []
        for p in partitions:
            docs.extend(_list(db, p))
        return docs
    finally:
        db.close()


def _search(query: str, partitions: Optional[list[str]], limit: int = 5):
    db = SessionLocal()
    try:
        from .storage import search_documents as _search_docs
        if not partitions:
            return _search_docs(db, query, limit=limit)
        docs = []
        for p in partitions:
            docs.extend(_search_docs(db, query, p, limit=limit))
        return docs[:limit]
    finally:
        db.close()


def _read(path: str, partitions: Optional[list[str]]):
    db = SessionLocal()
    try:
        from .storage import get_document as _get
        if partitions and len(partitions) == 1:
            return _get(db, path, partitions[0])
        return _get(db, path)
    finally:
        db.close()


def _doc_to_dict(doc) -> dict:
    return {"path": doc.path, "partition": doc.partition, "title": doc.title, "keywords": doc.keywords}


def _doc_to_full_dict(doc) -> dict:
    return {**_doc_to_dict(doc), "content": doc.content}


def _verify_token(request: Request) -> Optional[JSONResponse]:
    if not config.KB_AUTH_TOKEN:
        return None
    auth = request.headers.get("authorization", "")
    if not auth.startswith("Bearer "):
        return JSONResponse({"error": "Missing token"}, status_code=401)
    if auth[7:] != config.KB_AUTH_TOKEN:
        return JSONResponse({"error": "Invalid token"}, status_code=401)
    return None


# ---------------------------------------------------------------------------
# REST routes
# ---------------------------------------------------------------------------

async def health(request: Request):
    return JSONResponse({"status": "healthy"})


async def api_list_partitions(request: Request):
    err = _verify_token(request)
    if err: return err
    docs = _get_docs(None)
    partitions = {}
    for doc in docs:
        partitions[doc.partition] = partitions.get(doc.partition, 0) + 1
    return JSONResponse([{"name": k, "document_count": v} for k, v in sorted(partitions.items())])


async def api_list_documents(request: Request):
    err = _verify_token(request)
    if err: return err
    partition = request.query_params.get("partition")
    partitions = _parse_partitions(partition)
    docs = _get_docs(partitions)
    return JSONResponse([_doc_to_dict(d) for d in docs])


async def api_get_document(request: Request):
    err = _verify_token(request)
    if err: return err
    path = request.path_params["path"]
    partition = request.query_params.get("partition")
    partitions = _parse_partitions(partition)
    doc = _read(path, partitions)
    if not doc:
        return JSONResponse({"error": "Document not found"}, status_code=404)
    return JSONResponse(_doc_to_full_dict(doc))


async def api_search(request: Request):
    err = _verify_token(request)
    if err: return err
    q = request.query_params.get("q", "")
    partition = request.query_params.get("partition")
    limit = int(request.query_params.get("limit", "5"))
    partitions = _parse_partitions(partition)
    docs = _search(q, partitions, limit)
    return JSONResponse([_doc_to_dict(d) for d in docs])


async def api_sync(request: Request):
    err = _verify_token(request)
    if err: return err
    try:
        sync()
        return JSONResponse({"status": "synced"})
    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# ---------------------------------------------------------------------------
# Sync background thread
# ---------------------------------------------------------------------------

_stop_event = threading.Event()


def _sync_loop():
    while not _stop_event.is_set():
        try:
            sync()
        except Exception as e:
            logger.error(f"Sync error: {e}")
        _stop_event.wait(config.SYNC_INTERVAL_SECONDS)


# ---------------------------------------------------------------------------
# App assembly
# ---------------------------------------------------------------------------

# Get the MCP SDK's ASGI app and extract its /mcp route
_mcp_starlette = mcp.streamable_http_app()
_mcp_route = _mcp_starlette.routes[0]  # Route(path='/mcp', app=StreamableHTTPASGIApp)

# The MCP SDK's lifespan initializes the session manager — we must call it
_mcp_lifespan = _mcp_starlette.router.lifespan_context


@asynccontextmanager
async def lifespan(app):
    # Init our stuff
    init_db()
    sync()
    thread = threading.Thread(target=_sync_loop, daemon=True)
    thread.start()
    # Run MCP SDK's lifespan (initializes session manager)
    async with _mcp_lifespan(app):
        yield
    _stop_event.set()


# Build our app: REST routes + MCP route as peers (not mounted)
app = Starlette(
    lifespan=lifespan,
    routes=[
        Route("/health", health, methods=["GET"]),
        Route("/api/partitions", api_list_partitions, methods=["GET"]),
        Route("/api/documents", api_list_documents, methods=["GET"]),
        Route("/api/documents/{path:path}", api_get_document, methods=["GET"]),
        Route("/api/search", api_search, methods=["GET"]),
        Route("/api/sync", api_sync, methods=["POST"]),
        _mcp_route,  # /mcp — handled by MCP SDK's StreamableHTTPASGIApp
    ],
)


def main():
    logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
    logger.info(f"Starting KB server on {config.HOST}:{config.PORT}")
    logger.info(f"MCP endpoint: http://{config.HOST}:{config.PORT}/mcp")
    logger.info(f"REST API: http://{config.HOST}:{config.PORT}/api/")
    if config.repos:
        for repo in config.repos:
            logger.info(f"Repo: {repo.name} → {repo.path} (branch: {repo.branch})")
        logger.info(f"Sync interval: {config.SYNC_INTERVAL_SECONDS}s")
    else:
        logger.info("No repos configured — running without sync")
    uvicorn.run(app, host=config.HOST, port=config.PORT)


if __name__ == "__main__":
    main()
