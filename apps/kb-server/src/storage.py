"""Document storage — CRUD + full-text search."""

from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from .db import is_sqlite
from .models import Document


def list_documents(db: Session, partition: Optional[str] = None) -> list[Document]:
    """List all documents, optionally filtered by partition."""
    q = db.query(Document)
    if partition:
        q = q.filter(Document.partition == partition)
    return q.order_by(Document.path).all()


def get_document(db: Session, path: str, partition: Optional[str] = None) -> Optional[Document]:
    """Get a document by path. Tries exact match, then suffix match."""
    q = db.query(Document)
    if partition:
        q = q.filter(Document.partition == partition)

    # Exact match
    doc = q.filter(Document.path == path).first()
    if doc:
        return doc

    # Suffix match (e.g. "components.md" matches "frontend/components.md")
    doc = q.filter(Document.path.endswith(f"/{path}")).first()
    if doc:
        return doc

    # Partial match anywhere in path
    return q.filter(Document.path.contains(path)).first()


def search_documents(
    db: Session, query: str, partition: Optional[str] = None, limit: int = 5
) -> list[Document]:
    """Full-text search across documents."""
    if is_sqlite():
        sql = "SELECT path FROM documents_fts WHERE documents_fts MATCH :query LIMIT :limit"
        result = db.execute(text(sql), {"query": query, "limit": limit})
        paths = [row[0] for row in result]
        if not paths:
            return []
        docs = db.query(Document).filter(Document.path.in_(paths))
        if partition:
            docs = docs.filter(Document.partition == partition)
        return docs.all()
    else:
        # Postgres tsvector search
        tsquery = " & ".join(query.split())
        sql = """
            SELECT path FROM documents
            WHERE to_tsvector('english', coalesce(title,'') || ' ' || coalesce(keywords,'') || ' ' || coalesce(content,''))
                  @@ to_tsquery('english', :query)
        """
        params = {"query": tsquery, "limit": limit}
        if partition:
            sql += " AND partition = :partition"
            params["partition"] = partition
        sql += " LIMIT :limit"
        result = db.execute(text(sql), params)
        paths = [row[0] for row in result]
        if not paths:
            return []
        return db.query(Document).filter(Document.path.in_(paths)).all()


def upsert_document(db: Session, doc: Document) -> Document:
    """Insert or update a document."""
    existing = db.query(Document).filter(Document.path == doc.path).first()
    if existing:
        if existing.hash == doc.hash:
            return existing  # no change
        existing.title = doc.title
        existing.content = doc.content
        existing.keywords = doc.keywords
        existing.hash = doc.hash
        existing.partition = doc.partition
        db.commit()
        return existing
    else:
        db.add(doc)
        db.commit()
        return doc


def delete_missing(db: Session, current_paths: set[str]):
    """Delete documents whose paths are no longer in the repo."""
    all_docs = db.query(Document).all()
    for doc in all_docs:
        if doc.path not in current_paths:
            db.delete(doc)
    db.commit()
