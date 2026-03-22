"""Database models — one table, dead simple."""

from sqlalchemy import Column, String, Text, DateTime, func, Index
from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


class Document(Base):
    __tablename__ = "documents"

    path = Column(String, primary_key=True)          # e.g. "frontend/components.md"
    partition = Column(String, nullable=False, index=True)  # e.g. "frontend"
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    keywords = Column(String, nullable=False, default="")
    hash = Column(String, nullable=False)             # content hash for change detection
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    # Full-text search index for Postgres (tsvector)
    # SQLite FTS is handled separately via raw SQL
    __table_args__ = (
        Index("ix_documents_partition_path", "partition", "path"),
    )
