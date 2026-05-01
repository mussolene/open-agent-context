from __future__ import annotations

from typing import Any

from oacs.core.errors import NotFound
from oacs.storage.sqlite import SQLiteStore


class Repository:
    def __init__(self, store: SQLiteStore, table: str):
        self.store = store
        self.table = table

    def save(self, record: dict[str, Any]) -> dict[str, Any]:
        self.store.put_json(self.table, record)
        return record

    def get(self, record_id: str) -> dict[str, Any]:
        record = self.store.get(self.table, record_id)
        if record is None:
            raise NotFound(f"{self.table} record not found: {record_id}")
        return record

    def list(self, where: str = "", params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
        return self.store.list(self.table, where, params)
