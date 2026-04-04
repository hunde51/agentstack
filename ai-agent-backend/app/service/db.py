"""SQLite persistence for demo users (replaces hardcoded lists)."""

import os
import sqlite3
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()

_DEFAULT_DB = Path(__file__).resolve().parent.parent / "data" / "app.db"
SQLITE_PATH = os.getenv("SQLITE_PATH", str(_DEFAULT_DB))


def _connect() -> sqlite3.Connection:
    Path(SQLITE_PATH).parent.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(SQLITE_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    conn = _connect()
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL
            )
            """
        )
        cur = conn.execute("SELECT COUNT(*) AS c FROM users")
        if cur.fetchone()[0] == 0:
            conn.executemany(
                "INSERT INTO users (name) VALUES (?)",
                [("Alice",), ("Bob",), ("Charlie",), ("Dana",)],
            )
        conn.commit()
    finally:
        conn.close()


def get_all_users() -> list[dict[str, Any]]:
    conn = _connect()
    try:
        cur = conn.execute("SELECT id, name FROM users ORDER BY id")
        return [{"id": row["id"], "name": row["name"]} for row in cur.fetchall()]
    finally:
        conn.close()
