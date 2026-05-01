from __future__ import annotations

from typing import Any, Literal, Protocol

SortDirection = Literal["asc", "desc"]
OrderBy = tuple[str, SortDirection]


class StorageBackend(Protocol):
    """Minimal record-store contract used by the OACS reference implementation."""

    def init(self) -> None:
        """Prepare storage for use."""

    def put_json(self, table: str, record: dict[str, Any]) -> None:
        """Create or replace a JSON-compatible record by id."""

    def get(self, table: str, record_id: str) -> dict[str, Any] | None:
        """Return one record by id, or None when absent."""

    def list(
        self,
        table: str,
        filters: dict[str, Any] | None = None,
        order_by: list[OrderBy] | None = None,
        limit: int | None = None,
    ) -> list[dict[str, Any]]:
        """Return records from a table through backend-neutral selectors."""

    def delete(self, table: str, record_id: str) -> None:
        """Delete a record by id if it exists."""
