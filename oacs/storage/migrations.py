from __future__ import annotations

from oacs.storage.sqlite import SQLiteStore


def initialize_database(db_path: str) -> None:
    SQLiteStore(db_path).init()
