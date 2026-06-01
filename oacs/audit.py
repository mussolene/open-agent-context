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
        previous = self.list()
        previous_hash = previous[-1]["content_hash"] if previous else None
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
        events = self.repo.list(order_by=[("created_at", "asc"), ("id", "asc")])
        return _chain_order(events)

    def verify_chain(self) -> dict[str, object]:
        events = self.list()
        errors: list[dict[str, object]] = []
        previous_hash: str | None = None
        for index, event in enumerate(events):
            expected_hash = _event_hash(event)
            if event.get("content_hash") != expected_hash:
                errors.append(
                    {
                        "index": index,
                        "id": event.get("id"),
                        "error": "content_hash_mismatch",
                    }
                )
            if event.get("previous_hash") != previous_hash:
                errors.append(
                    {
                        "index": index,
                        "id": event.get("id"),
                        "error": "previous_hash_mismatch",
                    }
                )
            previous_hash = str(event.get("content_hash") or "")
        return {"valid": not errors, "events": len(events), "errors": errors}


def _event_hash(event: dict[str, object]) -> str:
    payload = {key: value for key, value in event.items() if key != "content_hash"}
    return hash_json(payload)


def _chain_order(events: list[dict[str, object]]) -> list[dict[str, object]]:
    sorted_events = sorted(events, key=_event_sort_key)
    children: dict[str | None, list[dict[str, object]]] = {}
    for event in sorted_events:
        previous_hash = event.get("previous_hash")
        key = str(previous_hash) if previous_hash else None
        children.setdefault(key, []).append(event)

    ordered: list[dict[str, object]] = []
    seen: set[str] = set()

    def event_key(event: dict[str, object]) -> str:
        return str(event.get("id") or id(event))

    def append_chain(start: dict[str, object]) -> None:
        current: dict[str, object] | None = start
        while current is not None:
            key = event_key(current)
            if key in seen:
                return
            ordered.append(current)
            seen.add(key)

            content_hash = current.get("content_hash")
            if not content_hash:
                return
            next_events = [
                event
                for event in children.get(str(content_hash), [])
                if event_key(event) not in seen
            ]
            current = next_events[0] if next_events else None

    for event in children.get(None, []):
        append_chain(event)

    for event in sorted_events:
        if event_key(event) not in seen:
            append_chain(event)

    return ordered


def _event_sort_key(event: dict[str, object]) -> tuple[str, str]:
    return (str(event.get("created_at") or ""), str(event.get("id") or ""))
