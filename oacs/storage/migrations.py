from __future__ import annotations

from oacs.storage.backend import StorageBackend
from oacs.storage.sqlite import SQLiteStore


def initialize_database(db_path: str) -> None:
    SQLiteStore(db_path).init()


def initialize_backend(store: StorageBackend) -> None:
    store.init()
