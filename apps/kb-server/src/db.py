"""Database setup — SQLAlchemy with SQLite or Postgres, one env var."""

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker

from .config import config
from .models import Base

# Swap backend with DATABASE_URL env var:
#   sqlite:///kb.db
#   postgresql://user:pass@host/db
engine = create_engine(config.DATABASE_URL, echo=False)
SessionLocal = sessionmaker(bind=engine)

_is_sqlite = config.DATABASE_URL.startswith("sqlite")


def init_db():
    """Create tables and set up full-text search."""
    Base.metadata.create_all(engine)

    if _is_sqlite:
        # Create FTS5 virtual table for full-text search
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE VIRTUAL TABLE IF NOT EXISTS documents_fts
                USING fts5(path, title, content, keywords, content='documents', content_rowid='rowid')
            """))
            # Triggers to keep FTS in sync
            conn.execute(text("""
                CREATE TRIGGER IF NOT EXISTS documents_ai AFTER INSERT ON documents BEGIN
                    INSERT INTO documents_fts(rowid, path, title, content, keywords)
                    VALUES (new.rowid, new.path, new.title, new.content, new.keywords);
                END
            """))
            conn.execute(text("""
                CREATE TRIGGER IF NOT EXISTS documents_ad AFTER DELETE ON documents BEGIN
                    INSERT INTO documents_fts(documents_fts, rowid, path, title, content, keywords)
                    VALUES('delete', old.rowid, old.path, old.title, old.content, old.keywords);
                END
            """))
            conn.execute(text("""
                CREATE TRIGGER IF NOT EXISTS documents_au AFTER UPDATE ON documents BEGIN
                    INSERT INTO documents_fts(documents_fts, rowid, path, title, content, keywords)
                    VALUES('delete', old.rowid, old.path, old.title, old.content, old.keywords);
                    INSERT INTO documents_fts(rowid, path, title, content, keywords)
                    VALUES (new.rowid, new.path, new.title, new.content, new.keywords);
                END
            """))
            conn.commit()
    else:
        # Postgres: create GIN index for tsvector search
        with engine.connect() as conn:
            conn.execute(text("""
                CREATE INDEX IF NOT EXISTS ix_documents_fts
                ON documents
                USING GIN (to_tsvector('english', coalesce(title,'') || ' ' || coalesce(keywords,'') || ' ' || coalesce(content,'')))
            """))
            conn.commit()


def is_sqlite() -> bool:
    return _is_sqlite
