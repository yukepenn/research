"""Citation database + source verifier ledger (COMMON-005, manual 12.4).

A SQLite store of sources that have been OPENED AND VERIFIED against the
original (not a search snippet). The DB records the verification fact and a
content hash; it does not itself browse the web (agents do that and then
register the verified source here). A citation may only be used in a manuscript
if its row has verified=1.
"""
from __future__ import annotations

import sqlite3
from dataclasses import dataclass

from core.util import utc_now_iso

_SCHEMA = """
CREATE TABLE IF NOT EXISTS sources (
    source_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    authors TEXT,
    year TEXT,
    venue_or_status TEXT,
    url TEXT NOT NULL,
    verified INTEGER NOT NULL DEFAULT 0,
    verified_at TEXT,
    content_hash TEXT,
    notes TEXT
);
"""


@dataclass
class Source:
    source_id: str
    title: str
    url: str
    authors: str = ""
    year: str = ""
    venue_or_status: str = ""
    verified: bool = False
    verified_at: str | None = None
    content_hash: str | None = None
    notes: str = ""


class CitationDB:
    def __init__(self, path: str = ":memory:"):
        self.conn = sqlite3.connect(path)
        self.conn.row_factory = sqlite3.Row
        self.conn.executescript(_SCHEMA)

    def add(self, src: Source) -> None:
        self.conn.execute(
            "INSERT OR REPLACE INTO sources VALUES (?,?,?,?,?,?,?,?,?,?)",
            (src.source_id, src.title, src.authors, src.year, src.venue_or_status,
             src.url, int(src.verified), src.verified_at, src.content_hash, src.notes),
        )
        self.conn.commit()

    def mark_verified(self, source_id: str, content_hash: str | None = None) -> None:
        self.conn.execute(
            "UPDATE sources SET verified=1, verified_at=?, content_hash=? WHERE source_id=?",
            (utc_now_iso(), content_hash, source_id),
        )
        self.conn.commit()

    def get(self, source_id: str) -> Source | None:
        row = self.conn.execute("SELECT * FROM sources WHERE source_id=?",
                                (source_id,)).fetchone()
        return self._row(row) if row else None

    def all(self) -> list[Source]:
        return [self._row(r) for r in self.conn.execute("SELECT * FROM sources")]

    def unverified(self) -> list[Source]:
        return [s for s in self.all() if not s.verified]

    def to_bibtex(self) -> str:
        out = []
        for s in self.all():
            if not s.verified:
                continue
            out.append(
                f"@misc{{{s.source_id},\n"
                f"  title={{{s.title}}},\n"
                f"  author={{{s.authors}}},\n"
                f"  year={{{s.year}}},\n"
                f"  howpublished={{\\url{{{s.url}}}}},\n"
                f"  note={{{s.venue_or_status}}}\n}}"
            )
        return "\n\n".join(out)

    @staticmethod
    def _row(row: sqlite3.Row) -> Source:
        return Source(
            source_id=row["source_id"], title=row["title"], url=row["url"],
            authors=row["authors"] or "", year=row["year"] or "",
            venue_or_status=row["venue_or_status"] or "",
            verified=bool(row["verified"]), verified_at=row["verified_at"],
            content_hash=row["content_hash"], notes=row["notes"] or "",
        )
