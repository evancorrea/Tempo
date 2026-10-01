from __future__ import annotations

import json
import sqlite3
from datetime import UTC, datetime
from pathlib import Path
from typing import Any


class Database:
    def __init__(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        self.path = path
        self._initialize()

    def _connect(self) -> sqlite3.Connection:
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def _initialize(self) -> None:
        with self._connect() as db:
            db.executescript(
                """
                CREATE TABLE IF NOT EXISTS papers (
                  id TEXT PRIMARY KEY, filename TEXT NOT NULL, sha256 TEXT NOT NULL,
                  status TEXT NOT NULL, stage TEXT NOT NULL, progress INTEGER NOT NULL,
                  page_count INTEGER, error_code TEXT, error_message TEXT,
                  created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE UNIQUE INDEX IF NOT EXISTS papers_sha256_idx ON papers(sha256);
                CREATE TABLE IF NOT EXISTS artifacts (
                  paper_id TEXT NOT NULL, kind TEXT NOT NULL, payload TEXT NOT NULL,
                  PRIMARY KEY (paper_id, kind),
                  FOREIGN KEY (paper_id) REFERENCES papers(id)
                );
                """
            )

    def create_paper(self, paper_id: str, filename: str, sha256: str) -> dict[str, Any]:
        now = datetime.now(UTC).isoformat()
        with self._connect() as db:
            db.execute(
                "INSERT INTO papers VALUES (?, ?, ?, 'uploaded', 'uploaded', 0, NULL, NULL, NULL, ?, ?)",
                (paper_id, filename, sha256, now, now),
            )
        return self.get_paper(paper_id)

    def get_by_hash(self, sha256: str) -> dict[str, Any] | None:
        with self._connect() as db:
            row = db.execute("SELECT * FROM papers WHERE sha256 = ?", (sha256,)).fetchone()
        return dict(row) if row else None

    def get_paper(self, paper_id: str) -> dict[str, Any] | None:
        with self._connect() as db:
            row = db.execute("SELECT * FROM papers WHERE id = ?", (paper_id,)).fetchone()
        return dict(row) if row else None

    def update_paper(self, paper_id: str, **values: Any) -> None:
        values["updated_at"] = datetime.now(UTC).isoformat()
        fields = ", ".join(f"{key} = ?" for key in values)
        with self._connect() as db:
            db.execute(f"UPDATE papers SET {fields} WHERE id = ?", (*values.values(), paper_id))

    def save_artifact(self, paper_id: str, kind: str, payload: Any) -> None:
        with self._connect() as db:
            db.execute(
                "INSERT INTO artifacts(paper_id, kind, payload) VALUES (?, ?, ?) "
                "ON CONFLICT(paper_id, kind) DO UPDATE SET payload = excluded.payload",
                (paper_id, kind, json.dumps(payload)),
            )

    def get_artifact(self, paper_id: str, kind: str) -> Any | None:
        with self._connect() as db:
            row = db.execute("SELECT payload FROM artifacts WHERE paper_id = ? AND kind = ?", (paper_id, kind)).fetchone()
        return json.loads(row["payload"]) if row else None
