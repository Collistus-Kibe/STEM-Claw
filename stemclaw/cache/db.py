"""Local SQLite scientific literature cache and research memory."""

import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional
from stemclaw.config import get_settings


class PaperCacheDB:
    """Manages local SQLite cache for retrieved scientific papers and abstracts."""

    def __init__(self, db_path: Optional[Path] = None) -> None:
        if db_path:
            self.db_path = db_path
        else:
            settings = get_settings()
            self.db_path = settings.stemclaw_dir / "cache.db"

        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(str(self.db_path))
        conn.row_factory = sqlite3.Row
        return conn

    def _init_db(self) -> None:
        """Create tables and indexes if they do not exist."""
        with self._get_connection() as conn:
            conn.execute(
                """
                CREATE TABLE IF NOT EXISTS papers (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    paper_id TEXT UNIQUE NOT NULL,
                    title TEXT NOT NULL,
                    authors TEXT,
                    year INTEGER,
                    venue TEXT,
                    abstract TEXT,
                    doi TEXT,
                    url TEXT,
                    pdf_url TEXT,
                    category TEXT,
                    source TEXT,
                    cached_at TEXT
                )
                """
            )
            conn.execute("CREATE INDEX IF NOT EXISTS idx_papers_title ON papers (title)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_papers_doi ON papers (doi)")
            conn.execute("CREATE INDEX IF NOT EXISTS idx_papers_category ON papers (category)")

    def cache_paper(
        self,
        paper_id: str,
        title: str,
        authors: Optional[str] = None,
        year: Optional[int] = None,
        venue: Optional[str] = None,
        abstract: Optional[str] = None,
        doi: Optional[str] = None,
        url: Optional[str] = None,
        pdf_url: Optional[str] = None,
        category: Optional[str] = None,
        source: Optional[str] = None,
    ) -> bool:
        """Insert or replace a paper record in the local cache."""
        clean_id = paper_id.strip()
        if not clean_id or not title:
            return False

        now_iso = datetime.now(timezone.utc).isoformat()
        with self._get_connection() as conn:
            conn.execute(
                """
                INSERT INTO papers (
                    paper_id, title, authors, year, venue, abstract,
                    doi, url, pdf_url, category, source, cached_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ON CONFLICT(paper_id) DO UPDATE SET
                    title = excluded.title,
                    authors = coalesce(excluded.authors, papers.authors),
                    year = coalesce(excluded.year, papers.year),
                    venue = coalesce(excluded.venue, papers.venue),
                    abstract = coalesce(excluded.abstract, papers.abstract),
                    doi = coalesce(excluded.doi, papers.doi),
                    url = coalesce(excluded.url, papers.url),
                    pdf_url = coalesce(excluded.pdf_url, papers.pdf_url),
                    category = coalesce(excluded.category, papers.category),
                    source = coalesce(excluded.source, papers.source),
                    cached_at = excluded.cached_at
                """,
                (
                    clean_id,
                    title.strip(),
                    authors.strip() if authors else None,
                    year,
                    venue.strip() if venue else None,
                    abstract.strip() if abstract else None,
                    doi.strip() if doi else None,
                    url.strip() if url else None,
                    pdf_url.strip() if pdf_url else None,
                    category.strip() if category else None,
                    source.strip() if source else None,
                    now_iso,
                ),
            )
            conn.commit()
            return True

    def search_papers(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search papers in cache by title, abstract, or authors."""
        pattern = f"%{query.strip().lower()}%"
        with self._get_connection() as conn:
            cursor = conn.execute(
                """
                SELECT * FROM papers
                WHERE lower(title) LIKE ?
                   OR lower(abstract) LIKE ?
                   OR lower(authors) LIKE ?
                   OR lower(venue) LIKE ?
                ORDER BY year DESC, id DESC
                LIMIT ?
                """,
                (pattern, pattern, pattern, pattern, limit),
            )
            return [dict(row) for row in cursor.fetchall()]

    def get_paper(self, paper_id_or_doi: str) -> Optional[Dict[str, Any]]:
        """Retrieve a paper by exact ID or DOI."""
        target = paper_id_or_doi.strip()
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM papers WHERE paper_id = ? OR doi = ? LIMIT 1",
                (target, target),
            )
            row = cursor.fetchone()
            return dict(row) if row else None

    def count(self) -> int:
        """Return total number of cached papers."""
        with self._get_connection() as conn:
            cursor = conn.execute("SELECT count(*) FROM papers")
            return cursor.fetchone()[0]

    def list_recent(self, limit: int = 10) -> List[Dict[str, Any]]:
        """List recently cached papers."""
        with self._get_connection() as conn:
            cursor = conn.execute(
                "SELECT * FROM papers ORDER BY id DESC LIMIT ?", (limit,)
            )
            return [dict(row) for row in cursor.fetchall()]

    def clear(self) -> None:
        """Clear all cached papers."""
        with self._get_connection() as conn:
            conn.execute("DELETE FROM papers")
            conn.commit()


_GLOBAL_CACHE_DB: Optional[PaperCacheDB] = None


def get_paper_cache() -> PaperCacheDB:
    """Singleton getter for PaperCacheDB."""
    global _GLOBAL_CACHE_DB
    if _GLOBAL_CACHE_DB is None:
        _GLOBAL_CACHE_DB = PaperCacheDB()
    return _GLOBAL_CACHE_DB

