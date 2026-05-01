from __future__ import annotations

from oacs.core.ids import new_id
from oacs.core.json import hash_json
from oacs.core.time import now_iso
from oacs.storage.repositories import Repository


class AuditService:
    def __init__(self, repo: Repository):
        self.repo = repo

    def record(
        self,
        operation: str,
        actor_id: str | None = None,
        target_id: str | None = None,
        metadata: dict[str, object] | None = None,
    ) -> dict[str, object]:
        previous = self.repo.list(order_by=[("created_at", "desc")], limit=1)
        previous_hash = previous[0]["content_hash"] if previous else None
        event: dict[str, object] = {
            "id": new_id("aud"),
            "operation": operation,
            "actor_id": actor_id,
            "target_id": target_id,
            "metadata": metadata or {},
            "previous_hash": previous_hash,
            "created_at": now_iso(),
            "status": "active",
            "namespace": "default",
            "scope": [],
            "owner_actor_id": actor_id,
        }
        event["content_hash"] = hash_json(event)
        self.repo.save(event)
        return event

    def list(self) -> list[dict[str, object]]:
        return self.repo.list(order_by=[("created_at", "asc")])
