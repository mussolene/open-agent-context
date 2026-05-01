from __future__ import annotations

from typing import Any, Protocol


class StorageBackend(Protocol):
    """Minimal record-store contract used by the OACS reference implementation."""

    def init(self) -> None:
        """Prepare storage for use."""

    def put_json(self, table: str, record: dict[str, Any]) -> None:
        """Create or replace a JSON-compatible record by id."""

    def get(self, table: str, record_id: str) -> dict[str, Any] | None:
        """Return one record by id, or None when absent."""

    def list(
        self, table: str, where: str = "", params: tuple[Any, ...] = ()
    ) -> list[dict[str, Any]]:
        """Return records from a table.

        SQLite remains the reference backend, so the optional where/params surface
        intentionally preserves the current SQL-fragment compatibility path.
        """

    def delete(self, table: str, record_id: str) -> None:
        """Delete a record by id if it exists."""
