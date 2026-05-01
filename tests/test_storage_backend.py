from __future__ import annotations

from typing import Any

from oacs.core.errors import NotFound
from oacs.storage.backend import StorageBackend
from oacs.storage.migrations import initialize_backend
from oacs.storage.repositories import Repository
from oacs.storage.sqlite import SQLiteStore


class InMemoryBackend:
    def __init__(self) -> None:
        self.tables: dict[str, dict[str, dict[str, Any]]] = {}
        self.initialized = False

    def init(self) -> None:
        self.initialized = True

    def put_json(self, table: str, record: dict[str, Any]) -> None:
        self.tables.setdefault(table, {})[str(record["id"])] = dict(record)

    def get(self, table: str, record_id: str) -> dict[str, Any] | None:
        record = self.tables.setdefault(table, {}).get(record_id)
        return dict(record) if record is not None else None

    def list(
        self, table: str, where: str = "", params: tuple[Any, ...] = ()
    ) -> list[dict[str, Any]]:
        if where or params:
            raise AssertionError(
                "test backend intentionally covers repository-level semantics only"
            )
        return [dict(record) for record in self.tables.setdefault(table, {}).values()]

    def delete(self, table: str, record_id: str) -> None:
        self.tables.setdefault(table, {}).pop(record_id, None)


def test_repository_uses_storage_backend_protocol() -> None:
    backend = InMemoryBackend()
    typed_backend: StorageBackend = backend
    initialize_backend(typed_backend)
    repo = Repository(backend, "records")

    saved = repo.save({"id": "rec_1", "value": {"nested": ["ok"]}})

    assert backend.initialized is True
    assert saved["id"] == "rec_1"
    assert repo.get("rec_1")["value"] == {"nested": ["ok"]}
    assert repo.list() == [{"id": "rec_1", "value": {"nested": ["ok"]}}]

    repo.delete("rec_1")

    try:
        repo.get("rec_1")
    except NotFound:
        pass
    else:
        raise AssertionError("deleted record should not be readable")


def test_sqlite_store_implements_storage_backend_protocol(tmp_path) -> None:
    backend: StorageBackend = SQLiteStore(tmp_path / "oacs.db")
    initialize_backend(backend)
    backend.put_json(
        "task_traces",
        {
            "id": "trace_1",
            "payload": {"nested": ["ok"]},
            "created_at": "2026-05-01T00:00:00Z",
            "updated_at": "2026-05-01T00:00:00Z",
            "status": "active",
            "namespace": "default",
            "scope": ["project"],
            "owner_actor_id": None,
            "content_hash": "hash",
        },
    )

    repo = Repository(backend, "task_traces")

    assert repo.get("trace_1")["payload"] == {"nested": ["ok"]}
    assert repo.list("WHERE status=?", ("active",))[0]["id"] == "trace_1"

    repo.delete("trace_1")
    assert backend.get("task_traces", "trace_1") is None
