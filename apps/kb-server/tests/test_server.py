"""
Test harness for the KB server.

Three test tiers:
1. Unit tests: parsing, storage, sync — no server needed
2. REST API tests: lightweight Starlette app with REST routes only
3. MCP integration: tested via MCP Inspector or live server (see README)
"""

import hashlib
import os
import tempfile
from pathlib import Path

import pytest
from starlette.testclient import TestClient
from starlette.applications import Starlette
from starlette.routing import Route

# Configure BEFORE importing app modules
os.environ["DATABASE_URL"] = "sqlite:///test_kb.db"
os.environ["KB_AUTH_TOKEN"] = "test-token-123"
os.environ["REPO_URL"] = ""
os.environ["SYNC_INTERVAL_SECONDS"] = "999999"

from src.db import init_db, engine, SessionLocal
from src.models import Base, Document
from src.storage import list_documents, get_document, search_documents, upsert_document
from src.sync import _parse_frontmatter, _extract_title, _normalize_partition
from src.server import (
    health, api_list_partitions, api_list_documents,
    api_get_document, api_search, api_sync,
)


@pytest.fixture(autouse=True)
def fresh_db():
    """Create fresh tables for each test."""
    Base.metadata.drop_all(engine)
    init_db()
    yield
    Base.metadata.drop_all(engine)


@pytest.fixture
def db():
    session = SessionLocal()
    yield session
    session.close()


@pytest.fixture
def client():
    """Lightweight REST-only test app (no MCP SDK, no lifespan issues)."""
    test_app = Starlette(routes=[
        Route("/health", health, methods=["GET"]),
        Route("/api/partitions", api_list_partitions, methods=["GET"]),
        Route("/api/documents", api_list_documents, methods=["GET"]),
        Route("/api/documents/{path:path}", api_get_document, methods=["GET"]),
        Route("/api/search", api_search, methods=["GET"]),
        Route("/api/sync", api_sync, methods=["POST"]),
    ])
    return TestClient(test_app, raise_server_exceptions=False)


@pytest.fixture
def auth_headers():
    return {"Authorization": "Bearer test-token-123"}


# ---------------------------------------------------------------------------
# Unit tests: parsing helpers
# ---------------------------------------------------------------------------

class TestParsing:
    def test_extract_title(self):
        assert _extract_title("# Hello World\nSome content") == "Hello World"
        assert _extract_title("No heading here") == ""
        assert _extract_title("## Not H1\n# Actual Title") == "Actual Title"

    def test_parse_frontmatter(self):
        content = "---\nkeywords: react, testing\n---\n# Title\nBody"
        keywords, clean = _parse_frontmatter(content)
        assert keywords == "react, testing"
        assert clean.startswith("# Title")

    def test_parse_frontmatter_no_frontmatter(self):
        content = "# Just a doc\nNo frontmatter here"
        keywords, clean = _parse_frontmatter(content)
        assert keywords == ""
        assert clean == content

    def test_parse_frontmatter_with_extra_fields(self):
        content = "---\nkeywords: react\nlast_reviewed: 2026-03-01\nowner: team\n---\n# Doc"
        keywords, clean = _parse_frontmatter(content)
        assert keywords == "react"

    def test_normalize_partition(self):
        assert _normalize_partition("frontend") == "frontend"
        assert _normalize_partition("My Documents") == "my-documents"
        assert _normalize_partition("Backend API") == "backend-api"
        assert _normalize_partition("frontend/v2") == "frontend-v2"
        assert _normalize_partition("  UPPER  ") == "upper"


# ---------------------------------------------------------------------------
# Storage tests
# ---------------------------------------------------------------------------

class TestStorage:
    def _make_doc(self, path="frontend/components.md", partition="frontend",
                  title="Components", content="# Components\nSome content",
                  keywords="react, components"):
        return Document(
            path=path, partition=partition, title=title,
            content=content, keywords=keywords,
            hash=hashlib.sha256(content.encode()).hexdigest()[:16],
        )

    def test_upsert_and_list(self, db):
        doc = self._make_doc()
        upsert_document(db, doc)
        docs = list_documents(db)
        assert len(docs) == 1
        assert docs[0].title == "Components"

    def test_list_by_partition(self, db):
        upsert_document(db, self._make_doc("frontend/a.md", "frontend", "A", "# A"))
        upsert_document(db, self._make_doc("backend/b.md", "backend", "B", "# B"))
        assert len(list_documents(db, "frontend")) == 1
        assert len(list_documents(db, "backend")) == 1
        assert len(list_documents(db)) == 2

    def test_get_by_exact_path(self, db):
        upsert_document(db, self._make_doc())
        doc = get_document(db, "frontend/components.md")
        assert doc is not None
        assert doc.title == "Components"

    def test_get_by_partial_path(self, db):
        upsert_document(db, self._make_doc())
        doc = get_document(db, "components.md")
        assert doc is not None

    def test_get_nonexistent(self, db):
        assert get_document(db, "nope.md") is None

    def test_upsert_no_change(self, db):
        upsert_document(db, self._make_doc())
        upsert_document(db, self._make_doc())
        assert len(list_documents(db)) == 1

    def test_upsert_with_change(self, db):
        upsert_document(db, self._make_doc(content="# V1"))
        upsert_document(db, self._make_doc(content="# V2"))
        docs = list_documents(db)
        assert len(docs) == 1
        assert "V2" in docs[0].content

    def test_search(self, db):
        upsert_document(db, self._make_doc(
            "frontend/testing.md", "frontend", "Testing",
            "# Testing\nUse jest for unit tests", "jest, testing"
        ))
        upsert_document(db, self._make_doc(
            "backend/api.md", "backend", "API Design",
            "# API Design\nREST conventions", "api, rest"
        ))
        results = search_documents(db, "testing jest")
        assert len(results) >= 1
        assert any("Testing" in r.title for r in results)

    def test_search_with_partition(self, db):
        upsert_document(db, self._make_doc(
            "frontend/testing.md", "frontend", "FE Testing", "# FE Testing", "testing"
        ))
        upsert_document(db, self._make_doc(
            "backend/testing.md", "backend", "BE Testing", "# BE Testing", "testing"
        ))
        results = search_documents(db, "testing", partition="frontend")
        assert all(r.partition == "frontend" for r in results)


# ---------------------------------------------------------------------------
# REST API tests
# ---------------------------------------------------------------------------

def _seed_docs():
    """Seed test documents directly via DB."""
    db = SessionLocal()
    for path, partition, title, content, kw in [
        ("frontend/components.md", "frontend", "Components", "# Components\nReact patterns", "react"),
        ("frontend/testing.md", "frontend", "Testing", "# Testing\nJest patterns", "jest, testing"),
        ("backend/api.md", "backend", "API Design", "# API Design\nREST", "api, rest"),
    ]:
        db.add(Document(
            path=path, partition=partition, title=title,
            content=content, keywords=kw,
            hash=hashlib.sha256(content.encode()).hexdigest()[:16],
        ))
    db.commit()
    db.close()


class TestRestAPI:
    def test_health(self, client):
        r = client.get("/health")
        assert r.status_code == 200
        assert r.json()["status"] == "healthy"

    def test_auth_required(self, client):
        r = client.get("/api/documents")
        assert r.status_code == 401

    def test_auth_bad_token(self, client):
        r = client.get("/api/documents", headers={"Authorization": "Bearer wrong"})
        assert r.status_code == 401

    def test_list_documents(self, client, auth_headers):
        _seed_docs()
        r = client.get("/api/documents", headers=auth_headers)
        assert r.status_code == 200
        assert len(r.json()) == 3

    def test_list_documents_by_partition(self, client, auth_headers):
        _seed_docs()
        r = client.get("/api/documents?partition=frontend", headers=auth_headers)
        assert r.status_code == 200
        docs = r.json()
        assert len(docs) == 2
        assert all(d["partition"] == "frontend" for d in docs)

    def test_get_document(self, client, auth_headers):
        _seed_docs()
        r = client.get("/api/documents/frontend/components.md", headers=auth_headers)
        assert r.status_code == 200
        doc = r.json()
        assert doc["title"] == "Components"
        assert "content" in doc

    def test_get_document_not_found(self, client, auth_headers):
        r = client.get("/api/documents/nope.md", headers=auth_headers)
        assert r.status_code == 404

    def test_search(self, client, auth_headers):
        _seed_docs()
        r = client.get("/api/search?q=testing", headers=auth_headers)
        assert r.status_code == 200
        assert len(r.json()) >= 1

    def test_search_by_partition(self, client, auth_headers):
        _seed_docs()
        r = client.get("/api/search?q=testing&partition=frontend", headers=auth_headers)
        assert r.status_code == 200
        results = r.json()
        assert all(d["partition"] == "frontend" for d in results)

    def test_list_partitions(self, client, auth_headers):
        _seed_docs()
        r = client.get("/api/partitions", headers=auth_headers)
        assert r.status_code == 200
        names = [p["name"] for p in r.json()]
        assert "frontend" in names
        assert "backend" in names


# ---------------------------------------------------------------------------
# Git sync tests (local filesystem, no actual git)
# ---------------------------------------------------------------------------

class TestSync:
    def test_index_local_docs(self):
        """Test indexing from a local directory configured as a repo."""
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / "frontend").mkdir()
            (Path(tmpdir) / "backend").mkdir()
            (Path(tmpdir) / "frontend" / "components.md").write_text(
                "---\nkeywords: react, components\n---\n# React Components\nUse function components."
            )
            (Path(tmpdir) / "frontend" / "testing.md").write_text(
                "---\nkeywords: jest, testing\nlast_reviewed: 2026-03-01\n---\n# Testing\nUse RTL."
            )
            (Path(tmpdir) / "backend" / "api.md").write_text("# API Conventions\nUse REST.")
            (Path(tmpdir) / ".git").mkdir()
            (Path(tmpdir) / ".git" / "config").write_text("gitconfig")

            # Use the multi-repo _index_path function directly
            from src.sync import _index_path
            paths = _index_path("test-kb", tmpdir)

            assert len(paths) == 3

            db = SessionLocal()
            docs = list_documents(db)
            db.close()

            assert len(docs) == 3
            # Partitions should be prefixed with repo name
            partitions = {d.partition for d in docs}
            assert any("frontend" in p for p in partitions)
            assert any("backend" in p for p in partitions)

            # Verify frontmatter parsed
            db = SessionLocal()
            doc = get_document(db, "components.md")
            db.close()
            assert doc is not None
            assert "react" in doc.keywords

    def test_hidden_dirs_skipped(self):
        with tempfile.TemporaryDirectory() as tmpdir:
            (Path(tmpdir) / ".hidden").mkdir()
            (Path(tmpdir) / ".hidden" / "secret.md").write_text("# Secret")
            (Path(tmpdir) / "public").mkdir()
            (Path(tmpdir) / "public" / "doc.md").write_text("# Public Doc")

            from src.sync import _index_path
            paths = _index_path("test-kb", tmpdir)

            assert len(paths) == 1

            db = SessionLocal()
            docs = list_documents(db)
            db.close()

            assert len(docs) == 1
            assert docs[0].title == "Public Doc"

    def test_multi_repo_indexing(self):
        """Test indexing from two repos with different partitions."""
        with tempfile.TemporaryDirectory() as dir1, tempfile.TemporaryDirectory() as dir2:
            # Repo 1: frontend KB
            (Path(dir1) / "kb").mkdir()
            (Path(dir1) / "kb" / "components.md").write_text("# Components\nReact stuff")
            (Path(dir1) / "kb" / "testing.md").write_text("# Testing\nJest stuff")

            # Repo 2: backend KB
            (Path(dir2) / "kb").mkdir()
            (Path(dir2) / "kb" / "api.md").write_text("# API Design\nREST stuff")

            from src.sync import _index_path
            paths1 = _index_path("frontend", dir1)
            paths2 = _index_path("backend", dir2)

            assert len(paths1) == 2
            assert len(paths2) == 1

            db = SessionLocal()
            all_docs = list_documents(db)
            db.close()

            assert len(all_docs) == 3

            # Partitions should be distinct
            partitions = {d.partition for d in all_docs}
            assert len(partitions) >= 2  # at least frontend-kb and backend-kb
