"""SQLite persistence for submissions and editor drafts.

Open question 3 (SQLModel vs raw sqlite3) resolved: raw sqlite3. Two small
tables don't justify a SQLAlchemy dependency, and the schema below is the
whole story — nothing hides in a metaclass. Connections are opened per
operation, which makes the store thread-safe without locks.
"""

import json
import os
import sqlite3
from contextlib import contextmanager
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS submissions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    challenge_id TEXT NOT NULL,
    code TEXT NOT NULL,
    verdict TEXT NOT NULL,
    kernel_ms REAL,
    failed_test TEXT,
    compile_stderr TEXT NOT NULL DEFAULT '',
    tests_json TEXT NOT NULL DEFAULT '[]',
    created_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);
CREATE INDEX IF NOT EXISTS idx_submissions_challenge
    ON submissions (challenge_id, id DESC);

CREATE TABLE IF NOT EXISTS drafts (
    challenge_id TEXT PRIMARY KEY,
    code TEXT NOT NULL,
    updated_at TEXT NOT NULL DEFAULT (strftime('%Y-%m-%dT%H:%M:%SZ', 'now'))
);
"""


def default_db_path() -> Path:
    if env := os.environ.get("NOOBGPU_DB"):
        return Path(env)
    data_home = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return data_home / "noobgpu" / "noobgpu.sqlite3"


class Store:
    def __init__(self, path: Path):
        self.path = path

    @contextmanager
    def _conn(self):
        self.path.parent.mkdir(parents=True, exist_ok=True)
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row
        try:
            conn.executescript(SCHEMA)
            yield conn
            conn.commit()
        finally:
            conn.close()

    def add_submission(
        self,
        challenge_id: str,
        code: str,
        verdict: str,
        kernel_ms: float | None,
        failed_test: str | None,
        compile_stderr: str,
        tests: list[dict],
    ) -> int:
        with self._conn() as conn:
            cur = conn.execute(
                "INSERT INTO submissions (challenge_id, code, verdict, kernel_ms,"
                " failed_test, compile_stderr, tests_json) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (challenge_id, code, verdict, kernel_ms, failed_test, compile_stderr,
                 json.dumps(tests)),
            )
            return cur.lastrowid

    def list_submissions(self, challenge_id: str) -> list[dict]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT id, challenge_id, verdict, kernel_ms, failed_test, created_at"
                " FROM submissions WHERE challenge_id = ? ORDER BY id DESC",
                (challenge_id,),
            ).fetchall()
            return [dict(r) for r in rows]

    def get_submission(self, submission_id: int) -> dict | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM submissions WHERE id = ?", (submission_id,)
            ).fetchone()
            if row is None:
                return None
            result = dict(row)
            result["tests"] = json.loads(result.pop("tests_json"))
            return result

    def save_draft(self, challenge_id: str, code: str) -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO drafts (challenge_id, code) VALUES (?, ?)"
                " ON CONFLICT (challenge_id) DO UPDATE SET code = excluded.code,"
                " updated_at = strftime('%Y-%m-%dT%H:%M:%SZ', 'now')",
                (challenge_id, code),
            )

    def get_draft(self, challenge_id: str) -> str | None:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT code FROM drafts WHERE challenge_id = ?", (challenge_id,)
            ).fetchone()
            return row["code"] if row else None
